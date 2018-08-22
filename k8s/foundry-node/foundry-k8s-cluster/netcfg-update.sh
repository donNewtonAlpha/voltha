#!/bin/bash

curl --user onos:rocks -X POST -H "Content-Type: application/json" http://onos-voltha-ui.voltha.svc.cluster.local:8181/onos/v1/network/configuration/ -d @/home/foundry/source/voltha/onos-config/network-cfg.json

