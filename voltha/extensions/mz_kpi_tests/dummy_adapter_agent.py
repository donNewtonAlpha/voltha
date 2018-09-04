


class DummyAdapterAgent(object):

    def __init__(self, device, adapter_name, log):
        self.adapter_name = adapter_name
        self.log = log
        self.device = device

    # ~~~~~~~~~~~~~~~~~~~ Handling KPI metric submissions ~~~~~~~~~~~~~~~~~~~~~

    def submit_kpis(self, kpi_event_msg):
        try:
            # assert isinstance(kpi_event_msg, KpiEvent)
            self.log.info("Adapter agent is the DummyAgent .  Logging the data: ", kpi_event=kpi_event_msg)
        except Exception as e:
            self.log.exception('failed-kpi-submission',
                               type=type(kpi_event_msg))

    def update_device_pm_config(self, device_pm_config, init=False):
        self.log.info("Update of pm config does nothing in the dummy agent.")

    def get_device(self, device_id):
        # return self.root_proxy.get('/devices/{}'.format(device_id))
        device = self.device
        return device


