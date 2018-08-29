# Copyright 2017-present Adtran, Inc.
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

import json
import random

import structlog

from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks, returnValue
#

from voltha.extensions.alarms.onu.onu_los_alarm import OnuLosAlarm
from voltha.protos.common_pb2 import AdminState
from voltha.protos.device_pb2 import Port

class PonPort(object):
    """
    GPON Port

        This is a highly reduced version taken from the adtran nni_port.
    TODO:   add functions to allow for port specific values and operations
    """
    MAX_ONUS_SUPPORTED = 256
    DEFAULT_ENABLED = False
    MAX_DEPLOYMENT_RANGE = 25000    # Meters (OLT-PB maximum)

    _MCAST_ONU_ID = 253
    _MCAST_ALLOC_BASE = 0x500

    _SUPPORTED_ACTIVATION_METHODS = ['autodiscovery']    # , 'autoactivate']
    _SUPPORTED_AUTHENTICATION_METHODS = ['serial-number']

    def __init__(self, **kwargs):

        # super(PonPort, self).__init__(parent, **kwargs)

        assert 'pon-id' in kwargs, 'PON ID not found'


        self._pon_id = kwargs['pon-id']
        self._device_id = kwargs['device_id']
        self._intf_id = kwargs['intf_id']
        self.log = structlog.get_logger(device_id=self._device_id, pon_id=self._pon_id)
        self._port_no = kwargs['port_no']
        # self._name = 'xpon 0/{}'.format(self._pon_id+1)
        self._label = 'pon-{}'.format(self._pon_id)

        self._in_sync = False
        self._expedite_sync = False
        self._expedite_count = 0

        self._discovery_tick = 20.0
        self._no_onu_discover_tick = self._discovery_tick / 2
        self._discovered_onus = []  # List of serial numbers

        self._onus = {}         # serial_number-base64 -> ONU  (allowed list)
        self._onu_by_id = {}    # onu-id -> ONU
        # self._next_onu_id = Onu.MIN_ONU_ID + 128
        self._mcast_gem_ports = {}                # VLAN -> GemPort

        self._discovery_deferred = None           # Specifically for ONU discovery
        self._active_los_alarms = set()           # ONU-ID

        # xPON configuration

        self._xpon_name = None
        self._downstream_fec_enable = False
        self._upstream_fec_enable = False
        self._deployment_range = 25000
        self._authentication_method = 'serial-number'
        self._mcast_aes = False
        self._line_rate = 'down_10_up_10'
        self._activation_method = 'autodiscovery'


        # Statistics  taken from nni_port

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
        return "PonPort-{}: Admin: {}, Oper: {}, OLT: {}".format(self._label,
                                                                 self._admin_state,
                                                                 self._oper_status,
                                                                 self.olt)

    # def get_port(self):
    #     """
    #     Get the VOLTHA PORT object for this port
    #     :return: VOLTHA Port object
    #     """
    #     if self._port is None:
    #         self._port = Port(port_no=self._port_no,
    #                           label=self._label,
    #                           type=Port.PON_OLT,
    #                           admin_state=self._admin_state,
    #                           oper_status=self._oper_status)
    #
    #     return self._port
    #
    # @property
    # def xpon_name(self):
    #     return self._xpon_name
    #
    # @xpon_name.setter
    # def xpon_name(self, value):
    #     assert '/' not in value, "xPON names cannot have embedded forward slashes '/'"
    #     self._xpon_name = value

    @property
    def intf_id(self):
        return self._intf_id

    @property
    def pon_id(self):
        return self._pon_id

    @property
    def port_no(self):
        return self._port_no

    @property
    def onus(self):
        """
        Get a set of all ONUs.  While the set is immutable, do not use this method
        to get a collection that you will iterate through that my yield the CPU
        such as inline callback.  ONUs may be deleted at any time and they will
        set some references to other objects to NULL during the 'delete' call.
        Instead, get a list of ONU-IDs and iterate on these and call the 'onu'
        method below (which will return 'None' if the ONU has been deleted.

        :return: (frozenset) collection of ONU objects on this PON
        """
        return frozenset(self._onus.values())

    @property
    def onu_ids(self):
        return frozenset(self._onu_by_id.keys())

    def onu(self, onu_id):
        return self._onu_by_id.get(onu_id)

    @property
    def in_service_onus(self):
        return len({onu.onu_id for onu in self.onus
                    if onu.onu_id not in self._active_los_alarms})

    @property
    def closest_onu_distance(self):
        distance = -1
        for onu in self.onus:
            if onu.fiber_length < distance or distance == -1:
                distance = onu.fiber_length
        return distance

    @property
    def downstream_fec_enable(self):
        return self._downstream_fec_enable

    @downstream_fec_enable.setter
    def downstream_fec_enable(self, value):
        assert isinstance(value, bool), 'downstream FEC enabled is a boolean'

        if self._downstream_fec_enable != value:
            self._downstream_fec_enable = value
            if self.state == AdtnPort.State.RUNNING:
                self.deferred = self._set_pon_config("downstream-fec-enable", value)

    @property
    def upstream_fec_enable(self):
        return self._upstream_fec_enable


    @property
    def line_rate(self):
        return self._line_rate

    @line_rate.setter
    def line_rate(self, value):
        assert isinstance(value, (str, unicode)), 'Line Rate is a string'
        # TODO cast to enum
        if self._line_rate != value:
            self._line_rate = value
            if self.state == AdtnPort.State.RUNNING:
                pass    # TODO

    @property
    def deployment_range(self):
        """Maximum deployment range (in meters)"""
        return self._deployment_range



    @property
    def discovery_tick(self):
        return self._discovery_tick * 10
    
    @discovery_tick.setter
    def discovery_tick(self, value):
        if value < 0:
            raise ValueError("Polling interval must be >= 0")

        if self.discovery_tick != value:
            self._discovery_tick = value / 10

            try:
                if self._discovery_deferred is not None and \
                        not self._discovery_deferred.called:
                    self._discovery_deferred.cancel()
            except:
                pass
            self._discovery_deferred = None

            if self._discovery_tick > 0:
                self._discovery_deferred = reactor.callLater(self._discovery_tick,
                                                             self._discover_onus)

    @property
    def activation_method(self):
        return self._activation_method

    @activation_method.setter
    def activation_method(self, value):
        value = value.lower()
        if value not in PonPort._SUPPORTED_ACTIVATION_METHODS:
            raise ValueError('Invalid ONU activation method')
        self._activation_method = value

    @property
    def authentication_method(self):
        return self._authentication_method

    @authentication_method.setter
    def authentication_method(self, value):
        value = value.lower()
        if value not in PonPort._SUPPORTED_AUTHENTICATION_METHODS:
            raise ValueError('Invalid ONU authentication method')
        self._authentication_method = value

    def cancel_deferred(self):
        super(PonPort, self).cancel_deferred()

        d, self._discovery_deferred = self._discovery_deferred, None

        try:
            if d is not None and not d.called:
                d.cancel()
        except Exception as e:
            pass

    def _update_adapter_agent(self):
        """
        Update the port status and state in the core
        """
        self.log.debug('update-adapter-agent', admin_state=self._admin_state,
                       oper_status=self._oper_status)

        # because the core does not provide methods for updating admin
        # and oper status per port, we need to copy any existing port
        # info so that we don't wipe out the peers
        if self._port is not None:
            agent_ports = self.adapter_agent.get_ports(self.olt.device_id, Port.PON_OLT)

            agent_port = next((ap for ap in agent_ports if ap.port_no == self._port_no), None)

            # copy current Port info
            if agent_port is not None:
                self._port = agent_port

        # set new states
        self._port.admin_state = self._admin_state
        self._port.oper_status = self._oper_status

        # adapter_agent add_port also does an update of existing port
        self.adapter_agent.add_port(self.olt.device_id, self.get_port())




