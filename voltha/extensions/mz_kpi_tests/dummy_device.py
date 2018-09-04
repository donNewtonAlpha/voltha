
from voltha.extensions.mz_kpi_tests.dummy_adapter_agent import DummyAdapterAgent

class DummyDevice(object):
    def __init__(self, adapter=None, device_id='dummy_12345',
                 logical_device_id='logical12345',log=None):
        self.adapter = adapter
        self.adapter_agent = DummyAdapterAgent(self, "dummy_adapter",log )
        self.device_id=device_id
        self.logical_device_id = device_id
        self.serial_number = "123-345-678"
