# Completely Remove All Docker and Kubernetes containers.
Purging all containers and images, remove k8s.   This explicitly removes voltha pods and deployments but given the kubeadm reset, it gets rid of EVERYTHING.

```
cd ~/source/voltha/k8s
```

Remove all running voltha services
```
kubectl delete -f foundry-node/
```

Remove the running k8s cluster
```
sudo kubeadm reset
```

Remove all leftover containers and images.  This will force new docker image downloads.
```
sudo docker system prune --all
```

Clear out voltha persistent data
```
sudo rm -rf /var/lib/voltha-runtime
```

Remove local user credentials for removed k8s
```
rm -rf ~/.kube
```

Stop kubelet and docker
```
systemctl stop kubelet
systemctl stop docker
```


