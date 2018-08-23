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
from voltha.protos.events_pb2 import KpiEvent, MetricValuePairs
from voltha.protos.events_pb2 import KpiEventType
import voltha.adapters.openolt.openolt_platform as platform
from voltha.extensions.kpi.olt.olt_pm_metrics import OltPmMetrics

from voltha.protos.device_pb2 import PmConfig, PmConfigs, PmGroupConfig

# added for kpi extensions
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.python.failure import Failure

class OpenOltStatisticsMgr(object):
    def __init__(self, openolt_device, log):
        self.device = openolt_device
        self.log = log

        self.pm_metrics = None
        # Northbound and Southbound ports
        self.northbound_ports = {}  # port number -> Port
        self.southbound_ports = {}  # port number -> Port  (For PON, use pon-id as key)
        try:
            self.northbound_ports = {0:0, 1:1}  # port number -> Port
            self.southbound_ports = {0:0, 1:1}  # port number -> Port  (For PON, use pon-id as key)
        except Exception as dicterr:
            foo = dicterr
        try:
            self.set_pm_metrics()
        except Exception as metrics_err:
            foo = metrics_err



    def set_pm_metrics(self):
        ############################################################################
        # Setup PM configuration for this device
        if self.pm_metrics is None:
            try:
                try:
                    self.device.reason = 'setting up Performance Monitoring configuration'
                    # self.device.adapter_agent.update_device(self.device.device_id)
                except Exception as d1:
                    foo = d1  # jtesting ignore
                    foo = self.device


                kwargs = {
                    'nni-ports': self.northbound_ports.values(),
                    'pon-ports': self.southbound_ports.values()
                }
                self.pm_metrics = OltPmMetrics(self.device.adapter_agent, self.device.device_id,
                                               grouped=True, freq_override=False,
                                               **kwargs)

                pm_config = self.pm_metrics.make_proto()
                self.log.debug("initial-pm-config", pm_config=pm_config)
                self.device.adapter_agent.update_device_pm_config(pm_config, init=True)

            except Exception as e:
                self.log.exception('pm-setup', e=e)
                # self.activate_failed(self.device.device_id, e.message, reachable=False)

            # # Start collecting stats from the device after a brief pause
            # foo = reactor.callLater(10, self.pm_metrics.start_collector)
        ############################################################################

    def port_statistics_indication(self, port_stats):
        self.log.info('port-stats-collected', stats=port_stats)
        self.ports_statistics_kpis(port_stats)
        #FIXME: etcd problem, do not update objects for now

        #
        #
        # #FIXME : only the first uplink is a logical port
        # if port_stats.intf_id == 128:
        #     # ONOS update
        #     self.update_logical_port_stats(port_stats)
        # # FIXME: Discard other uplinks, they do not exist as an object
        # if port_stats.intf_id in [129, 130, 131]:
        #     self.log.debug('those uplinks are not created')
        #     return
        # # update port object stats
        # port = self.device.adapter_agent.get_port(self.device.device_id,
        #     port_no=port_stats.intf_id)
        #
        # if port is None:
        #     self.log.warn('port associated with this stats does not exist')
        #     return
        #
        # port.rx_packets = port_stats.rx_packets
        # port.rx_bytes = port_stats.rx_bytes
        # port.rx_errors = port_stats.rx_error_packets
        # port.tx_packets = port_stats.tx_packets
        # port.tx_bytes = port_stats.tx_bytes
        # port.tx_errors = port_stats.tx_error_packets
        #
        # # Add port does an update if port exists
        # self.device.adapter_agent.add_port(self.device.device_id, port)

    def flow_statistics_indication(self, flow_stats):
        self.log.info('flow-stats-collected', stats=flow_stats)
        # TODO: send to kafka ?
        # FIXME: etcd problem, do not update objects for now
        # # UNTESTED : the openolt driver does not yet provide flow stats
        # self.device.adapter_agent.update_flow_stats(
        #       self.device.logical_device_id,
        #       flow_id=flow_stats.flow_id, packet_count=flow_stats.tx_packets,
        #       byte_count=flow_stats.tx_bytes)

    def ports_statistics_kpis(self, port_stats):
        pm_data = {}
        pm_data["rx_bytes"] = port_stats.rx_bytes
        pm_data["rx_packets"] = port_stats.rx_packets
        pm_data["rx_ucast_packets"] = port_stats.rx_ucast_packets
        pm_data["rx_mcast_packets"] = port_stats.rx_mcast_packets
        pm_data["rx_bcast_packets"] = port_stats.rx_bcast_packets
        pm_data["rx_error_packets"] = port_stats.rx_error_packets
        pm_data["tx_bytes"] = port_stats.tx_bytes
        pm_data["tx_packets"] = port_stats.tx_packets
        pm_data["tx_ucast_packets"] = port_stats.tx_ucast_packets
        pm_data["tx_mcast_packets"] = port_stats.tx_mcast_packets
        pm_data["tx_bcast_packets"] = port_stats.tx_bcast_packets
        pm_data["tx_error_packets"] = port_stats.tx_error_packets
        pm_data["rx_crc_errors"] = port_stats.rx_crc_errors
        pm_data["bip_errors"] = port_stats.bip_errors


        prefix = 'voltha.openolt.{}'.format(self.device.device_id)



        # FIXME
        if port_stats.intf_id < 132:
            prefixes = {
                prefix + '.nni.{}'.format(port_stats.intf_id): MetricValuePairs(
                    metrics=pm_data)
            }
        else:
            prefixes = {
                prefix + '.pon.{}'.format(platform.intf_id_from_pon_port_no(
                    port_stats.intf_id)): MetricValuePairs(
                    metrics=pm_data)
            }
        foo = KpiEventType.slice
        kpi_event = KpiEvent(
            type=KpiEventType.slice,
            ts=port_stats.timestamp,
            prefixes=prefixes)
        self.device.adapter_agent.submit_kpis(kpi_event)
        #Some debug stuff

        self.grouped = False

        pmconfigs = None
        try:
            pmconfigs = PmConfigs(id=self.device.device_id, default_freq=150,
                      grouped=self.grouped,
                      freq_override=False)

        except Exception as failedConfig:
            foo = failedConfig

        pm_config = self.pm_metrics.make_proto(pmconfigs)
        foo = True
        """
        The following code is for testing the conversion to the voltha/extensions/kpis
        
        """

        # 1 convert the incoming stats to one of the structures in the olt_metrics group.
        try:
            port_type_name = platform.intf_id_to_port_type_name(intf_id=port_stats.intf_id).lower()
            if 'nni' in port_type_name:
                # foo = self.extract_nni_metrics(port_stats)
                foo = True
            elif 'pon' in port_type_name:
                # foo = self.extract_pon_metrics(port_stats)
                foo = True
            else:
                foo = True
        except Exception as extracterr:
            foo = extracterr

        foo = True

    def extract_pon_metrics(self, stats):
        rtrn_pon_metrics = dict()
        for m in stats.metrics:
            if m.port_name == "pon":
                for p in m.packets:
                    if self.pon_metrics_config[p.name].enabled:
                        rtrn_pon_metrics[p.name] = p.value
                return rtrn_pon_metrics

    def extract_nni_metrics(self, stats):
        rtrn_pon_metrics = dict()
        for m in stats.metrics:
            if m.port_name == "nni":
                for p in m.packets:
                    if self.pon_metrics_config[p.name].enabled:
                        rtrn_pon_metrics[p.name] = p.value
                return rtrn_pon_metrics

    def update_logical_port_stats(self, port_stats):
        # FIXME
        label = 'nni-{}'.format(port_stats.intf_id)
        try:
            logical_port = self.device.adapter_agent.get_logical_port(
                self.device.logical_device_id, label)
        except KeyError as e:
            self.log.warn('logical port was not found, it may not have been '
                          'created yet', exception=e)
            return

        if logical_port is None:
            self.log.error('logical-port-is-None',
                logical_device_id=self.device.logical_device_id, label=label,
                port_stats=port_stats)
            return


        logical_port.ofp_port_stats.rx_packets = port_stats.rx_packets
        logical_port.ofp_port_stats.rx_bytes = port_stats.rx_bytes
        logical_port.ofp_port_stats.tx_packets = port_stats.tx_packets
        logical_port.ofp_port_stats.tx_bytes = port_stats.tx_bytes
        logical_port.ofp_port_stats.rx_errors = port_stats.rx_error_packets
        logical_port.ofp_port_stats.tx_errors = port_stats.tx_error_packets
        logical_port.ofp_port_stats.rx_crc_err = port_stats.rx_crc_errors

        self.log.debug('after-stats-update', port=logical_port)

        self.device.adapter_agent.update_logical_port(
            self.device.logical_device_id, logical_port)
