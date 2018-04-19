import time
import structlog
import voltha.isp.voltha_config_calls as config

activeOnus = []


log = structlog.get_logger()
sleep = 15

def add_subscriber(dpid, oltTag, oltDeviceId, onuSerialNumber, id, trafficDescriptor, channelPartition, channelPair, username,
                   tcont, enet, gem, port, vlan):
    log.info("FOUNDRY Configuring subscriber with ONU {} and VLAN {} on OLT {} ({})".format(onuSerialNumber, vlan, oltDeviceId,
                                                                                    oltTag))

    config.create_v_ont_anis(onuSerialNumber, id, username, channelPartition, channelPair)
    time.sleep(sleep)
    config.createTcont(tcont, username, trafficDescriptor, 1023 + id)
    time.sleep(sleep)
    config.createVEnets(enet, username)
    time.sleep(sleep)
    config.createGemPort(gem, enet, tcont, 1023 + id)
    time.sleep(sleep)
    config.onosSubscriber(dpid, port, vlan)

    log.info("Subscriber with ONU {} and VLAN {} configured\n".format(onuSerialNumber, vlan))
    # self.activeOnu +=1