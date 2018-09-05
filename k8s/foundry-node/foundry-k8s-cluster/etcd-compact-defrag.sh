#!/bin/bash

compact=$1

clusterip=$(dig +short etcd-cluster-client.default.svc.cluster.local @10.96.0.10)

if [ "$compact" = "compact" ]
then
  revision=$(etcdctl --endpoints=${clusterip}:2379 get "Revision" --prefix -w fields |grep "Revision" |cut -f2 -d:|xargs)
  cleanuprev=$((revision-10))

  echo "current revision: $revision"
  echo "cleanup revision: $cleanuprev"

  etcdctl --endpoints=${clusterip}:2379 compact $cleanuprev
fi


for i in $(kubectl get pods --all-namespaces|grep etcd-cluster |awk '{ print $2 }');  
do    
  name=$i;   
  echo -ne "\n\n$name\n";    
  host=$(dig +short ${name}.etcd-cluster.default.svc.cluster.local @10.96.0.10);    
  etcdctl --endpoints=${host}:2379 defrag;  
  etcdctl --endpoints=${host}:2379 endpoint status;  
done

