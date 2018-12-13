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

## Git clone ATT voltha.  

Contains deployment yaml for specific pods and services.  And other goodies.
Checkout repo, if not done already.
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

This process will manually apply k8s yaml files to deploy the environment.  This does NOT use helm.

Install non-voltha specific software components.  
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

Actual pods needed to run voltha. Edited to reflect ATT foundry docker repo 
```
kubectl apply -f foundry-node/vcore_for_etcd_repo.yml
kubectl apply -f foundry-node/ofagent_repo.yml 
kubectl apply -f foundry-node/envoy_for_etcd_repo.yml 
kubectl apply -f foundry-node/vcli_repo.yml 
kubectl apply -f foundry-node/netconf_repo.yml 
```

Edit onos network config to reflect your OLT hardware.  Otherwise copy as-is.  Install onos needed to drive the voltha "switch"
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
kubectl get pods -n voltha   # choose pod name to investigate
kubectl describe pod <pod-name> -n voltha
kubectl log <pod-name> -n voltha -f --tail=20
```


Get service ip, either NodePort or ClusterIP, and connect to CLI services.
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

At this point voltha and its required pods are running.  Use the CLI or API to add your OLT "linecard".  We typically use EdgeCore OLT devices.


## USEFUL SCRIPTS AND ALIASES 

Add an entry called master0 into your hosts file.  This is to stay consistent with cluster naming later:
```
localip=$(ip addr show dev eth0|grep "inet "|awk '{ print $2 }' |cut -d'/' -f1)
sudo bash -c "echo \"${localip}     master0\" >> /etc/hosts"
```

Add this to your .bashrc file for ease of system usage.
```
export EDITOR=vi
export HELM_HOME=/home/foundry/.helm
export ETCDCTL_API=3

source <(kubectl completion bash)
alias purge='~/source/voltha/k8s/foundry-node/scripts/etcd-clean.sh purge'
alias onos='ssh-keygen -f "/home/foundry/.ssh/known_hosts" -R [master0]:30115; ssh -p 30115 -o StrictHostKeyChecking=no karaf@master0'
alias vcli='ssh-keygen -f "/home/foundry/.ssh/known_hosts" -R [master0]:30110; ssh -p 30110 -o StrictHostKeyChecking=no voltha@master0'
alias kgp='kubectl get pods --all-namespaces -o wide'

kol ()
{
    pod=$(kubectl get pods -n voltha |grep onos |grep Running | awk '{print $1}');
    kubectl logs $pod -n voltha $@
}
kvl ()
{
    pod=$(kubectl get pods -n voltha |grep vcore |grep Running | awk '{print $1}');
    kubectl logs $pod -n voltha $@
}
```

purge clears etcd data and delete/re-applys pods.  Good for development cycle iteration.
vcli alias accesses voltha cli. 
onos alias accesses onos cli. 
kgp gets kubernetes pods without all the typing.
kvl get vcore's log.
kol get onos' log.



## TO BUILD CONTAINERS 

If need to modify code or build your own Docker image follow these steps.  
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


