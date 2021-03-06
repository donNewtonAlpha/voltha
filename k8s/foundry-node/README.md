# Foundry Notes

These are some of the documents we (Foundry) refer to when building out kubernetes and seba/voltha.  They are split apart into the different paths needed, be they a simple development environment or a full cluster running all of SEBA



## Kubernetes Builds

Setup a basic k8s single instance, good for anything needing a k8s environment.  Not specific to voltha. Basically just a single kubeadm based setup.  
https://github.com/etowah/seba-control-repo/blob/master/simple-kubeadm-setup.txt

Setup a 3 server k8s cluster using kubespray.  Capable of being installed offline if images/artifacts are gathered.  The old way is no longer needed (and was too complicated).  Simple online kubespray way.    
https://github.com/etowah/seba-control-repo/blob/master/simple-kubespray-setup.txt

The specifics for a fully offline setup, lots of prep work required.  Much more detail on ansible capabilities here:  
https://github.com/etowah/seba-control-repo/blob/master/README.md



## Building VOLTHA Docker Images

Setting up the build environment and building local :latest images  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/dev/build-notes.txt

### Access to the Foundry docker repo
This requires your source IP to be added to a trusted ACL.  Provide that to the repo administrator then follow the notes below to add the needed CA cert to your system and test:  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/convert-repo.md

### Debugging VOLTHA

Run pycharm with remote debugging capabilities.   Build development image that allows stepping through code and breakpoints  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/pycharm-voltha-debug.md



## Installing SEBA or VOLTHA

### VOLTHA development using static k8s yaml
Installing voltha using static yaml files.   This is what we typically do for day-to-day development iteration.   
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/dev/dev-notes.txt


### Install full SEBA pod using helm (xos/onos/voltha).  
This has also been tested on a single VM and a 3 server cluster.  Much of this has been pulled from the official CORD
documentation:  
https://guide.opencord.org/profiles/seba/install.html

Development installation (override chart/docker image versions, values yaml as needed):  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/dev/seba-notes.txt

Release Installation (using all-in-one macro charts. voltha 1.6, seba 1.0, cord 6.1):  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/dev/seba-macro-chart-notes.txt



## Testing VOLTHA Development Environment

When running only the voltha pods/containers and the voltha onos, use these steps to provision an olt and pass traffic  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/dev/test-notes.txt



