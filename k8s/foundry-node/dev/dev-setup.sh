#!/bin/bash

action=$1

srcpath=~/source/voltha/k8s/foundry-node/dev/


function kube_delete() {

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

  rm /var/lib/voltha-runtime/logconfig.yml
  rm /var/lib/voltha-runtime/network-cfg.json

}

function kube_install() {

  cp $srcpath/logconfig.yml /var/lib/voltha-runtime/
  cp $srcpath/network-cfg.json /var/lib/voltha-runtime/

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

}



if [ "$action" = "deploy" ]
then
  kube_install
elif [ "$action" = "clean" ]
then
  kube_delete
elif [ "$action" = "redeploy" ]
then
  kube_delete
  echo "waiting to restart apps..."
  sleep 5
  kube_install
else
  echo "Usage $0 <deploy|clean|redeploy>"
  exit 1
fi


