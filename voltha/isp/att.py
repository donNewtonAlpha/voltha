from voltha.isp.onu_provisionning import add_subscriber
from threading import Lock
import requests
import json
import structlog

activeOnus = []
lock = Lock()
log = structlog.get_logger()

DEFAULT_DPID = "0001000000000001"

def new_onu_detected(onuData):


    onuSerialNumber = onuData['serial_number']
    deviceId = onuData['device_id']
    ponId = onuData['pon_id']
    #TODO: keep it / remove it ?
    oltMessage = onuData['olt_event_message']

    oltParentId = DEFAULT_DPID
    oltTag = 'defaultTag'

    try :
        devices = json.loads(requests.get('127.0.0.1:8882/api/v1/devices'))['items']
        for device in devices:
            if device['id'] == deviceId:
                oltParentId = device['parent_id']
                oltTag = device['host_and_port'].split(':')[0].split('.')[3]

    #Modification of dpid to match ONOS : bug
    #TODO: fix the source of the bug
        oltParentId[3] = '0'
    except Exception as e:
        log.error('att onu detection error: preparation', e)
        return

    with lock:
        if onuSerialNumber not in activeOnus:
            try:
                add_subscriber_on_pon(deviceId, oltParentId, oltTag, onuSerialNumber, ponId, len(activeOnus) + 1)
                activeOnus.append(onuSerialNumber)
            except Exception as e:
                log.error('att onu detection error: provisionning calls', e)




def add_subscriber_on_pon(oltDeviceId, dpid, oltTag, onuSerialNumber, ponId, onuId):



    channelPartition = getChannelPartition(oltTag, ponId)
    channelPair = getChannelPair(oltTag, ponId)
    trafficDescriptor = getTrafficDescriptor(oltTag, ponId)
    username = getUsername(oltTag, onuId)
    tcont = getTcont(oltTag, onuId)
    enet = getEnet(oltTag, onuId)
    gem = getGem(oltTag, onuId)
    vlan = 19 + onuId
    port = 256 + onuId

    add_subscriber(dpid, oltTag, oltDeviceId, onuSerialNumber, onuId, trafficDescriptor, channelPartition, channelPair, username,
                        tcont, enet, gem, port, vlan)

    onuId += 1
        
def getChannelGroup(tag, ponId):
    return "ChannelGroup{}-{}".format(tag, ponId)

def getChannelPartition(tag, ponId):
    return "channelPartition{}-{}".format(tag, ponId)

def getChannelPair(tag, ponId):
    return "PonPort{}-{}".format(tag, ponId)

def getChannelTermination(tag, ponId):
    return "PonPort{}-{}".format(tag, ponId)

def getTrafficDescriptor(tag, ponId):
    return "TD{}-{}".format(tag, ponId)

def getUsername(tag,  onuId):
    return "User{}-{}".format(tag, onuId)

def getEnet(tag, onuId):
    return "Enet{}-{}".format(tag, onuId)

def getTcont(tag, onuId):
    return "TCONT{}-{}".format(tag, onuId)

def getGem(tag, onuId):
    return "GemPort{}-{}".format(tag, onuId)