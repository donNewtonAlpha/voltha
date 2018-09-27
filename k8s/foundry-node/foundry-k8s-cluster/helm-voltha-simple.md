# Basic voltha install with helm

Minimal setup without seba pods.  Assumes a working k8s environment, single server or cluster.  Helm must also already be installed.  See other notes for k8s and helm setup.
This should be runnable as a non-root user assuming previous install steps allowed this.


## Verify Docker Repo Access

The docker images used are downloaded from the foundry docker repo docker-repo.dev.atl.foundry.att.com.   This repo requires your source public IP to be added to a whitelist before being able to download images.   Contact mj3580@att.com for access.


To test this access works run the following:

Test locally installed Foundry CA approves https server cert
```
curl -v https://docker-repo.dev.atl.foundry.att.com:5000/v2/_catalog
```

Test docker pull
```
docker pull docker-repo.dev.atl.foundry.att.com:5000/ubuntu:16.04
```


## Clone needed github repos

Checkout needed repos.  Some of this may exist if youve followed previous notes
```
cd ~/
mkdir -p source
cd ~/source
git clone https://github.com/donNewtonAlpha/voltha.git
git clone https://github.com/donNewtonAlpha/helm-charts.git
cd ~/

# this may exists if you used previous notes
ln -s ~/source/voltha/k8s/foundry-node/foundry-k8s-cluster
```


## Helm setup 

Foundry specific values, currently dockers images from the foundry docker-repo
```
cd ~/source/helm-charts

helm repo add incubator https://kubernetes-charts-incubator.storage.googleapis.com/
helm repo add cord https://charts.opencord.org/master
helm repo update
helm repo list
```


## Install charts

Install Kafka and etcd-operator from hosted repos
```
helm install -n cord-kafka incubator/kafka --version 0.8.8 --set persistence.enabled=false --set zookeeper.persistence.enabled=false
helm install -n etcd-operator stable/etcd-operator

# wait until the 3 etcd CustomResourceDefinitions are added
kubectl get crd | grep etcd
```


Install etcd-operator managed etcd cluster
```
helm install -n etcd-cluster etcd-cluster

# wait until all 3 etcd-cluster-XXXX are Running
kubectl get pods -o wide |grep etcd-cluster
```


Install voltha.  Note the custom values.  There we define the docker images we want to run, and the kafka that we want voltha to share with xos and onos.
```
helm dep update voltha
helm install -n voltha voltha -f ~/foundry-k8s-cluster/simple-voltha-values.yaml
```


Install onos.  Values point to a custom onos image with aaa, olt and sadis apps built in.  
```
helm dep update onos
helm install -n onos onos -f ~/foundry-k8s-cluster/simple-onos-values.yaml
```


Properly inject onos config for olt, aaa, and sadis
For now just run curl shell script to inject needed config.  xos/nem/seba will provide this later
```
cd ~/foundry-k8s-cluster
./quick-onos-update.sh master0 ~/source/voltha/onos-config/network-cfg.json
```


### Verify cluster operation

Login verify apps running.  Manually add subscribers if there is no radius available
```
ssh -p 30110 voltha@master0
# username/password voltha/admin
#   devices 
#   table should say empty
#

ssh -p 30115 karaf@master0
# username/password karaf/karaf
#   apps -s -a
#   should list the installed apps
```

At this point you can use the voltha cli to preprovision and enable one or more edgecore OLT linecards.  Be sure to run bal_core_dist and openolt on the edgecore linecard.  Voltha will discover the onu, inform onos, and eap/dhcp should take over.


