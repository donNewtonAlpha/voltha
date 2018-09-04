
import yaml
import sys,os, json, random
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
from twisted.python.failure import Failure
from twisted.internet.task import LoopingCall

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

loopTimes = 4
_loopCounter = 0

def load_config():
    path = os.getcwd()
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, "mztest_logging.yml")
    path = os.path.abspath(path)
    with open(path) as fd:
        config = yaml.load(fd)
    return config


def get_port_stats(intf_id, value=0):

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

@inlineCallbacks
def start_reactor(log):
        from twisted.internet import reactor
        reactor.callWhenRunning(
            lambda: log.info('twisted-reactor-started'))

        reactor.run()
        yield "done"

def ind_dataloop(stat_mgr):

    ethcount = 0
    for i in range(0, 1):
        port_stats = get_port_stats(intf_id=i + 128, value=random.randint(100, 1000))
        stat_mgr.port_statistics_indication(port_stats)
        ethcount += 1

    # build the pon port sets
    poncount = 0
    for i in range(0, 16):
        intf_id = 0x2 << 28 | i
        port_stats = get_port_stats(intf_id=intf_id, value=random.randint(100, 1000))
        stat_mgr.port_statistics_indication(port_stats)
        poncount += 1
    print("Populating stats data: {} Ethernet ports, {} Pon ports ".format(ethcount, poncount))
def print_loop():
    print("a second has passed")

    reactor.stop()

@inlineCallbacks
def my_callbacks():

    global _loopCounter

    if _loopCounter < loopTimes:
        print 'first callback'
        result = yield 1 # yielded values that aren't deferred come right back

        print 'second callback got', result
        d = Deferred()
        reactor.callLater(5, d.callback, 2)
        result = yield d # yielded deferreds will pause the generator

        print 'third callback got', result # the result of the deferred

        d = Deferred()
        reactor.callLater(5, d.errback, Exception(3))

        try:
            yield d
        except Exception, e:
            result = e

        print 'fourth callback got', repr(result) # the exception from the deferred
    lc.stop()

def cbLoopDone(result):
    """
    Called when loop was stopped with success.
    """
    print("Loop done.")
    reactor.stop()


def ebLoopFailed(failure):
    """
    Called when loop execution failed.
    """
    print(failure.getBriefTraceback())
    reactor.stop()

def main():

    try:
        config = load_config()
        instance_id = os.environ.get('INSTANCE_ID', os.environ.get('HOSTNAME', '1'))
        log = setup_logging(config.get('logging', {}), "main")

        # random.seed(42)

        # print(random.sample(range(1000),k=10))
        # print(random.randint(100,1000))
        #
        #
        #
        port_stats = get_port_stats(random.randint(100,1000))
        print("port stats :")
        print(port_stats)
        foo = port_stats
        device_id = "00017579ccb9b"

        # Bring in a dummy device.  This will avoid any dependencies on the underlying
        # sysem in order to perform a standalone testing of the module.


        from dummy_device import DummyDevice
        device = DummyDevice(log=log)

        kargs = {"metrics_init" : False}
        kargs = {}
        stat_mgr = OpenOltStatisticsMgr(device,log, **kargs)

        # call the statistics manager to init the collection loop
        stat_mgr.init_pm_metrics()

        # set up the loop and start


        lc = LoopingCall(ind_dataloop, stat_mgr)
        lc.start(1.0)

        # lc = LoopingCall(my_callbacks)
        # reactor.callWhenRunning(my_callbacks)
        # lc.start(1.0)

        # Add callbacks for stop and failure.
        # loopDeferred.addCallback(cbLoopDone)
        # loopDeferred.addErrback(ebLoopFailed)
        reactor.run()

        # asjson = json.dumps(pon_metrics_config,indent=2,sort_keys=True)
        print("Done")
    except Exception as err1:
        print(err1.message)
        log.error("Error = ", errmsg=err1.message)
        foo = True

    sys.exit()




if __name__ == '__main__':

    main()