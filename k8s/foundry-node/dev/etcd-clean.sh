#!/bin/bash

export ETCDCTL_API=3
srcpath=~/source/voltha/k8s/foundry-node/dev/

action=$1

if ! type "etcdctl"
then
  echo ""
  echo "install etcdctl in your environment before attempting this script"
  echo "you can get it by copying from an etcd k8s container, for example"
  echo ""
  echo "sudo kubectl cp voltha/etcd-0:/usr/local/bin/etcdctl /usr/local/bin"
  echo "sudo kubectl cp kube-system/etcd-kube-03:/usr/local/bin/etcdctl /usr/local/bin"
  echo "sudo kubectl cp default/etcd-cluster-mcbfnsdc6d:/usr/local/bin/etcdctl /usr/local/bin"
  echo ""
  echo "sudo chmod 755 /usr/local/bin/etcdctl"
  echo ""
  echo "exiting"
  exit 1
fi

if [ ! "$action" ]
then
  echo "Usage: $0 purge|memberclean"
  exit 1
fi


kubectl delete -f $srcpath/onos_dev.yaml
kubectl delete -f $srcpath/vcli_dev.yaml
kubectl delete -f $srcpath/ofagent_dev.yaml
kubectl delete -f $srcpath/netconf_dev.yaml
kubectl delete -f $srcpath/envoy_dev.yaml
kubectl delete -f $srcpath/vcore_dev.yaml

sleep 2

clusterip=$(dig +short etcd-cluster-client.default.svc.cluster.local @10.96.0.10)
totalkeys=$(etcdctl --endpoints=${clusterip}:2379 get --command-timeout=60s --from-key service --keys-only |grep service | wc -l)
echo -ne "Total Keys: $totalkeys\n\n"

if [ "$action" = "memberclean" ]
then
  etcdctl --endpoints=${clusterip}:2379 del service/voltha/assignments --prefix -w fields
elif [ "$action" = "purge" ]
then
  etcdctl --endpoints=${clusterip}:2379 del service --prefix -w fields
else
  echo "action $action not available. redeploying "
fi


echo "waiting to restart apps..."
sleep 5

kubectl apply -f $srcpath/vcore_dev.yaml
kubectl apply -f $srcpath/envoy_dev.yaml
kubectl apply -f $srcpath/ofagent_dev.yaml
kubectl apply -f $srcpath/netconf_dev.yaml
kubectl apply -f $srcpath/vcli_dev.yaml
kubectl apply -f $srcpath/onos_dev.yaml

