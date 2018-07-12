#!/bin/bash

arg=$1

if [ "$arg" = "install" ]
then
  kubectl apply -f ~/source/voltha/k8s/foundry-node/zookeeper_persist.yml
  kubectl apply -f ~/source/voltha/k8s/foundry-node/kafka_persist.yml
  kubectl apply -f ~/source/voltha/k8s/foundry-node/fluentd.yml
  kubectl apply -f ~/source/voltha/k8s/foundry-node/etcd_persist.yml
  kubectl apply -f ~/source/voltha/k8s/foundry-node/vcore_for_etcd_repo.yml
  kubectl apply -f ~/source/voltha/k8s/foundry-node/envoy_for_etcd_repo.yml
  kubectl apply -f ~/source/voltha/k8s/foundry-node/ofagent_repo.yml
  kubectl apply -f ~/source/voltha/k8s/foundry-node/netconf_repo.yml
  kubectl apply -f ~/source/voltha/k8s/foundry-node/vcli_repo.yml
  kubectl apply -f ~/source/voltha/k8s/foundry-node/onos_repo.yml
else
  kubectl delete -f ~/source/voltha/k8s/foundry-node/onos_repo.yml
  kubectl delete -f ~/source/voltha/k8s/foundry-node/vcli_repo.yml
  kubectl delete -f ~/source/voltha/k8s/foundry-node/netconf_repo.yml
  kubectl delete -f ~/source/voltha/k8s/foundry-node/ofagent_repo.yml
  kubectl delete -f ~/source/voltha/k8s/foundry-node/envoy_for_etcd_repo.yml
  kubectl delete -f ~/source/voltha/k8s/foundry-node/vcore_for_etcd_repo.yml
  kubectl delete -f ~/source/voltha/k8s/foundry-node/etcd_persist.yml
  kubectl delete -f ~/source/voltha/k8s/foundry-node/fluentd.yml
  kubectl delete -f ~/source/voltha/k8s/foundry-node/kafka_persist.yml
  kubectl delete -f ~/source/voltha/k8s/foundry-node/zookeeper_persist.yml
fi

sleep 2

kubectl get po -n voltha

