


# from voltha.protos.events_pb2 import KpiEvent, MetricValuePairs
# from voltha.protos.events_pb2 import KpiEventType
# import voltha.adapters.openolt.openolt_platform as platform
# from voltha.extensions.kpi.olt.olt_pm_metrics import OltPmMetrics
#




import sys,os, json
from voltha.protos.third_party.google.api import annotations_pb2
from voltha.protos.device_pb2 import PmConfig, PmConfigs, PmGroupConfig
from voltha.extensions.kpi.olt.olt_pm_metrics import OltPmMetrics
from voltha.core.adapter_agent_alt import AdapterAgentAlt
from voltha.adapters.simulated_olt.simulated_olt import SimulatedOltAdapter
from voltha.registry import registry
from voltha.extensions.mz_kpi_tests.olt_pm_metrics_alt import OltPmMetricsAlt
from voltha.protos.device_pb2 import Port
from voltha.protos.common_pb2 import OperStatus, AdminState
from voltha.extensions.mz_kpi_tests.onu_port import OnuPort

from voltha.extensions.mz_kpi_tests.map2test import map2Test


def buildMetrics():
    nni_pm_names = {
        ('admin_state', PmConfig.STATE),
        ('oper_status', PmConfig.STATE),
        ('port_no', PmConfig.GUAGE),  # Device and logical_device port numbers same
        ('rx_packets', PmConfig.COUNTER),
        ('rx_bytes', PmConfig.COUNTER),
        ('rx_dropped', PmConfig.COUNTER),
        ('rx_errors', PmConfig.COUNTER),
        ('rx_bcast', PmConfig.COUNTER),
        ('rx_mcast', PmConfig.COUNTER),
        ('tx_packets', PmConfig.COUNTER),
        ('tx_bytes', PmConfig.COUNTER),
        ('tx_dropped', PmConfig.COUNTER),
        ('tx_bcast', PmConfig.COUNTER),
        ('tx_mcast', PmConfig.COUNTER),

    }
    pon_pm_names = {
        ('admin_state', PmConfig.STATE),
        ('oper_status', PmConfig.STATE),
        ('port_no', PmConfig.GUAGE),  # Physical device port number
        ('pon_id', PmConfig.GUAGE),
        ('rx_packets', PmConfig.COUNTER),
        ('rx_bytes', PmConfig.COUNTER),
        ('tx_packets', PmConfig.COUNTER),
        ('tx_bytes', PmConfig.COUNTER),
        ('tx_bip_errors', PmConfig.COUNTER),
        ('in_service_onus', PmConfig.GUAGE),
        ('closest_onu_distance', PmConfig.GUAGE)
    }
    onu_pm_names = {
        ('pon_id', PmConfig.GUAGE),
        ('onu_id', PmConfig.GUAGE),
        ('fiber_length', PmConfig.GUAGE),
        ('equalization_delay', PmConfig.GUAGE),
        ('rssi', PmConfig.GUAGE),  #
    }
    gem_pm_names = {
        ('pon_id', PmConfig.GUAGE),
        ('onu_id', PmConfig.GUAGE),
        ('gem_id', PmConfig.GUAGE),
        ('alloc_id', PmConfig.GUAGE),
        ('rx_packets', PmConfig.COUNTER),
        ('rx_bytes', PmConfig.COUNTER),
        ('tx_packets', PmConfig.COUNTER),
        ('tx_bytes', PmConfig.COUNTER),
    }
    nni_metrics_config = {m: PmConfig(name=m, type=t, enabled=True)
                               for (m, t) in nni_pm_names}
    pon_metrics_config = {m: PmConfig(name=m, type=t, enabled=True)
                               for (m, t) in pon_pm_names}
    onu_metrics_config = {m: PmConfig(name=m, type=t, enabled=True)
                               for (m, t) in onu_pm_names}
    gem_metrics_config = {m: PmConfig(name=m, type=t, enabled=True)
                               for (m, t) in gem_pm_names}

    foo = True
    return pon_metrics_config

def build_port(port_num, type="ETHERNET"):
    try:
        #Build the label

        label = 'NNI port {}'.format(port_num)

        if type == "ETHERNET":
            port = Port(port_no=port_num, type=Port.ETHERNET_NNI,
                    label=label,
                    admin_state=AdminState.ENABLED,
                    oper_status=OperStatus.ACTIVE)
        else:
            # PON ports require a different configuration
            port_olt = Port(port_no=port_num, type=Port.PON_OLT,
                        label=label,
                        admin_state=AdminState.ENABLED,
                        oper_status=OperStatus.ACTIVE)

            # port = {"port_no": , "onu_ids":[], "onu_id": "xxxxx", "port": port_olt}
            port = OnuPort(port_no=536870913, onu_id="xxxx", port=port_olt, onu_ids=[])
            foo = port

        return port

    except Exception as err:
        foo = err.message
        raise Exception(err)

def extract_pon_metrics( stats):
    try:
        rtrn_pon_metrics = dict()
        for m in stats.metrics:
            if m.port_name == "pon":
                for p in m.packets:
                    if pon_metrics_config[p.name].enabled:
                        rtrn_pon_metrics[p.name] = p.value
                return rtrn_pon_metrics
    except Exception as err1:
        print(err1.message)


def extract_nni_metrics(stats):
    try:
        rtrn_pon_metrics = dict()
        for m in stats.metrics:
            if m.port_name == "nni":
                for p in m.packets:
                    if pon_metrics_config[p.name].enabled:
                        rtrn_pon_metrics[p.name] = p.value
                return rtrn_pon_metrics
    except Exception as err1:
        print(err1.message)
        raise Exception(err1)

def main():

    try:
        stat = {'intf_id': 536870913,'tx_bytes': 428,'tx_packets': 2,'tx_mcast_packets': 2,'timestamp': 1534857356}
        # intf_id: 129
        # tx_bytes: 420
        # tx_packets: 2
        # tx_mcast_packets: 2
        # timestamp: 1534964059

        device_id = "00017579ccb9b"
        stats = {'tx_bcast_packets': 0L, 'rx_packets': 86L, 'rx_bytes': 7548L, 'tx_ucast_packets': 0L, 'rx_crc_errors': 0L,
         'rx_error_packets': 0L, 'tx_error_packets': 0L, 'tx_mcast_packets': 0L, 'rx_bcast_packets': 0L,
         'rx_ucast_packets': 0L, 'bip_errors': 0L, 'tx_bytes': 0L, 'tx_packets': 0L, 'rx_mcast_packets': 86L}
        # nni-ports = [4]
        # pon-ports = [5]

        # agent = AdapterAgentAlt("simulated_onu", SimulatedOltAdapter)

        nni_ports = []
        for i in range(0,4):
            nni_ports.append(build_port(port_num=i, type="ETHERNET"))
        pon_ports = []
        for i in range(0,5):
            pon_ports.append(build_port(port_num=i, type="OLT_PON"))

        kwargs = {
            'nni-ports': nni_ports,
            'pon-ports': pon_ports
        }

        oltmetrics = OltPmMetricsAlt(None, device_id, grouped=True, freq_override=False, **kwargs)
        # pon_metrics_config = buildMetrics()
        pm_configs = oltmetrics.make_proto()
        print(pm_configs)

        # Test updating first with just the proto.
        oltmetrics.update(pm_configs)


        # test the metrics collection
        collected = oltmetrics.collect_metrics()
        oltmetrics.collect_and_publish_metrics()

        # asjson = json.dumps(pon_metrics_config,indent=2,sort_keys=True)
        print("Done")
    except Exception as err1:
        print(err1.message)

    sys.exit()




if __name__ == '__main__':

    main()