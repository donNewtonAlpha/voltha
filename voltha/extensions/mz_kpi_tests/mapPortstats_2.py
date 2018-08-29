


# from voltha.protos.events_pb2 import KpiEvent, MetricValuePairs
# from voltha.protos.events_pb2 import KpiEventType
# import voltha.adapters.openolt.openolt_platform as platform
# from voltha.extensions.kpi.olt.olt_pm_metrics import OltPmMetrics
#



import yaml
import sys,os, json
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

"""
This is the slimmed down version....  Much closer to working

"""


def test_ports_statistics_kpis():
    """

    20180827:
    the current indicators coming from the BAL drive loop through all the nni ports 128 - 132 and send up the
    the stats.

    The PON ports are collected by looping through 0 - 15 and sending the inidicators for each one. This is done

    In actual use  0 - 15 are collected with no assigment to any given NNI.   In actual use for the short to intermediate
    term 0 - 15 are always associated with NNI intf_id 128.  This means that the PON ports will be 'nested' under
    the NNI in order to conform to the KPI template models

    :param port_stats:
    :return:
    """
    pm_data = {}
    pm_data["rx_bytes"] = 0
    pm_data["rx_packets"] = 0
    pm_data["rx_ucast_packets"] = 0
    pm_data["rx_mcast_packets"] = 0
    pm_data["rx_bcast_packets"] = 0
    pm_data["rx_error_packets"] = 0
    pm_data["tx_bytes"] = 0
    pm_data["tx_packets"] = 0
    pm_data["tx_ucast_packets"] = 0
    pm_data["tx_mcast_packets"] = 0
    pm_data["tx_bcast_packets"] = 0
    pm_data["tx_error_packets"] = 0
    pm_data["rx_crc_errors"] = 0
    pm_data["bip_errors"] = 0

    prefix = 'voltha.openolt.{}'.format(12345)

    # Ignore all but 128 since that is the only one currently having pon ports associated with it
    #

    prefixes = {
        prefix + '.nni.{}'.format(128): MetricValuePairs(
            metrics=pm_data)
    }

    foo = KpiEventType.slice
    kpi_event = KpiEvent(
        type=KpiEventType.slice,
        ts=1525376128.0,
        prefixes=prefixes)
    print(kpi_event)
    foo = True
    return

def init_ports(type="nni", device_id=12345, log=None):
    """

    :param type:
    :param device_id:
    :param log:
    :return:
    """
    try:
        if type == "nni":
            nni_ports = []
            for i in range(0, 1):
                nni_port = build_port_object(i, type='nni', device_id=device_id)

                # create the dummy data
                stats = {'tx_bcast_packets': 5000, 'rx_packets': 5000, 'rx_bytes': 7548, 'tx_ucast_packets': 5000,
                         'rx_crc_errors': 2,
                         'rx_error_packets': 100, 'tx_error_packets': 500, 'tx_mcast_packets': 5000, 'rx_bcast_packets': 6000,
                         'rx_ucast_packets': 12000, 'bip_errors': 50, 'tx_bytes': 800000, 'tx_packets': 70000,
                         'rx_mcast_packets': 20000}
                update_port_data(port=nni_port, datadict=stats, log=log)
                nni_ports.append(nni_port)
            return nni_ports
        elif type == "pon":
            pon_ports = []
            for i in range(0, 15):
                pon_port = build_port_object(i, type="pon", device_id=device_id)

                # create the dummy data
                stats = {'tx_bcast_packets': 5000, 'rx_packets': 5000, 'rx_bytes': 7548, 'tx_ucast_packets': 5000,
                         'rx_crc_errors': 2,
                         'rx_error_packets': 100, 'tx_error_packets': 500, 'tx_mcast_packets': 5000,
                         'rx_bcast_packets': 6000,
                         'rx_ucast_packets': 12000, 'bip_errors': 50, 'tx_bytes': 800000, 'tx_packets': 70000,
                         'rx_mcast_packets': 20000}
                update_port_data(port=pon_port, datadict=stats, log=log)
                pon_ports.append(pon_port)
            return pon_ports
        else:
            raise Exception("Unmapped port type requested = " + type)


    except Exception as err:
        raise Exception(err)

def build_port_object(port_num, type="nni", device_id=1234):
    try:
        """ This builds a port object wich is passed as to the """
        # Build the label
        from voltha.extensions.mz_kpi_tests.nni_port import NniPort

        label = 'NNI port {}'.format(port_num)

        if type == "nni":
            # Expected kwargs
            # self._label = kwargs.pop('label', 'NNI port {}'.format(self._port_no))
            # self._mac_address = kwargs.pop('mac_address', '00:00:00:00:00:00')
            # # TODO: Get with JOT and find out how to pull out MAC Address via NETCONF
            # # TODO: May need to refine capabilities into current, advertised, and peer
            #
            # self._ofp_capabilities = kwargs.pop('ofp_capabilities', OFPPF_100GB_FD | OFPPF_FIBER)
            # self._ofp_state = kwargs.pop('ofp_state', OFPPS_LIVE)
            # self._current_speed = kwargs.pop('current_speed', OFPPF_100GB_FD)
            # self._max_speed = kwargs.pop('max_speed', OFPPF_100GB_FD)
            # self._device_port_no = kwargs.pop('device_port_no', self._port_no)


            # port num is the only required item

            kwargs = {
                'port_no': port_num,
                'intf_id': port_num + 128,
                "device_id": device_id
            }
            nni_port = NniPort
            port = nni_port(**kwargs)
            return port

        elif type == "pon":
            # PON ports require a different configuration
            kwargs = {
                'port_no': port_num,
                'intf_id': 0x2 << 28 | port_num,
                'pon-id': 0x2 << 28 | port_num,
                "device_id": device_id
            }
            pon_port = PonPort
            port = pon_port(**kwargs)
            return port

        else:
            raise Exception("Unknown port type")

    except Exception as err:
        foo = err.message
    raise Exception(err)

def update_port_data(port,log, datadict={} ):
    """

    :param port:
    :param log:
    :param datadict:
    :return:
    """
    try:
        if isinstance(port,NniPort):
            for k, v in datadict.items():
                if hasattr(port,k):
                    setattr(port,k,v)
        elif isinstance(port,PonPort):
            for k, v in datadict.items():
                if hasattr(port,k):
                    setattr(port,k,v)
        else:
            raise Exception("Must be either PON or NNI port.")
    except Exception as err:
        log.exception("Caught error updating port data: ", errormsg=err.message)
        raise Exception(err)

def load_config():
    path = os.getcwd()
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, "mztest_logging.yml")
    path = os.path.abspath(path)
    with open(path) as fd:
        config = yaml.load(fd)
    return config

def get_openolt_port_pm_names():

    nni_pm_names = {
        ('admin_state', PmConfig.STATE),
        ('oper_status', PmConfig.STATE),
        ('intf_id',  PmConfig.STATE),
        ('port_no', PmConfig.GUAGE),
        ('rx_bytes', PmConfig.COUNTER),
        ('rx_packets', PmConfig.COUNTER),
        ('rx_ucast_packets', PmConfig.COUNTER),
        ('rx_mcast_packets', PmConfig.COUNTER),
        ('rx_bcast_packets', PmConfig.COUNTER),
        ('rx_error_packets', PmConfig.COUNTER),
        ('tx_bytes', PmConfig.COUNTER),
        ('tx_packets', PmConfig.COUNTER),
        ('tx_ucast_packets', PmConfig.COUNTER),
        ('tx_mcast_packets', PmConfig.COUNTER),
        ('tx_bcast_packets', PmConfig.COUNTER),
        ('tx_error_packets', PmConfig.COUNTER)
    }
    pon_pm_names = nni_pm_names      # for openolt the same structure is being used.
    pon_pm_names_orig = {
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
    # Build a dict for the names.  The caller will index to the correct values
    names_dict = {"nni_pm_names":nni_pm_names,
                  "pon_pm_names": pon_pm_names,
                  "pon_pm_names_orig": pon_pm_names_orig,
                  "onu_pm_names": onu_pm_names,
                  "gem_pm_names": gem_pm_names,

                  }

    return names_dict

def main():

    try:
        config = load_config()
        instance_id = os.environ.get('INSTANCE_ID', os.environ.get('HOSTNAME', '1'))
        log = setup_logging(config.get('logging', {}), "main")

        device_id = "00017579ccb9b"

        """
        Configure the nni and pon ports:
        The Model is that a given NNI port is the parent of a set of PON ports
        for our purposes ALL PONs are associated with NNI intf_id = 128.

        In order to make all this work the template must have a real nni or pon object.
        This opject gets updated with the actual data change, once that occurs the the processing routine
        is called:  collect_and_publish_metrics
        
        collect_and_publish_metrics iterates through the objects (nni/pon port) extracts the new data and maps
        that data into the config.
        
        The Port objects reflect the data rquired by the proto, so they must be kept in synch.
        
        """

        # Build the list of port objects

        nni_ports = init_ports(type='nni', device_id=device_id, log=log)
        pon_ports = init_ports(type='pon', device_id=device_id, log=log)

        # nni_ports = []
        # for i in range(0,1):
        #     nni_port = build_port_object(i, type='nni', device_id=device_id)
        #
        #     # create the dummy data
        #     stats = {'tx_bcast_packets': 5000, 'rx_packets': 5000, 'rx_bytes': 7548, 'tx_ucast_packets': 5000, 'rx_crc_errors':2,
        #      'rx_error_packets': 100, 'tx_error_packets': 500, 'tx_mcast_packets': 5000, 'rx_bcast_packets': 6000,
        #      'rx_ucast_packets': 12000, 'bip_errors': 50, 'tx_bytes': 800000, 'tx_packets': 70000, 'rx_mcast_packets': 20000}
        #     update_port_data(port=nni_port,datadict=stats,log=log)
        #     nni_ports.append(nni_port)
        #
        # pon_ports = []
        # for i in range(0,15):
        #     pon_port = build_port_object(i, type="pon",device_id=device_id)
        #
        #     # create the dummy data
        #     stats = {'tx_bcast_packets': 5000, 'rx_packets': 5000, 'rx_bytes': 7548, 'tx_ucast_packets': 5000, 'rx_crc_errors':2,
        #      'rx_error_packets': 100, 'tx_error_packets': 500, 'tx_mcast_packets': 5000, 'rx_bcast_packets': 6000,
        #      'rx_ucast_packets': 12000, 'bip_errors': 50, 'tx_bytes': 800000, 'tx_packets': 70000, 'rx_mcast_packets': 20000}
        #     update_port_data(port=pon_port,datadict=stats,log=log)
        #     pon_ports.append(pon_port)


        kwargs = {
            'nni-ports': nni_ports,
            'pon-ports': pon_ports
        }

        oltmetrics = OltPmMetrics(adapter_agent=None, device_id=device_id,
                                     grouped=True, freq_override=False, **kwargs)
        # change the structs

        oltmetrics.nni_pm_names = (get_openolt_port_pm_names())['nni_pm_names']
        oltmetrics.nni_metrics_config = {m: PmConfig(name=m, type=t, enabled=True)
                                   for (m, t) in oltmetrics.nni_pm_names}

        oltmetrics.pon_pm_names = (get_openolt_port_pm_names())['pon_pm_names']
        oltmetrics.pon_metrics_config = {m: PmConfig(name=m, type=t, enabled=True)
                                   for (m, t) in oltmetrics.pon_pm_names}

        pm_configs = oltmetrics.make_proto(pm_config=None)
        # print(pm_configs)
        # test the metrics collection
        # collected = oltmetrics.collect_metrics()

        metrics = {}
        # oltmetrics.publish_metrics(metrics=metrics)
        oltmetrics.collect_and_publish_metrics()

        # now test alternate transform.
        test_ports_statistics_kpis()


        # asjson = json.dumps(pon_metrics_config,indent=2,sort_keys=True)
        print("Done")
    except Exception as err1:
        print(err1.message)

    sys.exit()




if __name__ == '__main__':

    main()