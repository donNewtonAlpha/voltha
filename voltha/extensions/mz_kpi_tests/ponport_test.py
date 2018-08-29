


# from voltha.protos.events_pb2 import KpiEvent, MetricValuePairs
# from voltha.protos.events_pb2 import KpiEventType
# import voltha.adapters.openolt.openolt_platform as platform
# from voltha.extensions.kpi.olt.olt_pm_metrics import OltPmMetrics
#



import yaml
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
from voltha.extensions.mz_kpi_tests.nni_port import NniPort


from voltha.extensions.mz_kpi_tests.map2test import map2Test
from common.structlog_setup import setup_logging, update_logging




def load_config():
    path = os.getcwd()
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, "mztest_logging.yml")
    path = os.path.abspath(path)
    with open(path) as fd:
        config = yaml.load(fd)
    return config



def main():
    """
    This just test what nick did in the BAL driver to create a PON ID

    :return:
    """

    try:
        config = load_config()
        instance_id = os.environ.get('INSTANCE_ID', os.environ.get('HOSTNAME', '1'))
        log = setup_logging(config.get('logging', {}), "main")

        for i in range(0,16):
            val =  0x2 << 28 | i
            print(val)


        print("Done")
    except Exception as err1:
        print(err1.message)

    sys.exit()




if __name__ == '__main__':

    main()