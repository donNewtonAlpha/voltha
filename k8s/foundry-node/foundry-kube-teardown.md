# Completely teardown and voltha and k8s
Purging all containers and images, remove k8s.

```
cd ~/source/voltha/k8s

Remove all running voltha services
```
kubectl delete -f foundry-node/
```

Remove the running k8s cluster
```
sudo kubeadm reset
```

Remove all leftover containers and images
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

