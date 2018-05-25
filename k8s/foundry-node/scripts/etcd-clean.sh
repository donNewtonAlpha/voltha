#!/bin/bash

export ETCDCTL_API=3

#kubectl delete -f envoy_for_etcd_repo.yml
kubectl delete -f vcore_for_etcd_repo.yml 

sleep 2

#etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/data/core/assignment -w fields
#etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/assignments/vcore-7f568d8446-9dh92_1524854704/core_store -w fields
#etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/assignments/ --prefix -w fields
#etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/members --prefix -w fields

#etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 get service --prefix -w fields
etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/assignments --prefix -w fields
#etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/members --prefix -w fields
## maybe this # etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 del service/voltha/data/core/assignment --prefix -w fields
#etcdctl --endpoints=http://etcd.voltha.svc.cluster.local:2379 get service --prefix -w fields

sleep 2

kubectl apply -f vcore_for_etcd_repo.yml 
#kubectl apply -f envoy_for_etcd_repo.yml


