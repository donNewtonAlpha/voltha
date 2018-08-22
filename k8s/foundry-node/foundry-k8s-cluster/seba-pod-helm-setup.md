# Full SEBA Pod Installation Notes

Will run on a single k8s instance or a 3 server cluster.  See other notes on how to setup


## Clone needed repos

We use a set of custom helm values yaml file for our deployments, kept in our voltha github clone
```
cd ~/source
git clone https://github.com/donNewtonAlpha/voltha.git
git clone https://bitbucket.org/onfcord/podconfigs.git
git clone https://gerrit.opencord.org/seba
git clone https://gerrit.opencord.org/helm-charts
```

### Install helm

Skip if you already have helm/tiller running.  
```
wget https://storage.googleapis.com/kubernetes-helm/helm-v2.9.1-linux-amd64.tar.gz
mkdir helm-unpack
cd helm-unpack/
tar -zxvf ../helm-v2.9.1-linux-amd64.tar.gz
sudo cp linux-amd64/helm /usr/local/bin/

cd ~/source/voltha/k8s/foundry-node/foundry-k8s-cluster
kubectl apply -f helm-role.yaml
helm init --service-account tiller
export HELM_HOME=/home/foundry/.helm
```


# Install cord helm charts. xos, onos, voltha etc

See https://guide.opencord.org/profiles/rcord/workflows/att.html .
This is just a condensed version of those instructions, with the addition of our custom environment values yaml files.
```
cd ~/source/helm-charts/
helm repo add incubator https://kubernetes-charts-incubator.storage.googleapis.com/
helm repo add cord https://charts.opencord.org/master
helm repo update
helm repo list
```


XOS Core and a Kafka that both voltha, onos and xos share
```
helm dep update xos-core
helm install -n xos-core xos-core
helm install -n cord-kafka incubator/kafka --set replicas=1 --set persistence.enabled=false --set zookeeper.servers=1 --set zookeeper.persistence.enabled=false 
```

Install voltha.  Note the custom values.  There we define the docker images we want to run, and the kafka that we want voltha to share with xos and onos.
```
helm dep update voltha
helm install -n voltha voltha --set etcd-operator.customResources.createEtcdClusterCRD=false -f ~/source/voltha/k8s/foundry-node/foundry-k8s-cluster/att-seba-voltha-values.yaml
```

Install onoses (onosi?).   Voltha onos should refer to stock onos image.  Custom apps get loaded later.  Fabric onos currently requires a custom build as there are features not yet pushed to the base image yet.  This should change soon enough.
```
helm dep update onos
helm install -n onos-voltha onos -f ~/source/helm-charts/configs/onos-voltha.yaml
helm install -n onos-fabric onos -f ~/source/voltha/k8s/foundry-node/foundry-k8s-cluster/att-seba-fabric-values.yaml
```

Give voltha a couple minutes to install. This step is needed because of a bug with etcd-operator.  Need to "upgrade" to get etcd-cluster pods.
Verify with kubectl get pods that 3 etcd-cluster-000X are running.
```
sleep 120
helm upgrade voltha voltha --set etcd-operator.customResources.createEtcdClusterCRD=true -f ~/source/voltha/k8s/foundry-node/foundry-k8s-cluster/att-seba-voltha-values.yaml
```

Install att workflow xos-to-voltha and onos syncronizers.  Business logic specific.  Load needed onos apps into voltha onos.
```
helm dep update xos-profiles/att-workflow
helm install -n att-workflow xos-profiles/att-workflow -f ~/source/voltha/k8s/foundry-node/foundry-k8s-cluster/att-seba-profile-values.yaml
# give the workflow pods time to populate models, load apps, etc.
sleep 120
```


## POD, OLT, and Subscriber Provisioning

Below is where provisioning starts.  These are specific to the QA pod so change yaml files to match your environment.  Replace localip with whichever k8s host has the available NodePorts.   See kubectl get svc.
```
cd ~/source/podconfigs/tosca/att-workflow

localip=10.64.1.X
```

Load radius server config into onos voltha.  You may need to replace foundry-simple-netcfg.json with foundry-full-netcfg.json depending on if xos syncronizers can fully populate/query sadis.
```
~/source/voltha/k8s/foundry-node/foundry-k8s-cluster/quick-onos-update.sh $localip foundry-simple-netcfg.json
```

Run the tosca model additions to create pod, olt line card, onu whitelist additions, and actual subscriber data.
```
curl -H "xos-username: admin@opencord.org" -H "xos-password: letmein" -X POST --data-binary @foundry-pod-config.yaml http://${localip}:30007/run
curl -H "xos-username: admin@opencord.org" -H "xos-password: letmein" -X POST --data-binary @foundry-pod-olt.yaml http://${localip}:30007/run
curl -H "xos-username: admin@opencord.org" -H "xos-password: letmein" -X POST --data-binary @foundry-whitelist.yaml http://${localip}:30007/run
curl -H "xos-username: admin@opencord.org" -H "xos-password: letmein" -X POST --data-binary @foundry-subscribers.yaml http://${localip}:30007/run
```

## Troubleshoot and Purge

Only needed to troubleshoot auth events
```
helm install -n kafkacat ~/source/helm-charts/xos-tools/kafkacat
kubectl exec -ti kafkacat-86bf65f7f7-8w5m2 -- kafkacat -b cord-kafka -t authentication.events
```

To delete everything.  
```
helm delete --purge att-workflow cord-kafka onos-fabric onos-voltha voltha xos-core
```

At this point plug in ONU and RG that can authenticate to the ATT lab radius server.  VLANS should be pushed on successfull eap authentication and traffic pass all the way out to the BNG.


