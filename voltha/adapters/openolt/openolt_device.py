#
# Copyright 2018 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import structlog
import threading
import grpc
import collections
import time

from twisted.internet import reactor

from voltha.protos.device_pb2 import Port, Device
from voltha.protos.common_pb2 import OperStatus, AdminState, ConnectStatus
from voltha.protos.logical_device_pb2 import LogicalDevice
from voltha.protos.openflow_13_pb2 import OFPPS_LIVE, OFPPF_FIBER, OFPPS_LINK_DOWN, \
    OFPPF_1GB_FD, OFPC_GROUP_STATS, OFPC_PORT_STATS, OFPC_TABLE_STATS, \
    OFPC_FLOW_STATS, ofp_switch_features, ofp_desc, ofp_port, \
    OFPXMC_OPENFLOW_BASIC
from voltha.protos.logical_device_pb2 import LogicalPort, LogicalDevice
from voltha.core.logical_device_agent import mac_str_to_tuple
from voltha.registry import registry
from voltha.adapters.openolt.protos import openolt_pb2_grpc, openolt_pb2
from voltha.protos.bbf_fiber_tcont_body_pb2 import TcontsConfigData
import voltha.core.flow_decomposer as fd

ASFVOLT_HSIA_ID = 13 # FIXME
ASFVOLT_DHCP_TAGGED_ID = 5 # FIXME

Onu = collections.namedtuple("Onu", ["intf_id", "onu_id"])

"""
OpenoltDevice represents an OLT.
"""
class OpenoltDevice(object):

    def __init__(self, **kwargs):
        super(OpenoltDevice, self).__init__()

        self.adapter_agent = kwargs['adapter_agent']
        device = kwargs['device']
        self.device_id = device.id
        self.host_and_port = device.host_and_port
        self.log = structlog.get_logger(id=self.device_id, ip=self.host_and_port)
        self.oper_state = 'unknown'
        self.nni_oper_state = dict() #intf_id -> oper_state
        self.onus = {} # Onu -> serial_number
        self.uni_port_num = 20 # FIXME

        # Create logical device
        ld = LogicalDevice(
            desc=ofp_desc(
                mfr_desc='FIXME', hw_desc='FIXME',
                sw_desc='FIXME', serial_num='FIXME',
                dp_desc='n/a'),
            switch_features=ofp_switch_features(
                n_buffers=256, n_tables=2,
                capabilities=(
                    OFPC_FLOW_STATS | OFPC_TABLE_STATS |
                    OFPC_GROUP_STATS | OFPC_PORT_STATS)),
            root_device_id=self.device_id)
        # FIXME
        ld_initialized = self.adapter_agent.create_logical_device(ld, dpid='de:ad:be:ef:fe:ed') # FIXME
        self.logical_device_id = ld_initialized.id

        # Update device
        device.root = True
        device.vendor = 'Edgecore'
        device.model = 'ASFvOLT16'
        device.serial_number = self.host_and_port # FIXME
        device.parent_id = self.logical_device_id
        device.connect_status = ConnectStatus.REACHABLE
        device.oper_status = OperStatus.ACTIVATING
        self.adapter_agent.update_device(device)


        # Initialize gRPC
        self.channel = grpc.insecure_channel(self.host_and_port)
        self.channel_ready_future = grpc.channel_ready_future(self.channel)

        # Start indications thread
        self.indications_thread = threading.Thread(target=self.process_indications)
        self.indications_thread.daemon = True
        self.indications_thread.start()

    def process_indications(self):
        self.channel_ready_future.result() # blocks till gRPC connection is complete
        self.stub = openolt_pb2_grpc.OpenoltStub(self.channel)
        self.indications = self.stub.EnableIndication(openolt_pb2.Empty())
        while True:
            # get the next indication from olt
            ind = next(self.indications)
            self.log.debug("rx indication", indication=ind)
            # schedule indication handlers to be run in the main event loop
            if ind.HasField('olt_ind'):
                reactor.callFromThread(self.olt_indication, ind.olt_ind)
            elif ind.HasField('intf_ind'):
                reactor.callFromThread(self.intf_indication, ind.intf_ind)
            elif ind.HasField('intf_oper_ind'):
                reactor.callFromThread(self.intf_oper_indication, ind.intf_oper_ind)
            elif ind.HasField('onu_disc_ind'):
                reactor.callFromThread(self.onu_discovery_indication, ind.onu_disc_ind)
            elif ind.HasField('onu_ind'):
                reactor.callFromThread(self.onu_indication, ind.onu_ind)
            elif ind.HasField('omci_ind'):
                reactor.callFromThread(self.omci_indication, ind.omci_ind)

    def olt_indication(self, olt_indication):
	self.log.debug("olt indication", olt_ind=olt_indication)
        self.set_oper_state(olt_indication.oper_state)

    def intf_indication(self, intf_indication):
	self.log.debug("intf indication", intf_id=intf_indication.intf_id,
            oper_state=intf_indication.oper_state)

        if intf_indication.oper_state == "up":
            oper_status = OperStatus.ACTIVE
        else:
            oper_status = OperStatus.DISCOVERED

        # FIXME - If port exists, update oper state
        self.add_port(intf_indication.intf_id, Port.PON_OLT, oper_status)

    def intf_oper_indication(self, intf_oper_indication):
	self.log.debug("Received interface oper state change indication", intf_id=intf_oper_indication.intf_id,
            type=intf_oper_indication.type, oper_state=intf_oper_indication.oper_state)

        if intf_oper_indication.oper_state == "up":
            oper_state = OperStatus.ACTIVE
        else:
            oper_state = OperStatus.DISCOVERED

        if intf_oper_indication.type == "nni":

            # FIXME - Ignore all nni ports except nni port 0
            if intf_oper_indication.intf_id != 0:
                return

            if intf_oper_indication.intf_id not in self.nni_oper_state:
                self.nni_oper_state[intf_oper_indication.intf_id] = oper_state
                port_no, label = self.add_port(intf_oper_indication.intf_id, Port.ETHERNET_NNI, oper_state)
	        self.log.debug("int_oper_indication", port_no=port_no, label=label)
                self.add_logical_port(port_no) # FIXME - add oper_state
            elif intf_oper_indication.intf_id != self.nni_oper_state:
                # FIXME - handle subsequent NNI oper state change
                pass

        elif intf_oper_indication.type == "pon":
            # FIXME - handle PON oper state change
            pass

    def onu_discovery_indication(self, onu_disc_indication):
	self.log.debug("onu discovery indication", intf_id=onu_disc_indication.intf_id,
            serial_number=onu_disc_indication.serial_number)

        onu_id = self.lookup_onu(serial_number=onu_disc_indication.serial_number)

        if onu_id is None:
            onu_id = self.new_onu_id(onu_disc_indication.intf_id)
            try:
                self.add_onu_device(
                    onu_disc_indication.intf_id,
                    self.intf_id_to_port_no(onu_disc_indication.intf_id, Port.PON_OLT),
                    onu_id,
                    onu_disc_indication.serial_number)
            except Exception as e:
                self.log.exception('onu activation failed', e=e)
            else:
                self.activate_onu(
                    onu_disc_indication.intf_id, onu_id,
                    serial_number=onu_disc_indication.serial_number)
        else:
            # FIXME - handle discovery of already activated onu
	    self.log.info("onu activation in progress",
                intf_id=onu_disc_indication.intf_id, onu_id=onu_id)

    def _get_next_uni_port(self):
        self.uni_port_num += 1
        return self.uni_port_num

    def onu_indication(self, onu_indication):

        self.log.debug("onu indication", intf_id=onu_indication.intf_id,
                onu_id=onu_indication.onu_id)

        # FIXME - handle onu_id/serial_number mismatch
        assert onu_indication.onu_id == self.lookup_onu(serial_number=onu_indication.serial_number)

        onu_device = self.adapter_agent.get_child_device(
            self.device_id, onu_id=onu_indication.onu_id)
        assert onu_device is not None

        msg = {'proxy_address':onu_device.proxy_address,
               'event':'activation-completed',
               'event_data':{'activation_successful':True}}
        self.adapter_agent.publish_inter_adapter_message(onu_device.id, msg)

        #
        # tcont create (onu)
        #
        alloc_id = self.mk_alloc_id(onu_indication.onu_id)
        msg = {'proxy_address':onu_device.proxy_address,
               'event':'create-tcont',
               'event_data':{'alloc_id':alloc_id}}
        self.adapter_agent.publish_inter_adapter_message(onu_device.id, msg)

        #
        # v_enet create (olt)
        #
        uni_no = self._get_next_uni_port()
        uni_name = self.port_name(uni_no, Port.ETHERNET_UNI)
	self.adapter_agent.add_port(
            self.device_id,
            Port(
                port_no=uni_no,
                label=uni_name,
                type=Port.ETHERNET_UNI,
                admin_state=AdminState.ENABLED,
                oper_status=OperStatus.ACTIVE))

        #
        # v_enet create (onu)
        #
        interface_name = self.port_name(onu_indication.intf_id, Port.PON_OLT)
        msg = {'proxy_address':onu_device.proxy_address,
               'event':'create-venet',
               'event_data':{'uni_name':uni_name, 'interface_name':uni_name}}
        self.adapter_agent.publish_inter_adapter_message(onu_device.id, msg)

        #
        # gem port create
        #
        gemport_id = self.mk_gemport_id(onu_indication.onu_id)
        msg = {'proxy_address':onu_device.proxy_address,
               'event':'create-gemport',
               'event_data':{'gemport_id':gemport_id}}
        self.adapter_agent.publish_inter_adapter_message(onu_device.id, msg)

    def mk_gemport_id(self, onu_id):
        return 1023 + onu_id # FIXME

    def mk_alloc_id(self, onu_id):
        return 1023 + onu_id # FIXME

    def omci_indication(self, omci_indication):

        self.log.debug("omci indication", intf_id=omci_indication.intf_id,
                onu_id=omci_indication.onu_id)

        onu_device = self.adapter_agent.get_child_device(
            self.device_id,
            onu_id=omci_indication.onu_id)
        self.adapter_agent.receive_proxied_message(
            onu_device.proxy_address,
            omci_indication.pkt)

    def activate_onu(self, intf_id, onu_id, serial_number):

        self.log.info("activate onu", intf_id=intf_id, onu_id=onu_id,
                      serial_number=serial_number)

        self.onus[Onu(intf_id=intf_id, onu_id=onu_id)] = serial_number

        onu = openolt_pb2.Onu(
            intf_id=intf_id, onu_id=onu_id, serial_number=serial_number)

        self.stub.ActivateOnu(onu)


    def send_proxied_message(self, proxy_address, msg):
        omci = openolt_pb2.OmciMsg(
            intf_id=proxy_address.channel_id, # intf_id
            onu_id=proxy_address.onu_id,
            pkt=str(msg))
        self.stub.OmciMsgOut(omci)

    def add_onu_device(self, intf_id, port_no, onu_id, serial_number):

        self.log.info("Adding ONU", port_no=port_no, onu_id=onu_id,
                      serial_number=serial_number)

        # NOTE - channel_id of onu is set to intf_id
        proxy_address = Device.ProxyAddress(
            device_id=self.device_id,
            channel_id=intf_id,
            onu_id=onu_id,
            onu_session_id=onu_id)

        self.log.info("Adding ONU", proxy_address=proxy_address)

        serial_number_str = ''.join([
            serial_number.vendor_id,
            self.stringify_vendor_specific(serial_number.vendor_specific)])

        self.adapter_agent.add_onu_device(
            parent_device_id=self.device_id, parent_port_no=port_no,
            vendor_id=serial_number.vendor_id, proxy_address=proxy_address,
            root=True, serial_number=serial_number_str,
            admin_state=AdminState.ENABLED) # FIXME

    def intf_id_to_port_no(self, intf_id, intf_type):
        if intf_type is Port.ETHERNET_NNI:
            # FIXME - Remove hardcoded '129'
            return intf_id + 129
        elif intf_type is Port.PON_OLT:
            # Interface Ids (reported by device) are zero-based indexed
            # OpenFlow port numbering is one-based.
            return intf_id + 1
        else:
	    raise Exception('Invalid port type')


    def port_name(self, port_no, port_type):
        if port_type is Port.ETHERNET_NNI:
            prefix = "nni"
        elif port_type is Port.PON_OLT:
            prefix = "pon"
        elif port_type is Port.ETHERNET_UNI:
            prefix = "uni"
        return prefix + "-" + str(port_no)

    def update_device_status(self, connect_status=None, oper_status=None, reason=None):
        device = self.adapter_agent.get_device(self.device_id)
        if connect_status is not None:
            device.connect_status = connect_status
        if oper_status is not None:
            device.oper_status = oper_status
        if reason is not None:
            device.reason = reason
        self.adapter_agent.update_device(device)

    def add_logical_port(self, port_no):
        self.log.info('adding-logical-port', port_no=port_no)

        label = self.port_name(port_no, Port.ETHERNET_NNI)

        cap = OFPPF_1GB_FD | OFPPF_FIBER
        curr_speed = OFPPF_1GB_FD
        max_speed = OFPPF_1GB_FD

        ofp = ofp_port(
            port_no=port_no,
            hw_addr=mac_str_to_tuple('00:00:00:00:00:%02x' % port_no),
            name=label,
            config=0,
            state=OFPPS_LIVE,
            curr=cap,
            advertised=cap,
            peer=cap,
            curr_speed=curr_speed,
            max_speed=max_speed)

        logical_port = LogicalPort(
            id=label,
            ofp_port=ofp,
            device_id=self.device_id,
            device_port_no=port_no,
            root_port=True
        )

        self.adapter_agent.add_logical_port(self.logical_device_id, logical_port)

    def add_port(self, intf_id, port_type, oper_status):
        port_no = self.intf_id_to_port_no(intf_id, port_type)

        label = self.port_name(port_no, port_type)

        self.log.info('adding-port', port_no=port_no, label=label, port_type=port_type)
        port = Port(
            port_no=port_no,
            label=label,
            type=port_type,
            admin_state=AdminState.ENABLED,
            oper_status=oper_status
        )
        self.adapter_agent.add_port(self.device_id, port)
        return port_no, label

    def set_oper_state(self, new_state):
        if self.oper_state != new_state:
	    if new_state == 'up':
	        self.update_device_status(
		    connect_status=ConnectStatus.REACHABLE,
		    oper_status=OperStatus.ACTIVE,
		    reason='OLT indication - operation state up')
	    elif new_state == 'down':
	        self.update_device_status(
		    connect_status=ConnectStatus.REACHABLE,
		    oper_status=OperStatus.FAILED,
		    reason='OLT indication - operation state down')
            else:
	        raise ValueError('Invalid oper_state in olt_indication')

            self.oper_state = new_state

    def new_onu_id(self, intf_id):
        onu_id = None
        # onu_id is unique per PON.
        # FIXME - Remove hardcoded limit on ONUs per PON (64)
        for i in range(1, 64):
            onu = Onu(intf_id=intf_id, onu_id=i)
            if onu not in self.onus:
                onu_id = i
                break
        return onu_id

    def stringify_vendor_specific(self, vendor_specific):
        return ''.join(str(i) for i in [
		    ord(vendor_specific[0])>>4 & 0x0f,
		    ord(vendor_specific[0]) & 0x0f,
		    ord(vendor_specific[1])>>4 & 0x0f,
		    ord(vendor_specific[1]) & 0x0f,
		    ord(vendor_specific[2])>>4 & 0x0f,
		    ord(vendor_specific[2]) & 0x0f,
		    ord(vendor_specific[3])>>4 & 0x0f,
		    ord(vendor_specific[3]) & 0x0f])

    def lookup_onu(self, serial_number):
        onu_id = None
        for onu, s in self.onus.iteritems():
            if s.vendor_id == serial_number.vendor_id:
                str1 = self.stringify_vendor_specific(s.vendor_specific)
                str2 = self.stringify_vendor_specific(serial_number.vendor_specific)
                if str1 == str2:
                    onu_id = onu.onu_id
                    break
        return onu_id

    def update_flow_table(self, flows):
        device = self.adapter_agent.get_device(self.device_id)
        self.log.info('update flow table', flows=flows)

        for flow in flows:
            self.log.info('flow-details', device_id=self.device_id, flow=flow)
            classifier_info = dict()
            action_info = dict()
            is_down_stream = None
            _in_port = None
            try:
                _in_port = fd.get_in_port(flow)
                assert _in_port is not None
                # Right now there is only one NNI port. Get the NNI PORT and compare
                # with IN_PUT port number. Need to find better way.
                ports = self.adapter_agent.get_ports(device.id, Port.ETHERNET_NNI)

                for port in ports:
                    if (port.port_no == _in_port):
                        self.log.info('downstream-flow')
                        is_down_stream = True
                        break
                if is_down_stream is None:
                    is_down_stream = False
                    self.log.info('upstream-flow')

                _out_port = fd.get_out_port(flow)  # may be None
                self.log.info('out-port', out_port=_out_port)

                for field in fd.get_ofb_fields(flow):

                    if field.type == fd.ETH_TYPE:
                        classifier_info['eth_type'] = field.eth_type
                        self.log.info('field-type-eth-type',
                                      eth_type=classifier_info['eth_type'])

                    elif field.type == fd.IP_PROTO:
                        classifier_info['ip_proto'] = field.ip_proto
                        self.log.info('field-type-ip-proto',
                                      ip_proto=classifier_info['ip_proto'])

                    elif field.type == fd.IN_PORT:
                        classifier_info['in_port'] = field.port
                        self.log.info('field-type-in-port',
                                      in_port=classifier_info['in_port'])

                    elif field.type == fd.VLAN_VID:
                        classifier_info['vlan_vid'] = field.vlan_vid & 0xfff
                        self.log.info('field-type-vlan-vid',
                                      vlan=classifier_info['vlan_vid'])

                    elif field.type == fd.VLAN_PCP:
                        classifier_info['vlan_pcp'] = field.vlan_pcp
                        self.log.info('field-type-vlan-pcp',
                                      pcp=classifier_info['vlan_pcp'])

                    elif field.type == fd.UDP_DST:
                        classifier_info['udp_dst'] = field.udp_dst
                        self.log.info('field-type-udp-dst',
                                      udp_dst=classifier_info['udp_dst'])

                    elif field.type == fd.UDP_SRC:
                        classifier_info['udp_src'] = field.udp_src
                        self.log.info('field-type-udp-src',
                                      udp_src=classifier_info['udp_src'])

                    elif field.type == fd.IPV4_DST:
                        classifier_info['ipv4_dst'] = field.ipv4_dst
                        self.log.info('field-type-ipv4-dst',
                                      ipv4_dst=classifier_info['ipv4_dst'])

                    elif field.type == fd.IPV4_SRC:
                        classifier_info['ipv4_src'] = field.ipv4_src
                        self.log.info('field-type-ipv4-src',
                                      ipv4_dst=classifier_info['ipv4_src'])

                    elif field.type == fd.METADATA:
                        classifier_info['metadata'] = field.table_metadata
                        self.log.info('field-type-metadata',
                                      metadata=classifier_info['metadata'])

                    else:
                        raise NotImplementedError('field.type={}'.format(
                            field.type))

                for action in fd.get_actions(flow):

                    if action.type == fd.OUTPUT:
                        action_info['output'] = action.output.port
                        self.log.info('action-type-output',
                                      output=action_info['output'],
                                      in_port=classifier_info['in_port'])

                    elif action.type == fd.POP_VLAN:
                        action_info['pop_vlan'] = True
                        self.log.info('action-type-pop-vlan',
                                      in_port=_in_port)

                    elif action.type == fd.PUSH_VLAN:
                        action_info['push_vlan'] = True
                        action_info['tpid'] = action.push.ethertype
                        self.log.info('action-type-push-vlan',
                                      push_tpid=action_info['tpid'],
                                      in_port=_in_port)
                        if action.push.ethertype != 0x8100:
                            self.log.error('unhandled-tpid',
                                           ethertype=action.push.ethertype)

                    elif action.type == fd.SET_FIELD:
                        # action_info['action_type'] = 'set_field'
                        _field = action.set_field.field.ofb_field
                        assert (action.set_field.field.oxm_class ==
                                OFPXMC_OPENFLOW_BASIC)
                        self.log.info('action-type-set-field',
                                      field=_field, in_port=_in_port)
                        if _field.type == fd.VLAN_VID:
                            self.log.info('set-field-type-vlan-vid',
                                          vlan_vid=_field.vlan_vid & 0xfff)
                            action_info['vlan_vid'] = (_field.vlan_vid & 0xfff)
                        else:
                            self.log.error('unsupported-action-set-field-type',
                                           field_type=_field.type)
                    else:
                        self.log.error('unsupported-action-type',
                                       action_type=action.type, in_port=_in_port)

                if is_down_stream is False:
                    intf_id, onu_id = self.parse_port_no(classifier_info['in_port'])
                    self.divide_and_add_flow(onu_id, intf_id, classifier_info, action_info)
            except Exception as e:
                self.log.exception('failed-to-install-flow', e=e, flow=flow)

    def parse_port_no(self, port_no):
        return 0, 1 # FIXME

    # This function will divide the upstream flow into both
    # upstreand and downstream flow, as broadcom devices
    # expects down stream flows to be added to handle
    # packet_out messge from controller.
    def divide_and_add_flow(self, onu_id, intf_id, classifier, action):
        if 'ip_proto' in classifier:
            if classifier['ip_proto'] == 17:
                self.log.info('dhcp flow add')
                self.add_dhcp_trap(classifier, action, onu_id, intf_id)
            elif classifier['ip_proto'] == 2:
                self.log.info('igmp flow add ignored')
            else:
                self.log.info("Invalid-Classifier-to-handle", classifier=classifier,
                        action=action)
        elif 'eth_type' in classifier:
            if classifier['eth_type'] == 0x888e:
                self.log.error('epol flow add ignored')
        elif 'push_vlan' in action:
            self.add_data_flow(onu_id, intf_id, classifier, action)
        else:
            self.log.info('Invalid-flow-type-to-handle', classifier=classifier,
                    action=action)

    def add_data_flow(self, onu_id, intf_id, uplink_classifier, uplink_action):

        downlink_classifier = dict(uplink_classifier)
        downlink_action = dict(uplink_action)

        uplink_classifier['pkt_tag_type'] = 'single_tag'

        downlink_classifier['pkt_tag_type'] = 'double_tag'
        downlink_classifier['vlan_vid'] = uplink_action['vlan_vid']
        downlink_classifier['metadata'] = uplink_classifier['vlan_vid']
        del downlink_action['push_vlan']
        downlink_action['pop_vlan'] = True

        # To-Do right now only one GEM port is supported, so below method
        # will take care of handling all the p bits.
        # We need to revisit when mulitple gem port per p bits is needed.
        self.add_hsia_flow(onu_id, intf_id, uplink_classifier, uplink_action,
                downlink_classifier, downlink_action, ASFVOLT_HSIA_ID)

    def mk_classifier(self, classifier_info):

        classifier = openolt_pb2.Classifier()

        if 'eth_type' in classifier_info:
            classifier.eth_type = classifier_info['eth_type']
        if 'ip_proto' in classifier_info:
            classifier.ip_proto = classifier_info['ip_proto']
        if 'vlan_vid' in classifier_info:
            classifier.o_vid = classifier_info['vlan_vid']
        if 'metadata' in classifier_info:
            classifier.i_vid = classifier_info['metadata']
        if 'vlan_pcp' in classifier_info:
            classifier.o_pbits = classifier_info['vlan_pcp']
        if 'udp_src' in classifier_info:
            classifier.src_port = classifier_info['udp_src']
        if 'udp_dst' in classifier_info:
            classifier.dst_port = classifier_info['udp_dst']
        if 'ipv4_dst' in classifier_info:
            classifier.dst_ip = classifier_info['ipv4_dst']
        if 'ipv4_src' in classifier_info:
            classifier.src_ip = classifier_info['ipv4_src']
        if 'pkt_tag_type' in classifier_info:
            if classifier_info['pkt_tag_type'] == 'single_tag':
                classifier.pkt_tag_type = 'single_tag'
            elif classifier_info['pkt_tag_type'] == 'double_tag':
                classifier.pkt_tag_type = 'double_tag'
            elif classifier_info['pkt_tag_type'] == 'untagged':
                classifier.pkt_tag_type = 'untagged'
            else:
                classifier.pkt_tag_type = 'none'

        return classifier

    def mk_action(self, action_info):
        action = openolt_pb2.Action()

	if 'pop_vlan' in action_info:
	    action.o_vid = action_info['vlan_vid']
            action.cmd.remove_outer_tag = True
	elif 'push_vlan' in action_info:
	    action.o_vid = action_info['vlan_vid']
            action.cmd.add_outer_tag = True
	elif 'trap_to_host' in action_info:
            action.cmd.trap_to_host = True
	else:
	    self.log.info('Invalid-action-field')
	    return
        return action

    def add_hsia_flow(self, onu_id, intf_id, uplink_classifier, uplink_action,
                downlink_classifier, downlink_action, hsia_id):

        gemport_id = self.mk_gemport_id(onu_id)
        flow_id = self.mk_flow_id(onu_id, intf_id, hsia_id)

        self.log.info('add upstream flow', onu_id=onu_id, classifier=uplink_classifier,
                action=uplink_action, gemport_id=gemport_id, flow_id=flow_id)

        flow = openolt_pb2.Flow(
                onu_id=onu_id, flow_id=flow_id, flow_type="upstream",
                gemport_id=gemport_id, classifier=self.mk_classifier(uplink_classifier),
                action=self.mk_action(uplink_action))

        self.stub.FlowAdd(flow)
        time.sleep(0.1) # FIXME

        self.log.info('add downstream flow', classifier=downlink_classifier,
                action=downlink_action, gemport_id=gemport_id, flow_id=flow_id)

        flow = openolt_pb2.Flow(
                onu_id=onu_id, flow_id=flow_id, flow_type="downstream",
                access_intf_id=intf_id, gemport_id=gemport_id,
                classifier=self.mk_classifier(downlink_classifier),
                action=self.mk_action(downlink_action))

        self.stub.FlowAdd(flow)
        time.sleep(0.1) # FIXME

    def add_dhcp_trap(self, classifier, action, onu_id, intf_id):

        self.log.info('add dhcp trap', classifier=classifier, action=action)

        action.clear()
        action['trap_to_host'] = True
        classifier['pkt_tag_type'] = 'single_tag'
        classifier.pop('vlan_vid', None)

        gemport_id = self.mk_gemport_id(onu_id)
        flow_id = self.mk_flow_id(onu_id, intf_id, ASFVOLT_DHCP_TAGGED_ID)

        flow = openolt_pb2.Flow(
                onu_id=onu_id, flow_id=flow_id, flow_type="upstream",
                gemport_id=gemport_id, classifier=self.mk_classifier(classifier),
                action=self.mk_action(action))

        self.stub.FlowAdd(flow)

    def mk_flow_id(self, onu_id, intf_id, id):
        # Tp-Do Need to generate unique flow ID using
        # OnuID, IntfId, id
        # BAL accepts flow_id till 16384. So we are
        # using only onu_id and id to generate flow ID.
        return ((onu_id << 5) | id)
