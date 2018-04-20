from voltha.isp.onu_provisionning import add_subscriber
from voltha.registry import registry
from threading import Lock, Thread
import requests
import json
import structlog

#TODO: make obsolete, get it from the database proxy
activeOnus = []
#TODO : Make all this asynchronous
lock = Lock()
log = structlog.get_logger()

DEFAULT_DPID = '0001000000000001'

core = registry('core')
proxy = core.get_proxy('/')

def new_onu_detected(onuData):


    onuSerialNumber = onuData['serial_number']
    deviceId = onuData['device_id']
    ponId = onuData['pon_id']
    #TODO: keep it / remove it ?
    oltMessage = onuData['olt_event_message']

    oltParentId = DEFAULT_DPID
    oltTag = 'defaultTag'

    log.info('FOUNDRY-onu-data-preparation-before-device-check', onuSerialNumber=onuSerialNumber, deviceId=deviceId,
             ponId = ponId, oltParentId=oltParentId, oltTag=oltTag, rawmessage=oltMessage)

    try :
        devices = proxy.get('/devices')
        log.info('FOUNDRY-getting-devices-from-storage', devicesStored=devices)

        for device in devices:
            log.debug('FOUNDRY-checking-for device', device=device, deviceId=deviceId)

            if device.id == deviceId:
                log.debug('FOUNDRY-device-match', device=device, deviceId=deviceId)
                oltParentId = device.parent_id
                log.debug('FOUNDRY-device-match-dpid-found', device=device, deviceId=deviceId, dpid=oltParentId)
                #TODO: extract tag from channel termination instead
                oltTag = device.host_and_port.split(':')[0].split('.')[3]
                log.debug('FOUNDRY-device-match-tag-found', device=device, deviceId=deviceId, dpid=oltParentId, tag=oltTag)
                #Modification of dpid to match ONOS : bug
                #TODO: fix the source of the bug
                oltParentId = '0000{}'.format(oltParentId[4:])
                log.debug('FOUNDRY-device-dpid-modifcation-for-onos', device=device, deviceId=deviceId, dpid=oltParentId, tag=oltTag)

    except Exception as e:
        log.error('FOUNDRY att onu detection error: preparation', e)
        return

    log.info('FOUNDRY-onu-data-preparation-after-device-check', onuSerialNumber=onuSerialNumber, deviceId=deviceId,
             ponId=ponId, oltParentId=oltParentId, oltTag=oltTag, rawmessage=oltMessage)

    with lock:
        log.debug('FOUNDRY locking before checking activated onus', activeOnus=activeOnus, serial_number=onuSerialNumber)
        if onuSerialNumber not in activeOnus:
            try:
                activeOnus.append(onuSerialNumber)
                t = Thread(target=add_subscriber_on_pon, args=(deviceId, oltParentId, oltTag, onuSerialNumber, ponId, len(activeOnus)))
                t.start()
            except Exception as e:
                log.error('FOUNDRY att onu detection error: provisionning calls', e)
        else:
            log.debug('FOUNDRY-trying-to-activate-already-activated-onu', serialNumber=onuSerialNumber, activatedOnus=activeOnus)




def add_subscriber_on_pon(oltDeviceId, dpid, oltTag, onuSerialNumber, ponId, onuId):
    log.debug('FOUNDRY prepare to add subscriber on pon', deviceId=oltDeviceId, dpid=dpid, oltTag=oltTag, serialNumber=onuSerialNumber, ponId=ponId, onuId=onuId)

    channelPartition = getChannelPartition(oltTag, ponId)
    channelPair = getChannelPair(oltTag, ponId)
    trafficDescriptor = getTrafficDescriptor(oltTag, ponId)
    username = getUsername(oltTag, onuId)
    tcont = getTcont(oltTag, onuId)
    enet = getEnet(oltTag, onuId)
    gem = getGem(oltTag, onuId)
    vlan = 19 + onuId
    port = 256 + onuId

    log.debug('FOUNDRY adding subscriber on pon', deviceId=oltDeviceId, dpid=dpid, oltTag=oltTag,
              serialNumber=onuSerialNumber, ponId=ponId, onuId=onuId, channerPartition=channelPartition,
              channelPair=channelPair, trafficDescriptor=trafficDescriptor, username=username, tcont=tcont,
              enet=enet, gem = gem, vlan=vlan, onuLogivalPort=port)

    add_subscriber(dpid, oltTag, oltDeviceId, onuSerialNumber, onuId, trafficDescriptor, channelPartition, channelPair, username,
                        tcont, enet, gem, port, vlan)


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