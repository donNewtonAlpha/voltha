#!/bin/bash

# reset a master.  run on all master cluster nodes


kubeadm reset
docker system prune --all
systemctl stop kubelet
rm -rf /var/lib/etcd
rm -rf /etc/cni
rm -rf /opt/cni
rm -rf /var/lib/calico
rm -rf ~/.kube
rm -rf ~/.helm

