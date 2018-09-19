#!/bin/bash

srcpath=~/source/foundry_source/voltha_foundry_test/

#Stop containers
kubectl delete -f $srcpath/k8s/foundry-node/

#Flush stored data
sudo rm -r /var/lib/voltha-runtime/etcd/*
sudo rm -r /var/lib/voltha-runtime/consul/data/*
sudo rm -r /var/lib/voltha-runtime/fluentd/*
sudo rm -r /var/lib/voltha-runtime/kafka/*
sudo rm -r /var/lib/voltha-runtime/zookeeper/data/*
sudo rm -r /var/lib/voltha-runtime/zookeeper/datalog/*
sudo rm -r /var/lib/voltha-runtime/grafana/data/*

echo "waiting to restart apps..."
sleep 5

#Reapply/recreate containers
kubectl apply -f $srcpath/k8s/foundry-node/zookeeper_persist.yml
kubectl apply -f $srcpath/k8s/foundry-node/kafka_persist.yml
kubectl apply -f $srcpath/k8s/foundry-node/etcd_persist.yml
kubectl apply -f $srcpath/k8s/foundry-node/fluentd.yml
#kubectl apply -f $srcpath/k8s/foundry-node/vcore_for_etcd_repo.yml
kubectl apply -f $srcpath/k8s/foundry-node/vcore_for_etcd_repo_msz.yml
kubectl apply -f $srcpath/k8s/foundry-node/ofagent_repo.yml
kubectl apply -f $srcpath/k8s/foundry-node/envoy_for_etcd_repo.yml
kubectl apply -f $srcpath/k8s/foundry-node/vcli_repo.yml
kubectl apply -f $srcpath/k8s/foundry-node/netconf_repo.yml
kubectl apply -f $srcpath/k8s/foundry-node/onos_repo.yml

#Show resulting containers
kubectl get pod -n voltha
kubectl get svc -n voltha



