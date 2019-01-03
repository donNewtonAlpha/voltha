# Foundry Notes

These are some of the documents we (Foundry) refer to when building out kubernetes and seba/voltha.  They are split apart into the different paths needed, be they a simple development environment or a full cluster running all of SEBA


## Kubernetes Builds

Setup a basic k8s single instance, good for anything needing a k8s environment.  Not specific to voltha. Basically just a single kubeadm based setup.  
https://github.com/etowah/seba-control-repo/blob/master/simple-kubeadm-setup.txt

Setup a 3 server k8s cluster using kubespray.  Capable of being installed offline if images/artifacts are gathered.  The old way is no longer needed (and was too complicated).  Simple online kubespray way.    
https://github.com/etowah/seba-control-repo/blob/master/simple-kubespray-setup.txt

The specifics for a fully offline setup, lots of prep work required.  Much more detail on ansible capabilities here:  
https://github.com/etowah/seba-control-repo/blob/master/README.md



## Installing SEBA or VOLTHA

Installing voltha using static yaml files.   This is what we typically do for day-to-day development iteration.   
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/dev/dev-notes.txt


Install full SEBA pod using helm (xos/onos/voltha).  This has also been tested on a single VM and a 3 server cluster.  

Online/Development installation (override chart/docker image versions as needed):  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/dev/seba-notes.txt

Online Release Installation (using all-in-one macro charts. voltha 1.6, seba 1.0, cord 6.1):  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/dev/seba-macro-chart-notes.txt

Offline Release installation (voltha 1.5, seba pre-release):  
https://github.com/etowah/seba-control-repo/blob/master/helm-seba-voltha-install.txt  



## Debugging VOLTHA

Run pycharm with remote debugging capabilities.   Build development image that allows stepping through code and breakpoints  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/pycharm-voltha-debug.md

