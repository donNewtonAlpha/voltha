
import yaml
import sys,os, json, random
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.python.failure import Failure

from voltha.protos.third_party.google.api import annotations_pb2
from voltha.protos.device_pb2 import PmConfig, PmConfigs, PmGroupConfig
from voltha.extensions.kpi.olt.olt_pm_metrics import OltPmMetrics
from voltha.core.adapter_agent_alt import AdapterAgentAlt
from voltha.adapters.simulated_olt.simulated_olt import SimulatedOltAdapter
from voltha.registry import registry
from voltha.extensions.mz_kpi_tests.olt_pm_metrics_alt import OltPmMetricsAlt
from voltha.extensions.mz_kpi_tests.olt_pm_metrics import OltPmMetrics
# from voltha.extensions.kpi.olt.olt_pm_metrics import OltPmMetrics
from voltha.protos.device_pb2 import Port
from voltha.protos.common_pb2 import OperStatus, AdminState
from voltha.extensions.mz_kpi_tests.onu_port import OnuPort
from voltha.extensions.mz_kpi_tests.nni_port import NniPort
from voltha.extensions.mz_kpi_tests.pon_port import PonPort

import voltha.adapters.openolt.openolt_platform as platform
from voltha.extensions.mz_kpi_tests.map2test import map2Test
from common.structlog_setup import setup_logging, update_logging
from voltha.protos.events_pb2 import KpiEvent, MetricValuePairs
from voltha.protos.events_pb2 import KpiEventType

from voltha.adapters.openolt.protos.openolt_pb2 import PortStatistics
from voltha.adapters.openolt.openolt_statistics import OpenOltStatisticsMgr

"""
This will test the open_olt statistics module directly

"""



def load_config():
    path = os.getcwd()
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, "mztest_logging.yml")
    path = os.path.abspath(path)
    with open(path) as fd:
        config = yaml.load(fd)
    return config


def get_port_stats(intf_id, value=0):
    # pm_data["rx_bytes"] = port_stats.rx_bytes
    # pm_data["rx_packets"] = port_stats.rx_packets
    # pm_data["rx_ucast_packets"] = port_stats.rx_ucast_packets
    # pm_data["rx_mcast_packets"] = port_stats.rx_mcast_packets
    # pm_data["rx_bcast_packets"] = port_stats.rx_bcast_packets
    # pm_data["rx_error_packets"] = port_stats.rx_error_packets
    # pm_data["tx_bytes"] = port_stats.tx_bytes
    # pm_data["tx_packets"] = port_stats.tx_packets
    # pm_data["tx_ucast_packets"] = port_stats.tx_ucast_packets
    # pm_data["tx_mcast_packets"] = port_stats.tx_mcast_packets
    # pm_data["tx_bcast_packets"] = port_stats.tx_bcast_packets
    # pm_data["tx_error_packets"] = port_stats.tx_error_packets
    # pm_data["rx_crc_errors"] = port_stats.rx_crc_errors
    # pm_data["bip_errors"] = port_stats.bip_errors
    port_stats = PortStatistics(
        rx_bytes=1234 + value,
        rx_packets=value,
        rx_ucast_packets=value,
        rx_mcast_packets=value,
        rx_bcast_packets=value,
        rx_error_packets=value,
        tx_bytes=value,
        tx_packets=value,
        tx_ucast_packets=value,
        tx_mcast_packets=value,
        tx_bcast_packets=value,
        tx_error_packets=value,
        rx_crc_errors=value,
        bip_errors=1234 + value,
        intf_id=intf_id,
    )
    return port_stats

def main():

    try:
        config = load_config()
        instance_id = os.environ.get('INSTANCE_ID', os.environ.get('HOSTNAME', '1'))
        log = setup_logging(config.get('logging', {}), "main")

        # random.seed(42)
        print(random.sample(range(1000),k=10))
        print(random.randint(100,1000))



        port_stats = get_port_stats(random.randint(100,1000))
        print("port stats :")
        print(port_stats)
        foo = port_stats
        device_id = "00017579ccb9b"

        # Bring in a dummy device.  This will avoid any dependencies on the underlying
        # sysem in order to perform a standalone testing of the module.

        # test the logger
        # log.debug("testing the logger.....................", msg="some message")
        # log.info("testing the logger.....................", msg="some message")
        # log.warn("testing the logger.....................", msg="some message")
        # log.error("testing the logger.....................", msg="some message")
        # log.exception("testing the logger.....................", msg="some message")
        from dummy_device import DummyDevice
        device = DummyDevice(log=log)
        stat_mgr = OpenOltStatisticsMgr(device,log)

        # Send a test value
        # 128
        for i in range(0,3):
            port_stats = get_port_stats(intf_id=i + 128, value=random.randint(100, 1000))
            stat_mgr.port_statistics_indication(port_stats)

        # build the pon port sets
        for i in range(0,15):
            intf_id = 0x2 << 28 | i
            port_stats = get_port_stats(intf_id=intf_id, value=random.randint(100, 1000))
            stat_mgr.port_statistics_indication(port_stats)

        foo = True

        # asjson = json.dumps(pon_metrics_config,indent=2,sort_keys=True)
        print("Done")
    except Exception as err1:
        print(err1.message)

    sys.exit()




if __name__ == '__main__':

    main()