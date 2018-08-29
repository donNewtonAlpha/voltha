#
# Copyright 2017-present Adtran, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import random

# import structlog
# import xmltodict
# from port import OpenOltPrt
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks, returnValue, succeed, fail
from twisted.python.failure import Failure
from voltha.core.logical_device_agent import mac_str_to_tuple
from voltha.protos.common_pb2 import OperStatus, AdminState
from voltha.protos.device_pb2 import Port
from voltha.protos.logical_device_pb2 import LogicalPort
from voltha.protos.openflow_13_pb2 import OFPPF_100GB_FD, OFPPF_FIBER, OFPPS_LIVE, ofp_port


class NniPort(object):
    """
    Northbound network port, often Ethernet-based

    This is a highly reduced version taken from the adtran nni_port.
    TODO:   add functions to allow for port specific values and operations

    """
    def __init__(self, **kwargs):
        # super(NniPort, self).__init__( **kwargs)

        # TODO: Weed out those properties supported by common 'Port' object

        # self.log = structlog.get_logger(port_no=kwargs.get('port_no'))
        # self.log.info('creating')

        self.port_no = kwargs.get('port_no')
        self._port_no = self.port_no
        self._name = kwargs.get('name', 'nni-{}'.format(self._port_no))

        self._logical_port = None

        self.sync_tick = 10.0

        self._stats_tick = 5.0
        self._stats_deferred = None

        # Local cache of NNI configuration

        self._ianatype = '<type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>'

        # And optional parameters
        # TODO: Currently cannot update admin/oper status, so create this enabled and active
        # self._admin_state = kwargs.pop('admin_state', AdminState.UNKNOWN)
        # self._oper_status = kwargs.pop('oper_status', OperStatus.UNKNOWN)
        self._enabled = True
        self._admin_state = AdminState.ENABLED
        self._oper_status = OperStatus.ACTIVE

        self._label = kwargs.pop('label', 'NNI port {}'.format(self._port_no))
        self._mac_address = kwargs.pop('mac_address', '00:00:00:00:00:00')
        # TODO: Get with JOT and find out how to pull out MAC Address via NETCONF
        # TODO: May need to refine capabilities into current, advertised, and peer

        self._ofp_capabilities = kwargs.pop('ofp_capabilities', OFPPF_100GB_FD | OFPPF_FIBER)
        self._ofp_state = kwargs.pop('ofp_state', OFPPS_LIVE)
        self._current_speed = kwargs.pop('current_speed', OFPPF_100GB_FD)
        self._max_speed = kwargs.pop('max_speed', OFPPF_100GB_FD)
        self._device_port_no = kwargs.pop('device_port_no', self._port_no)
        self.intf_id = kwargs.pop('intf_id', None)


        # Statistics

        self.rx_bytes = 0
        self.rx_packets = 0
        self.rx_mcast_packets = 0
        self.rx_bcast_packets = 0

        self.rx_error_packets = 0
        self.tx_bytes = 0
        self.tx_packets = 0
        self.tx_ucast_packets = 0
        self.tx_mcast_packets = 0
        self.tx_bcast_packets = 0
        self.tx_error_packets = 0
        return

    def __str__(self):
        return "NniPort-{}: Admin: {}, Oper: {}, parent: {}".format(self._port_no,
                                                                    self._admin_state,
                                                                    self._oper_status,
                                                                    self._parent)

    # def get_port(self):
    #     """
    #     Get the VOLTHA PORT object for this port
    #     :return: VOLTHA Port object
    #     """
    #     self.log.debug('get-port-status-update', port=self._port_no,
    #                    label=self._label)
    #     if self._port is None:
    #         self._port = Port(port_no=self._port_no,
    #                           label=self._label,
    #                           type=Port.ETHERNET_NNI,
    #                           admin_state=self._admin_state,
    #                           oper_status=self._oper_status)
    #
    #     if self._port.admin_state != self._admin_state or\
    #        self._port.oper_status != self._oper_status:
    #
    #         self.log.debug('get-port-status-update', admin_state=self._admin_state,
    #                        oper_status = self._oper_status)
    #         self._port.admin_state = self._admin_state
    #         self._port.oper_status = self._oper_status
    #
    #     return self._port
    #
    # @property
    # def iana_type(self):
    #     return self._ianatype
    #
    # def _update_adapter_agent(self):
    #     # adapter_agent add_port also does an update of port status
    #     self.log.debug('update-adapter-agent', admin_state=self._admin_state,
    #                    oper_status=self._oper_status)
    #     self.adapter_agent.add_port(self.olt.device_id, self.get_port())
    #
    # def get_logical_port(self):
    #     """
    #     Get the VOLTHA logical port for this port
    #     :return: VOLTHA logical port or None if not supported
    #     """
    #     if self._logical_port is None:
    #         openflow_port = ofp_port(port_no=self._port_no,
    #                                  hw_addr=mac_str_to_tuple(self._mac_address),
    #                                  name=self._name,
    #                                  config=0,
    #                                  state=self._ofp_state,
    #                                  curr=self._ofp_capabilities,
    #                                  advertised=self._ofp_capabilities,
    #                                  peer=self._ofp_capabilities,
    #                                  curr_speed=self._current_speed,
    #                                  max_speed=self._max_speed)
    #
    #         self._logical_port = LogicalPort(id='nni{}'.format(self._port_no),
    #                                          ofp_port=openflow_port,
    #                                          device_id=self._parent.device_id,
    #                                          device_port_no=self._device_port_no,
    #                                          root_port=True)
    #     return self._logical_port
    #



