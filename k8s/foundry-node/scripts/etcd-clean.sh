#!/bin/bash

export ETCDCTL_API=3

repopath=~/source/voltha/k8s/foundry-node/
action=$1

if ! type "etcdctl"
then
  echo ""
  echo "install etcdctl in your environment before attempting this script"
  echo "you can get it by copying from an etcd k8s container, for example"
  echo ""
  echo "sudo kubectl cp voltha/etcd-0:/usr/local/bin/etcdctl /usr/local/bin"
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


kubectl delete -f $repopath/envoy_for_etcd_repo.yml
kubectl delete -f $repopath/vcore_for_etcd_repo.yml 
kubectl delete -f $repopath/vcli_repo.yml
kubectl delete -f $repopath/ofagent_repo.yml
kubectl delete -f $repopath/onos_repo.yml 
kubectl delete -f $repopath/netconf_repo.yml

sleep 2

# have a look 
#etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 get service --prefix -w fields

if [ "$action" = "memberclean" ]
then
  #etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/data/core/assignment -w fields
  #etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/assignments/vcore-7f568d8446-9dh92_1524854704/core_store -w fields
  #etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/assignments/ --prefix -w fields
  #etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/members --prefix -w fields

  ### THIS JUST CLEARS FUBAR MEMBERSHIP
  etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/assignments --prefix -w fields
  #etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/members --prefix -w fields
  ## maybe this # etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/data/core/assignment --prefix -w fields
elif [ "$action" = "purge" ]
then
  ### THIS DELETES EVERYTHING!
  etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service --prefix -w fields
else
  echo "action $action not available. redeploying "
fi


echo "waiting to restart apps..."
sleep 5

kubectl apply -f $repopath/vcore_for_etcd_repo.yml 
kubectl apply -f $repopath/envoy_for_etcd_repo.yml
kubectl apply -f $repopath/vcli_repo.yml
kubectl apply -f $repopath/ofagent_repo.yml
kubectl apply -f $repopath/onos_repo.yml 
kubectl apply -f $repopath/netconf_repo.yml
