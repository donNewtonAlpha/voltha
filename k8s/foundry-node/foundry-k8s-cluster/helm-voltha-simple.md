# Basic voltha install with helm

Minimal setup without seba pods

## Install voltha and dependencies.  finally, why we are here

Checkout needed repos.  Some of this may exist if youve followed previous notes
```
cd ~/
mkdir -p source
cd ~/source
git clone https://github.com/donNewtonAlpha/voltha.git
git clone https://bitbucket.org/onfcord/podconfigs.git
git clone https://gerrit.opencord.org/seba
git clone https://gerrit.opencord.org/helm-charts
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

helm install -n cord-kafka incubator/kafka --set replicas=1 --set persistence.enabled=false --set zookeeper.servers=1 --set zookeeper.persistence.enabled=false

helm dep update voltha
helm install -n voltha voltha --set etcd-operator.customResources.createEtcdClusterCRD=false -f ~/foundry-k8s-cluster/att-seba-voltha-values.yaml

helm dep update onos
helm install -n onos-voltha onos -f ~/foundry-k8s-cluster/att-seba-onos-voltha.yaml
```


Give voltha a couple minutes to install. This step is needed because of a bug with etcd-operator.  Need to "upgrade" to get etcd-cluster pods 
verify with kubectl get pods
```
sleep 120
helm upgrade voltha voltha --set etcd-operator.customResources.createEtcdClusterCRD=true -f ~/foundry-k8s-cluster/att-seba-voltha-values.yaml
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

