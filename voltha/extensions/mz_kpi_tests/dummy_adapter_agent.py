


class DummyAdapterAgent(object):

    def __init__(self, adapter_name, log):
        self.adapter_name = adapter_name
        self.log = log

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


