#!/bin/bash


clusterip=$(dig +short etcd-cluster-client.default.svc.cluster.local @10.96.0.10)

kubectl scale statefulset vcore -n voltha --replicas=0
etcdctl --endpoints=http://${clusterip}:2379 del service --prefix -w fields
sleep 2
kubectl scale statefulset vcore -n voltha --replicas=1

