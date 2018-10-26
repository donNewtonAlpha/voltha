# Foundry Notes

These are some of the documents we (Foundry) refer to when building out kubernetes and seba/voltha.  They are split apart into the different paths needed, be they a simple development environment or a full cluster running all of SEBA


## Kubernetes Builds

Setup a basic k8s single instance, good for anything needing a k8s environment.  Not specific to voltha. Basically just a single kubeadm based setup.  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/basic-k8s-setup.md

Setup a 3 server k8s cluster using kubespray.  Capable of being installed offline if images/artifacts are gathered.  The old way is no longer needed (and was too complicated).  Simple online kubespray way.    
https://github.com/etowah/seba-control-repo/blob/master/simple-kubespray-setup.txt

The specifics for an offline setup.  Much more detail on ansible capabilities here:  
https://github.com/etowah/seba-control-repo/blob/master/README.md



## Installing SEBA or VOLTHA

Installing voltha using static yaml files.   This is what we typically do for day-to-day development iteration.   
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/basic-voltha-setup.md

Install basic helm based voltha.  Keep this around until seba/xos (below) is ready.  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/foundry-k8s-cluster/helm-voltha-simple.md

Install full SEBA pod using helm (xos/onos/voltha).  This has also been tested on a single VM and a 3 server cluster.  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/foundry-k8s-cluster/seba-pod-helm-setup.md  

Or using the packaged/stable local helm charts using the new method  
https://github.com/etowah/seba-control-repo/blob/master/helm-seba-voltha-install.txt


## Development and Debugging

Run pycharm with remote debugging capabilities.   Build development image that allows stepping through code and breakpoints  
https://github.com/donNewtonAlpha/voltha/blob/master/k8s/foundry-node/pycharm-voltha-debug.md

