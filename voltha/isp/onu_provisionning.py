import time
import structlog
import grpc
import requests
log = structlog.get_logger()
from voltha.protos.bbf_fiber_base_pb2 import VOntaniConfig, VEnetConfig
from voltha.protos.bbf_fiber_tcont_body_pb2 import TcontsConfigData
from voltha.protos.bbf_fiber_gemport_body_pb2 import GemportsConfigData
from voltha.protos.voltha_pb2 import VolthaGlobalServiceStub

#TODO: make it clean and dicover the port through service or something
try:
    channel = grpc.insecure_channel('localhost:50556')
    stub = VolthaGlobalServiceStub(channel)
except Exception as e:
    log.error('Grpc stub preparation error', error=e)
activeOnus = []


sleep = 15
DO_ONOS_CONFIG_TOO = True

def add_subscriber(dpid, oltTag, oltDeviceId, onuSerialNumber, id, trafficDescriptor, channelPartition, channelPair, username,
                   tcont, enet, gem, port, vlan):
    log.info("FOUNDRY Configuring subscriber with ONU {} and VLAN {} on OLT {} ({})".format(onuSerialNumber, vlan, oltDeviceId,
                                                                                    oltTag))

    create_v_ont_anis(onuSerialNumber, id, username, channelPartition, channelPair)
    time.sleep(sleep)
    createTcont(tcont, username, trafficDescriptor, 1023 + id)
    time.sleep(sleep)
    createVEnets(enet, username)
    time.sleep(sleep)
    createGemPort(gem, enet, tcont, 1023 + id)
    if DO_ONOS_CONFIG_TOO:
        time.sleep(sleep)
        onosSubscriber(dpid, port, vlan)

    log.info("Subscriber with ONU {} and VLAN {} configured\n".format(onuSerialNumber, vlan))
    # self.activeOnu +=1

def create_v_ont_anis(serialNumber, id, username, channelPartition, channelPair):

    v_ont_ani_request = VOntaniConfig()
    log.debug("FOUNDRY-creating-vont-config", config=v_ont_ani_request, username=username, serialNumber=serialNumber,
              channelPair=channelPair, channelPartition=channelPartition, onu_id=id)

    try:
        v_ont_ani_request.interface.name = username
        v_ont_ani_request.interface.description = "v_ont for {}".format(username)
        v_ont_ani_request.interface.type = "v_ontani"
        v_ont_ani_request.interface.enabled = True
        v_ont_ani_request.data.parent_ref = channelPartition
        v_ont_ani_request.data.expected_serial_number = serialNumber
        v_ont_ani_request.data.preferred_chanpair = channelPair
        v_ont_ani_request.data.onu_id = id
        v_ont_ani_request.name = username

        log.debug("FOUNDRY-vont-config-prepared", config=v_ont_ani_request, username=username, serialNumber=serialNumber,
                  channelPair=channelPair, channelPartition=channelPartition, onu_id=id)
    except Exception as e:
        log.error("FOUNDRY-vont-config-error", exception=e, config = v_ont_ani_request, username=username,
                  serialNumber=serialNumber,
                  channelPair=channelPair, channelPartition=channelPartition, onu_id=id)

    try:
        log.debug("FOUNDRY-vont-config-grpc-call", config=v_ont_ani_request, username=username,
                  serialNumber=serialNumber,
                  channelPair=channelPair, channelPartition=channelPartition, onu_id=id)
        stub.CreateVOntani(v_ont_ani_request)
        log.info("FOUNDRY-autodetection-vont-created", config=v_ont_ani_request, username=username,
                  serialNumber=serialNumber,
                  channelPair=channelPair, channelPartition=channelPartition, onu_id=id)
    except Exception as e:
        log.error("FOUNDRY-vont-config-grpc-call-error", exception=e, config=v_ont_ani_request, username=username,
                  serialNumber=serialNumber,
                  channelPair=channelPair, channelPartition=channelPartition, onu_id=id)



def createTcont(name, username, trafficDescriptor, id):
    tcont_request = TcontsConfigData()
    log.debug("FOUNDRY-creating-tcont-config", config=tcont_request, name=name, username=username,  alloc_id=id)

    try:
        tcont_request.name = name
        tcont_request.interface_reference = username
        tcont_request.traffic_descriptor_profile_ref = trafficDescriptor
        tcont_request.alloc_id = id

        log.debug("FOUNDRY-tcont-config-prepared", config=tcont_request, name=name, username=username, alloc_id=id)
    except Exception as e:
        log.error("FOUNDRY-tcont-config-error", exception=e, config=tcont_request, name=name, username=username, alloc_id=id)

    try:
        log.debug("FOUNDRY-tcont-grpc-call", config=tcont_request, name=name, username=username, alloc_id=id)
        stub.CreateTcontsConfigData(tcont_request)
        log.info("FOUNDRY-autodetection-tcont-created", config=tcont_request, name=name, username=username, alloc_id=id)
    except Exception as e:
        log.error("FOUNDRY-tcont-config-grpc-call-error", exception=e, config=tcont_request, name=name, username=username, alloc_id=id)



def createVEnets(name, username):

    venet_request = VEnetConfig()
    log.debug("FOUNDRY-creating-venet-config", config=venet_request, name=name, username=username)

    try:
        venet_request.interface.name = name
        venet_request.interface.description = "Ethernet port - {}".format(name)
        venet_request.interface.type = "v-enet"
        venet_request.interface.enabled = True
        venet_request.data.v_ontani_ref = username
        venet_request.name = name

        log.debug("FOUNDRY-venet-config-prepared", config=venet_request, name=name, username=username)
    except Exception as e:
        log.error("FOUNDRY-venet-config-error", exception=e, config=venet_request, name=name, username=username,
                  alloc_id=id)

    try:
        log.debug("FOUNDRY-tcont-grpc-call", config=venet_request, name=name, username=username)
        stub.CreateTcontsConfigData(venet_request)
        log.info("FOUNDRY-autodetection-venet-created", config=venet_request, name=name, username=username, alloc_id=id)
    except Exception as e:
        log.error("FOUNDRY-venet-config-grpc-call-error", exception=e, config=venet_request, name=name,
                  username=username)




def createGemPort(name, enet, tcont, id):

    gem_port_request = GemportsConfigData()
    log.debug("FOUNDRY-creating-gemport-config", config=gem_port_request, name=name, enet=enet, tcont=tcont, gemPortId=id)

    try:
        gem_port_request.name = name
        gem_port_request.itf_ref = enet
        gem_port_request.traffic_class = 2
        gem_port_request.aes_indicator = True
        gem_port_request.tcont_ref = tcont
        gem_port_request.gemport_id = id

        log.debug("FOUNDRY-gemport-config-prepared", config=gem_port_request, name=name, enet=enet, tcont=tcont, gemPortId=id)
    except Exception as e:
        log.error("FOUNDRY-gemport-config-error", exception=e, config=gem_port_request, name=name, enet=enet, tcont=tcont, gemPortId=id)

    try:
        log.debug("FOUNDRY-gemport-grpc-call", config=gem_port_request, name=name, enet=enet, tcont=tcont, gemPortId=id)
        stub.CreateGemportsConfigData(gem_port_request)
        log.info("FOUNDRY-autodetection-gemport-created", config=gem_port_request, name=name, enet=enet, tcont=tcont, gemPortId=id)
    except Exception as e:
        log.error("FOUNDRY-gemport-config-grpc-call-error", exception=e, config=gem_port_request, name=name, enet=enet, tcont=tcont, gemPortId=id)


def onosSubscriber(oltDpid, port, ctag):
    r = requests.post('http://onos:8181/onos/olt/oltapp/of%3A{}/{}/{}'.format(oltDpid, port, ctag))
    if r.status_code != 200:
        log.error("Error {} on ONOS add subscriber POST".format(r.status_code))
        exit()
    else:
        log.info("Subscriber {} provisionned in ONOS".format(ctag))