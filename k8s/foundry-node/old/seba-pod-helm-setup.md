# Full SEBA Pod Installation Notes

Will run on a single k8s instance or a 3 server cluster.  Helm must also already be installed.  See other notes for k8s and helm setup. 
These helm charts and docker images are under daily active development and can break as often with no notice.  Work is being done to create snapshots of stable instances.  
These notes are subject to change until things stabilize.  This should be runnable as a non-root user assuming previous install steps allowed this.


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

We use a set of custom helm values yaml file for our deployments, kept in our voltha github clone
```
cd ~/
mkdir -p source
cd ~/source
git clone https://github.com/donNewtonAlpha/voltha.git
git clone https://github.com/donNewtonAlpha/helm-charts.git
git clone https://github.com/etowah/seba-control-repo.git
cd ~/

# this may exists if you used previous notes
ln -s ~/source/voltha/k8s/foundry-node/foundry-k8s-cluster
```


## Install cord helm charts. xos, onos, voltha etc

See https://guide.opencord.org/profiles/rcord/workflows/att.html .
This is just a condensed version of those instructions, with the addition of our custom environment values yaml files.
```
cd ~/source/helm-charts/
helm repo add incubator https://kubernetes-charts-incubator.storage.googleapis.com/
helm repo add cord https://charts.opencord.org/master
helm repo update
helm repo list
```


Install Kafka and etcd-operator from hosted repos
```
helm install -n cord-kafka incubator/kafka --version 0.8.8 --set persistence.enabled=false --set zookeeper.persistence.enabled=false
helm install -n etcd-operator stable/etcd-operator --version 0.8.0 

# wait until the etcd CustomResourceDefinitions are added
kubectl get crd | grep etcd
```


Install XOS Core
```
helm dep update xos-core
helm install -n xos-core xos-core -f ~/foundry-k8s-cluster/att-seba-voltha-values.yaml
```


Install voltha.  Note the custom values.  There we define the docker images we want to run, and the kafka that we want voltha to share with xos and onos.
```
helm dep update voltha
helm install -n voltha voltha -f ~/foundry-k8s-cluster/att-seba-voltha-values.yaml
```


Install onos
```
helm dep update onos
helm install -n onos onos -f ~/source/helm-charts/configs/onos.yaml -f ~/foundry-k8s-cluster/att-seba-voltha-values.yaml
```


Install att workflow xos-to-voltha and onos syncronizers.  Business logic specific.  Load needed onos apps into voltha onos.
```
helm dep update xos-profiles/att-workflow
helm install -n att-workflow xos-profiles/att-workflow -f ~/foundry-k8s-cluster/att-seba-voltha-values.yaml
```


Install k8s workflow synchronizers.  
```
helm dep update xos-profiles/base-kubernetes
helm install -n base-kubernetes xos-profiles/base-kubernetes -f ~/foundry-k8s-cluster/att-seba-voltha-values.yaml
```


Allow xos-profiles tosca loaders to finish.  Both att-workflow and base-kubernetes.  
```
kubectl get pods -o wide |grep Complete
```


Login to voltha cli and onos cli.  Verify voltha devices are empty.  Verify onos apps are loaded and kafka connected
```
TODO: grab a screencap
```



## POD, OLT, and Subscriber Provisioning

Below is where provisioning starts.  These are specific to the QA pod so change yaml files to match your environment.  Replace localip with whichever k8s host has the available NodePorts.   See kubectl get svc.  These TOSCA files being curl'ed into the pod represent the provisioning steps needed to build a pod, add an olt, add an onu, and then add a subscriber.   These ultimately would be called upon by an OSS system, using either gRPC or RESTful calls.  But for now we use curl to get things going. 
```
cd ~/source/seba-control-repo/provisioning-yaml/
```

Load radius server config into onos voltha.  Replace seba-node1 with one of your k8s host's IP addresses.
```
~/source/seba-control-repo/scripts/quick-onos-update.sh seba-node1 radius-netcfg.json
```

Run the tosca model additions to create pod, olt line card, onu whitelist additions, and actual subscriber data.  One important difference from previous voltha installs is you do NOT have to preprovision or enable the OLT via the voltha cli.   The API provisioning of the pod-olt.yaml below does that step.  You DO still need to start bal_core_dist and openolt on the edgecore itself.
```
# Provision POD OLT and test ONU/RG

# Should now be ready to use abstract-olt or manual yaml to provision pod OLT, whitelist, and subscriber.
# TODO: add abstract-olt commands instead

# Edit pod-olt.yaml, replace IP of your Edgecore OLT running bal and openolt
curl -H "xos-username: admin@opencord.org" -H "xos-password: letmein" -X POST --data-binary @provisioning-yaml/pod-olt.yaml http://seba-node1:30007/run
# Use vcli, verify olt is added and any onu go into omci-admin-lock state

# Modify whitelist for ONU plugged into proper ports.  Replace of:XXXX device id with parent_port_id from olt in vcli
curl -H "xos-username: admin@opencord.org" -H "xos-password: letmein" -X POST --data-binary @provisioning-yaml/whitelist.yaml http://seba-node1:30007/run
# Use vcli, devices, verify onu go into discovered state.  use onos cli, log:tail, verify RG are attempting to auth AND FAILING.

# Modify subscribers for ONU, nas-port-id, and vlans to be used by subscribers
curl -H "xos-username: admin@opencord.org" -H "xos-password: letmein" -X POST --data-binary @provisioning-yaml/subscribers.yaml http://seba-node1:30007/run
# Use onos cli, log:tail, verify RG are attempting to auth succeed.
# Also verify kafka app picks it up and SUBSCRIBER_REGISTERED is shown.  
# In onos cli, run aaa-users, volt-subscribers, volt-programmed-subscribers, and dhcpl2relay-allocations
# Use vcli, verify onu state is omci-flows-pushed.
```

At this point plug in ONU and RG that can authenticate to the ATT lab radius server.  VLANS should be pushed on successfull eap authentication and traffic pass all the way out to the BNG.



## Troubleshoot and Purge

Only needed to troubleshoot auth events
```
helm install -n kafkacat ~/source/helm-charts/xos-tools/kafkacat
kubectl exec -ti kafkacat-86bf65f7f7-8w5m2 -- kafkacat -b cord-kafka -t authentication.events
```

To delete everything.  
```
helm delete --purge att-workflow base-kubernetes onos voltha xos-core nem-monitoring etcd-cluster etcd-operator cord-kafka

# force removal of CRD added by etcd-operator
kubectl delete customresourcedefinition etcdclusters.etcd.database.coreos.com
kubectl delete customresourcedefinition etcdbackups.etcd.database.coreos.com
kubectl delete customresourcedefinition etcdrestores.etcd.database.coreos.com

kubectl delete endpoints etcd-operator
kubectl delete clusterrole etcd-operator
kubectl delete clusterrolebinding etcd-operator
```

