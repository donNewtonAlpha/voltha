import requests
import json
import logging


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


volthaIp = '127.0.0.1'

def volthaPost(name, url, data=None):
    r = requests.post(url, json=data)
    if r.status_code != 200:
        log.error("Error {} on {} POST".format(r.status_code, name))
        exit()
    else:
        if r.text:
            response = json.loads(r.text)
            log.debug(response)
        else:
            response = None
        return response

def volthaGet(name, url):
    r = requests.get(url)
    if r.status_code != 200:
        log.error("Error {} on {} GET".format(r.status_code, name))
        exit()
    else:
        if r.text:
            response = json.loads(r.text)
            log.debug(response)
        else:
            response = None
        return response

def preprovision_olt(oltIp, oltMac, driverPort):
    response = volthaPost('preprovsion','http://{}:8882/api/v1/devices'.format(volthaIp),{"type": "asfvolt16_olt", "host_and_port": "{}:{}".format(oltIp, driverPort), "mac-address": oltMac})
    return response['id']

def enable(volthaIp, deviceId):
    volthaPost('enable', 'http://{}:8882/api/v1/devices/{}/enable'.format(volthaIp, deviceId))

def isDeviceEnabled(deviceId):
    data = volthaGet('check enable', 'http://{}:8882/api/v1/devices'.format(volthaIp))
    if not data:
        log.error("Error in enabling device")
        return False
    items = data['items']
    device = None
    for item in items:
        if item['id'] == deviceId:
            device = item
    if not device:
        log.warning("Device not found")
        exit()
    log.debug(device)
    if device['admin_state'] == 'ENABLED' and device['oper_status'] == 'ACTIVE':
        log.info("Device {} is enabled and active".format(deviceId))
        return True
    return False

def createChannelGroup(name):
    data = {
       "interface": {
         "enabled": True,
         "link_up_down_trap_enable": "TRAP_DISABLED",
         "type": "channelgroup",
         "name": name,
         "description": "Channel Group for {}".format(name)
       },
       "cg_index": 1,
       "data": {
         "polling_period": 100,
         "system_id": "000000",
         "raman_mitigation": "RAMAN_NONE",
       },
       "name": name
     }

    volthaPost('channel group', 'http://{}:8882/api/v1/channel_groups/{}'.format(volthaIp, name), data)
    log.info("Channel group  : {} created".format(name))


def createChannelPartitions(name, channelGroup):
    data = {
      "interface": {
        "name": name,
        "description": "Channel Partition {} from channel group {}".format(name, channelGroup),
        "type": "channelpartition",
        "enabled": True,
        "link_up_down_trap_enable": "TRAP_DISABLED"
      },
      "data": {
        "channelgroup_ref": channelGroup,
        "fec_downstream": False,
        "closest_ont_distance": 0,
        "differential_fiber_distance": 20,
        "authentication_method": "SERIAL_NUMBER",
        "multicast_aes_indicator": False
      },
      "name": name
    }
    volthaPost('channel partitions', 'http://{}:8882/api/v1/channel_partitions/{}'.format(volthaIp, name), data)
    log.info("Channel partition : {} created".format(name))

def createChannelPairs(name, channelPartition, channelGroup):
    data = {
      "interface": {
        "name": name,
        "description": "Channel Pair for {}".format(name),
        "type": "channelpair",
        "enabled": True,
        "link_up_down_trap_enable": "TRAP_DISABLED"
      },
      "data": {
        "channelgroup_ref": channelGroup,
        "channelpartition_ref": channelPartition,
        "channelpair_type": "channelpair",
        "channelpair_linerate": "down_10_up_10",
        "gpon_ponid_interval": 0,
        "gpon_ponid_odn_class": "CLASS_A"
      },
      "name": name
    }

    volthaPost('channel pair', 'http://{}:8882/api/v1/channel_pairs/{}'.format(volthaIp, name), data)
    log.info("Channel pair : {} created".format(name))

def createTrafficDescriptor(name):
    data = {
     "id": "ffff000000000000",
     "name": name,
     "fixed_bandwidth": "10000000",
     "assured_bandwidth": "10000000",
     "maximum_bandwidth": "10000000",
     "priority": 1,
     "weight": 1,
     "additional_bw_eligibility_indicator": "ADDITIONAL_BW_ELIGIBILITY_INDICATOR_NONE"
   }
    volthaPost('traffic descriptor', 'http://{}:8882/api/v1/traffic_descriptor_profiles/{}'.format(volthaIp, name), data)
    log.info("Traffic descriptor : {} created".format(name))


def createChannelTermination(deviceId, name, channelPair, ponId):
    data = {
      "interface": {
        "name": name,
        "description": "Channel Termination for {}".format(channelPair),
        "type": "channel-termination",
        "enabled": True,
        "link_up_down_trap_enable": "TRAP_DISABLED"
      },
      "data": {
        "channelpair_ref": channelPair,
        "meant_for_type_b_primary_role": True,
        "ngpon2_twdm_admin_label": 0,
        "ngpon2_ptp_admin_label": 0,
        "xgs_ponid": ponId,
        "xgpon_ponid": 0,
        "gpon_ponid": "",
        "pon_tag": "",
        "ber_calc_period": 0,
        "location": "AT&T EdgeCore OLT",
        "url_to_reach": ""
      },
      "name": name
    }

    volthaPost('channel termination', 'http://{}:8882/api/v1/devices/{}/channel_terminations/{}'.format(volthaIp,
                                                                                    deviceId, channelPair), data)
    log.info("Channel termination : {} created".format(channelPair))

def create_v_ont_anis(serialNumber, id, username, channelPartition, channelPair):
    data = {
        "interface": {
        "name": username,
        "description": "ATT Golden User in Freedom Tower",
        "type": "v-ontani",
        "enabled": True,
        "link_up_down_trap_enable": "TRAP_DISABLED"
      },
      "data": {
        "parent_ref": channelPartition,
        "expected_serial_number": serialNumber,
        "expected_registration_id": "",
        "preferred_chanpair": channelPair,
        "protection_chanpair": "",
        "upstream_channel_speed": 0,
        "onu_id": id
      },
      "name": username
    }

    volthaPost('v_ont_anis', 'http://{}:8882/api/v1/v_ont_anis/{}'.format(volthaIp, username), data)
    log.info("V_ONT_ANIS : {} created".format(username))


def createTcont(name, username, trafficDescriptor, id):
    data = {
        "name": name,
        "interface_reference": username,
        "traffic_descriptor_profile_ref": trafficDescriptor,
        "alloc_id": id
    }
    volthaPost('tcont', 'http://{}:8882/api/v1/tconts/{}'.format(volthaIp, name), data)
    log.info("TCONT : {} created".format(name))


def createVEnets(name, username):
    data = {
      "interface": {
        "name": name,
        "description": "Ethernet port - {}".format(name),
        "type": "v-enet",
        "enabled": True,
        "link_up_down_trap_enable": "TRAP_DISABLED"
      },
      "data": {
        "v_ontani_ref": username
      },
      "name": name
    }

    volthaPost('v_enet', 'http://{}:8882/api/v1/v_enets/{}'.format(volthaIp, name), data)
    log.info("VEnet : {} created".format(name))


def createGemPort(name, enet, tcont, id):
    data = {
        "name": name,
        "itf_ref": enet,
        "traffic_class": 2,
        "aes_indicator": True,
        "tcont_ref": tcont,
        "gemport_id": id
    }

    volthaPost('gem port', 'http://{}:8882/api/v1/gemports/{}'.format(volthaIp, name), data)
    log.info("Gem port : {} created".format(name))

def onosSubscriber(oltDpid, port, ctag):
    r = requests.post('http://{}:8181/onos/olt/oltapp/of%3A{}/{}/{}'.format(volthaIp, oltDpid, port, ctag))
    if r.status_code != 200:
        log.error("Error {} on ONOS add subscriber POST".format(r.status_code))
        exit()
    else:
        log.info("Subscriber {} provisionned in ONOS".format(ctag))



