# Basic voltha setup
Assumes a running k8s environment.  Only installs yaml files specific to voltha


## Stage local persistent directories

Needed to simulate persistent storage for various dependent services
```
sudo mkdir -p /var/lib/voltha-runtime/etcd
sudo mkdir -p /var/lib/voltha-runtime/consul/data
sudo mkdir -p /var/lib/voltha-runtime/consul/config
sudo mkdir -p /var/lib/voltha-runtime/fluentd
sudo mkdir -p /var/lib/voltha-runtime/kafka
sudo mkdir -p /var/lib/voltha-runtime/zookeeper/data
sudo mkdir -p /var/lib/voltha-runtime/zookeeper/datalog
sudo mkdir -p /var/lib/voltha-runtime/onos/config
sudo chown -R $(id -u):$(id -g) /var/lib/voltha-runtime
```

## Git clone ATT voltha.  Contains deployment yaml for specific pods and services.  
Does NOT use helm.
This was likely done already.
```
mkdir -p ~/source
cd ~/source
git clone https://github.com/donNewtonAlpha/voltha.git
cd ~/source/voltha/k8s/
```

## Install ingress and namespace

```
kubectl apply -f namespace.yml 
kubectl apply -f ingress/
```


## BASE COMPONENTS

These files have been edited to reflect persistent environment
```
kubectl apply -f foundry-node/zookeeper_persist.yml
kubectl apply -f foundry-node/kafka_persist.yml
kubectl apply -f foundry-node/etcd_persist.yml
kubectl apply -f foundry-node/fluentd.yml
```

Verify pods startup, describe and get logs on select ones
```
kubectl get pod -n voltha
kubectl describe pod kafka-0 -n voltha
kubectl describe pod etcd-0 -n voltha
```

Verify mount binds are writing data
```
ls -atlrR /var/lib/voltha-runtime/
```


## VOLTHA CORE AND ACCESSORY CONTAINERS 

```
kubectl apply -f foundry-node/vcore_for_etcd_repo.yml
kubectl apply -f foundry-node/ofagent_repo.yml 
kubectl apply -f foundry-node/envoy_for_etcd_repo.yml 
kubectl apply -f foundry-node/vcli_repo.yml 
kubectl apply -f foundry-node/netconf_repo.yml 
```

Edit onos network config to reflect your OLT hardware.  Otherwise copy as-is
```
cp ~/source/voltha/onos-config/network-cfg.json /var/lib/voltha-runtime/onos/config/
kubectl apply -f foundry-node/onos_repo.yml 
```


Verify all pods
```
kubectl get pods -n voltha
```

Check health, vcore is the big one
```
kubectl get pods -n voltha   # get pod name of choice
kubectl describe pod <pod-name> -n voltha
kubectl log <pod-name> -n voltha -f --tail=20
kubectl exec -ti <pod-name> -n voltha -- /bin/sh
#   exit shell back to host
```


Get svc ip and connect cli
```
kubectl get svc -n voltha  # note the vcli clusterIP, and the onos clusterIP

# voltha, password admin
ssh -p 5022 voltha@<vcli-cluster-IP>
## run "devices" to verify connectivity to etcd.  you should see "table empty"
## type quit to exit voltha shell

# onos, password karaf
ssh -p 8101 karaf@<onos-cluster-IP>
## run "netcfg" to verify 
## type logout to exit onos shell
```

## VOLTHA CORE DONE 


## USEFUL SCRIPTS AND ALIASES 

Add this to your .bashrc file

```
alias purge='~/source/voltha/k8s/foundry-node/scripts/etcd-clean.sh purge'
alias vcli='ssh -p 5022 -o StrictHostKeyChecking=no voltha@vcli.voltha.svc.cluster.local'
alias onos='ssh-keygen -f "/home/foundry/.ssh/known_hosts" -R [onos.voltha.svc.cluster.local]:8101; ssh -p 8101 -o StrictHostKeyChecking=no karaf@onos.voltha.svc.cluster.local'


kgp() {
  kubectl get pods --all-namespaces
}

kvl() {
  pod=$(kubectl get pods -n voltha |grep vcore | awk '{print $1}')
  kubectl logs $pod -n voltha $@
}

kol() {
  pod=$(kubectl get pods -n voltha |grep onos | awk '{print $1}')
  kubectl logs $pod -n voltha $@
}
```

Purge clear etcd
vcli access voltha cli
onos access onos cli
kgp get kubernetes pods
kvl get vcore's log
kol get onos' log



## TO BUILD CONTAINERS 

```
sudo apt-get update
sudo apt-get install build-essential virtualenv python-dev python-pip python libssl-dev libpcap-dev python-netifaces \
python-virtualenv python-urllib3 python-nose python-flake8 python-scapy

cd ~/source/voltha

. env.sh
make install-protoc
make build

# Next time if you just want to rebuild the voltha container
. env.sh
make build voltha
```


