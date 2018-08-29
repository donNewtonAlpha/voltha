


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
from voltha.extensions.mz_kpi_tests.pon_port import PonPort


from voltha.extensions.mz_kpi_tests.map2test import map2Test
from common.structlog_setup import setup_logging, update_logging



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
            return port
        else:
            # PON ports require a different configuration
            curport = 536870913
            curport += port_num
            port_olt = Port(port_no=curport, type=Port.PON_OLT,
                        label=label,
                        admin_state=AdminState.ENABLED,
                        oper_status=OperStatus.ACTIVE)

            # port = {"port_no": , "onu_ids":[], "onu_id": "xxxxx", "port": port_olt}
            port = OnuPort(port_no=curport, onu_id="xxxx", port=port_olt, onu_ids=[])
            foo = port

            return port_olt

    except Exception as err:
        foo = err.message
        raise Exception(err)

def build_port_object(port_num, type="nni"):
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
                'port_num': port_num,
            }
            nni_port = NniPort
            port = nni_port(**kwargs)
            return port

        else:   #default to pon
            # PON ports require a different configuration
            port_olt = None

            return port_olt

    except Exception as err:
        foo = err.message
    raise Exception(err)

def update_port_data(port,log, datadict={} ):
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

def load_config():
    path = os.getcwd()
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, "mztest_logging.yml")
    path = os.path.abspath(path)
    with open(path) as fd:
        config = yaml.load(fd)
    return config

def get_port_stat_names():

    pm_names = {
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

    return pm_names

def main():

    try:
        config = load_config()
        instance_id = os.environ.get('INSTANCE_ID', os.environ.get('HOSTNAME', '1'))
        log = setup_logging(config.get('logging', {}), "main")
        stat = {'intf_id': 536870913,'tx_bytes': 428,'tx_packets': 2,'tx_mcast_packets': 2,'timestamp': 1534857356}

        # kwargs = {
        #     'port_no': 0,
        #     'intf_id': 0,
        #     'onu_ids' : []
        # }
        # nni_port = NniPort(**kwargs)




        device_id = "00017579ccb9b"
        # stats = {'tx_bcast_packets': 0L, 'rx_packets': 86L, 'rx_bytes': 7548L, 'tx_ucast_packets': 0L, 'rx_crc_errors': 0L,
        #  'rx_error_packets': 0L, 'tx_error_packets': 0L, 'tx_mcast_packets': 0L, 'rx_bcast_packets': 0L,
        #  'rx_ucast_packets': 0L, 'bip_errors': 0L, 'tx_bytes': 0L, 'tx_packets': 0L, 'rx_mcast_packets': 86L}
        # nni-ports = [4]
        # pon-ports = [5]

        # agent = AdapterAgentAlt("simulated_onu", SimulatedOltAdapter)

        """
        Configure the nni and pon ports:
        The Model is that a given NNI port is the parent of a set of PON ports
        for our purposes ALL PONs are associated with NNI intf_id = 128.
        """

        nni_ports = []
        for i in range(0,1):
            nni_ports.append(build_port(port_num=i, type="ETHERNET"))
        pon_ports = []
        for i in range(0,5):
            pon_ports.append(build_port(port_num=i, type="OLT_PON"))


        """ 
        In order to make all this work the template must have a real nni or pon object.
        This opject gets updated with the actual data change, once that occurs the the processing routine
        is called:  collect_and_publish_metrics
        
        collect_and_publish_metrics iterates through the objects (nni/pon port) extracts the new data and maps
        that data into the config.
        
        The Port objects reflect the data rquired by the proto, so they must be kept in synch.
        
        """

        # Build the list of port objects
        nni_ports = []
        for i in range(0,1):
            nni_port = build_port_object(i)

            # create the dummy data
            stats = {'tx_bcast_packets': 5000, 'rx_packets': 5000, 'rx_bytes': 7548, 'tx_ucast_packets': 5000, 'rx_crc_errors':2,
             'rx_error_packets': 100, 'tx_error_packets': 500, 'tx_mcast_packets': 5000, 'rx_bcast_packets': 6000,
             'rx_ucast_packets': 12000, 'bip_errors': 50, 'tx_bytes': 800000, 'tx_packets': 70000, 'rx_mcast_packets': 20000}
            update_port_data(port=nni_port,datadict=stats,log=log)
            nni_ports.append(nni_port)

        pon_ports = []
        kwargs = {
            'nni-ports': nni_ports,
            'pon-ports': pon_ports
        }

        oltmetrics = OltPmMetricsAlt(adapter_agent=None, device_id=device_id,
                                     grouped=True, freq_override=False, **kwargs)
        # change the structs

        oltmetrics.nni_pm_names = get_port_stat_names()
        oltmetrics.nni_metrics_config = {m: PmConfig(name=m, type=t, enabled=True)
                                   for (m, t) in oltmetrics.nni_pm_names}

        oltmetrics.pon_pm_names = get_port_stat_names()
        oltmetrics.pon_metrics_config = {m: PmConfig(name=m, type=t, enabled=True)
                                   for (m, t) in oltmetrics.pon_pm_names}

        # pon_metrics_config = buildMetrics()
        # pm_configs = oltmetrics.make_proto(pm_config=oltmetrics.nni_metrics_config)
        pm_configs = oltmetrics.make_proto(pm_config=None)

        print(pm_configs)
        # test the metrics collection
        collected = oltmetrics.collect_metrics()

        metrics = {}
        # metrics = {'rx_packets': 0L, 'rx_bytes': 0L, 'oper_status': 4, 'admin_state': 3, 'tx_bytes': 0L, 'tx_packets': 0L, 'port_no': 0}
        # metrics = {'rx_packets': 0, 'rx_bytes': 0, 'oper_status': 4, 'admin_state': 3, 'tx_bytes': 0,'tx_packets': 0, 'port_no': 0}

        # oltmetrics.publish_metrics(metrics=metrics)
        oltmetrics.collect_and_publish_metrics()


        # asjson = json.dumps(pon_metrics_config,indent=2,sort_keys=True)
        print("Done")
    except Exception as err1:
        print(err1.message)

    sys.exit()




if __name__ == '__main__':

    main()