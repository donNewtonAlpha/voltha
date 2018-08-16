#!/bin/bash



kubectl scale statefulset vcore -n voltha --replicas=0
etcdctl --endpoints=http://etcd-cluster.default.svc.cluster.local:2379 del service --prefix -w fields
sleep 2
kubectl scale statefulset vcore -n voltha --replicas=1

