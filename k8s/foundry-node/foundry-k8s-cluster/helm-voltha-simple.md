# Basic voltha install with helm

Minimal setup without seba pods.  Assumes a working k8s environment, single server or cluster.

## Install voltha and dependencies.  finally, why we are here

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


## Helm install 

Foundry specific values, currently dockers images from the foundry docker-repo
```
cd ~/source/helm-charts

helm repo add incubator https://kubernetes-charts-incubator.storage.googleapis.com/
helm repo add cord https://charts.opencord.org/master
helm repo update
helm repo list
```


Install Kafka and etcd-operator from hosted repos
```
helm install -n cord-kafka incubator/kafka --set replicas=1 --set persistence.enabled=false --set zookeeper.servers=1 --set zookeeper.persistence.enabled=false
helm install -n etcd-operator stable/etcd-operator

# wait until the etcd CustomResourceDefinitions are added
kubectl api-resources |grep etcd.database.coreos.com
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


Install onos
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

