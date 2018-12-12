#!/bin/bash

action=$1

srcpath=~/source/voltha/k8s/foundry-node/dev/

if [ "$action" != "deploy" ]
then
  #Stop containers
  kubectl delete -f $srcpath/onos_dev.yaml
  kubectl delete -f $srcpath/vcli_dev.yaml
  kubectl delete -f $srcpath/netconf_dev.yaml
  kubectl delete -f $srcpath/ofagent_dev.yaml
  kubectl delete -f $srcpath/envoy_dev.yaml
  kubectl delete -f $srcpath/vcore_dev.yaml
  kubectl delete -f $srcpath/etcd_cluster_dev.yaml
  kubectl delete -f $srcpath/rbac_dev.yaml
  kubectl delete -f $srcpath/ns_dev.yaml
  echo "waiting to restart apps..."
  sleep 5
fi

#Reapply/recreate containers
kubectl apply -f $srcpath/ns_dev.yaml
kubectl apply -f $srcpath/rbac_dev.yaml
kubectl apply -f $srcpath/etcd_cluster_dev.yaml
kubectl apply -f $srcpath/vcore_dev.yaml
kubectl apply -f $srcpath/envoy_dev.yaml
kubectl apply -f $srcpath/ofagent_dev.yaml
kubectl apply -f $srcpath/netconf_dev.yaml
kubectl apply -f $srcpath/vcli_dev.yaml
kubectl apply -f $srcpath/onos_dev.yaml

