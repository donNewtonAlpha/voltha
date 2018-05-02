#!/bin/bash

sudo rm -rf /var/lib/voltha-runtime


sudo mkdir -p /var/lib/voltha-runtime/consul/data
sudo mkdir -p /var/lib/voltha-runtime/consul/config
sudo mkdir -p /var/lib/voltha-runtime/fluentd
sudo mkdir -p /var/lib/voltha-runtime/kafka
sudo mkdir -p /var/lib/voltha-runtime/zookeeper/data
sudo mkdir -p /var/lib/voltha-runtime/zookeeper/datalog
sudo mkdir -p /var/lib/voltha-runtime/grafana/data
sudo mkdir -p /var/lib/voltha-runtime/onos/config
sudo mkdir -p /var/lib/voltha-runtime/etcd
sudo chown -R $(id -u):$(id -g) /var/lib/voltha-runtime

cp ~/source/voltha/onos-config/network-cfg.json /var/lib/voltha-runtime/onos/config/
