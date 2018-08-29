
from voltha.extensions.mz_kpi_tests.dummy_adapter_agent import DummyAdapterAgent

class DummyDevice(object):
    def __init__(self, adapter=None, device_id='12345', log=None):
        self.adapter = adapter
        self.adapter_agent = DummyAdapterAgent("dummy_adapter",log )
        self.device_id=device_id
