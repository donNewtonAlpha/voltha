# Kubernetes 3 Server Cluster Build Notes


Requires three hosts.  8 cpu, 16gb memory, 100GB disk.  Preferably SSD.  Swap must be disabled or permanently removed!
Ubuntu 16.04 patched and updated and on the network, internet.  

Note the IP and hostnames as will be used later in configs

Run all of this as root

Each host is referred below by their new alias that will be added to /etc/hosts, 
master0, master1, and master2.  Their existing hostnames will remain.  Note each of their IP 
addresses and which will be assigned their respective master role.  Some sections below must be run from one host, typially master0.  Other sections run from all 3 hosts.




## Run this section on ALL 3 HOSTS.  master0, master1, and master2

Disable swap if it was installed.  Left as an exersize to the reader on making this permanent and reclaiming the disk space.
```
swapoff -a
```


### Repo/package prep

scp package from outside host the build package, foundry-k8s-cluster.tgz. Or git clone.
Contains config, yaml, json files for certs, scripts, etc.
Unpack in ~/source
```
cd ~/
mkdir source
cd ~/source
git clone https://github.com/donNewtonAlpha/voltha.git
cd ~/
ln -s ~/source/voltha/k8s/foundry-node/foundry-k8s-cluster
cd foundry-k8s-cluster
sudo bash
```


### Host naming

Edit hosts-append to reflect the 3 master hosts and their IP addresses.  This will get appended into /etc/hosts and used later.
TODO: script this.  Edit references to master0, master1, and master2 to reflect your the 3 ip addresses for each. leave existing hostsnames in /etc/hosts.
```
vi hosts-append
cat hosts-append >> /etc/hosts
```


### Install base docker, kubelet, kubadm, etc

Docker-ce.  Add the gpg and repo  
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```

Kubernetes
```
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo add-apt-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
```

Actually install the packages
```
apt update
apt install docker-ce kubelet kubeadm kubectl -y
```

### Private CA cert installation.

Install the AT&T Foundry Atlanta CA cert at the system level.
```
cat > /usr/local/share/ca-certificates/att-foundry-atlanta-ca.crt << EOF
-----BEGIN CERTIFICATE-----
MIIE8DCCA9igAwIBAgIBADANBgkqhkiG9w0BAQUFADCBsDELMAkGA1UEBhMCVVMx
CzAJBgNVBAgTAkdBMSAwHgYDVQQKFBdBVCZUIEZvdW5kcnkgQXRsYW50YSBDQTEe
MBwGA1UECxMVQ2VydGlmaWNhdGUgQXV0aG9yaXR5MTMwMQYDVQQDFCpBVCZUIEZv
dW5kcnkgQXRsYW50YSBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkxHTAbBgkqhkiG9w0B
CQEWDm1qMzU4MEBhdHQuY29tMB4XDTE4MDgxNDE4MjA0OVoXDTI4MDgxMTE4MjA0
OVowgbAxCzAJBgNVBAYTAlVTMQswCQYDVQQIEwJHQTEgMB4GA1UEChQXQVQmVCBG
b3VuZHJ5IEF0bGFudGEgQ0ExHjAcBgNVBAsTFUNlcnRpZmljYXRlIEF1dGhvcml0
eTEzMDEGA1UEAxQqQVQmVCBGb3VuZHJ5IEF0bGFudGEgQ2VydGlmaWNhdGUgQXV0
aG9yaXR5MR0wGwYJKoZIhvcNAQkBFg5tajM1ODBAYXR0LmNvbTCCASIwDQYJKoZI
hvcNAQEBBQADggEPADCCAQoCggEBALLnf1Fxhld4E5/EDAW0h/3ZIb1gN5Zx8ZDc
9Jp3Xpt39few/rO6I2yNDZDBiISPhYTL3MvByAj971bLRbvp4yqMz97D/Fvzrm9E
FPTBye7pfa7BP9dBM1mshQ/7TB6fDx6jfgsCspEuQpIQJMfcy7R911jNbmstetYS
EirnpbyMPx2N3leRcSbmldZtW9sAep9hPqBQZfxCVD5WsYdsmxx6ppwuR4Oogno+
3uVcBosU3s8AezL2tTZ5dtweE5dcfIrbXbE+Cs/9GO3KKxHxFmto/TNo4TqIPVYq
o3yKNAMf9drrmBiJVkhpG+5tTa2/UB5Va/XI9qBKO/8iQw5nLy0CAwEAAaOCAREw
ggENMAwGA1UdEwQFMAMBAf8wHQYDVR0OBBYEFL05Q9KTYs7R+aZ0jukg3EE45KnC
MIHdBgNVHSMEgdUwgdKAFL05Q9KTYs7R+aZ0jukg3EE45KnCoYG2pIGzMIGwMQsw
CQYDVQQGEwJVUzELMAkGA1UECBMCR0ExIDAeBgNVBAoUF0FUJlQgRm91bmRyeSBB
dGxhbnRhIENBMR4wHAYDVQQLExVDZXJ0aWZpY2F0ZSBBdXRob3JpdHkxMzAxBgNV
BAMUKkFUJlQgRm91bmRyeSBBdGxhbnRhIENlcnRpZmljYXRlIEF1dGhvcml0eTEd
MBsGCSqGSIb3DQEJARYObWozNTgwQGF0dC5jb22CAQAwDQYJKoZIhvcNAQEFBQAD
ggEBAJgUgitXd2CFMsWRPLTf2JZbl6LaPYgSVMBc5aBH6xpMfSjQMXFgh134uQzl
iBOd6P9WDneW8N7lABksG/aS7sHTYOisUUlYbCjQdPgo+cm0i4WDXhMN5027TRim
eEo+E+Ge5XEGMTpLUNTN8lncHQvwg7XIYt7NDaQFFDMG25ZUHG2BR7K035fxBLEE
xWx6avSfPkUvlEoVNaiiY1cSr3m1L8GT608zFA6hRqkgAKHtAFNeUfrmlszUBskx
1ea9ij+sr6w92Nluwe5S/uAX8tfAYT+PTvD0+3q2BEwQyVqQhAa+qq8FKfOqxKIX
ufO7tbRNg4POypiXSOabbFfvS+0=
-----END CERTIFICATE-----
EOF
```


Apply the addition of the cert.  Should say "1 cert added"
```
update-ca-certificates
```

Allow local non-root user to manage docker, and restart.
```
# replace foundry with your local login user
usermod -aG docker foundry

systemctl restart docker
```



## Run this section on a SINGLE HOST. Just from master0


### Prepare k8s certs. 

Construct all the certs from one host in the working directory, using the json files as templates.
```
cd ~/foundry-k8s-cluster/pki-working/
```

Manually download cfssl toolkit as its not on apt.  install in /usr/local/bin
```
curl -o /usr/local/bin/cfssl https://pkg.cfssl.org/R1.2/cfssl_linux-amd64
curl -o /usr/local/bin/cfssljson https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64
chmod 755 /usr/local/bin/cfssl*
```


Edit kube-apiserver-csr.json to reflect local environment IP and hostnames
leave references to masterX, kubernetes, and 10.96 ip addresses.  
Under the section hosts, verify the hostnames master0, master1, and master2 remain, the many kubernetes aliases remain, and 10.96.0.1.
TODO: script this
```
vi kube-apiserver-csr.json
```

CA for apiserver, kubelet, kubectl
```
cfssl gencert -initca ca-csr.json | cfssljson -bare ca
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-apiserver-csr.json | cfssljson -bare kube-apiserver
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-apiserver-kubelet-client-csr.json | cfssljson -bare kube-apiserver-kubelet-client
```

CA for front proxy
```
cfssl gencert -initca front-proxy-ca-csr.json | cfssljson -bare front-proxy-ca
cfssl gencert -ca=front-proxy-ca.pem -ca-key=front-proxy-ca-key.pem -config=ca-config.json -profile=kubernetes front-proxy-client-csr.json | cfssljson -bare front-proxy-client
```

Just a simple private/public key for service account
```
openssl genrsa -out sa.key 2048
openssl rsa -in sa.key -outform PEM -pubout -out sa.pub
```


Rename keys/certs/csr so kubeadm below is happy. it expects the files to be named a certain way
```
mv ca.pem ca.crt
mv ca-key.pem ca.key
mv kube-apiserver.pem apiserver.crt
mv kube-apiserver-key.pem apiserver.key
mv kube-apiserver.csr apiserver.csr
mv kube-apiserver-kubelet-client.pem apiserver-kubelet-client.crt
mv kube-apiserver-kubelet-client-key.pem apiserver-kubelet-client.key
mv kube-apiserver-kubelet-client.csr apiserver-kubelet-client.csr
mv front-proxy-ca-key.pem front-proxy-ca.key
mv front-proxy-ca.pem front-proxy-ca.crt
mv front-proxy-client-key.pem front-proxy-client.key
mv front-proxy-client.pem front-proxy-client.crt
```


Copy all the keys/certs to all 3 hosts from master0
```
cd ..
scp pki-working/* foundry@master1:~/foundry-k8s-cluster/pki-working/
scp pki-working/* foundry@master2:~/foundry-k8s-cluster/pki-working/
```




## Run this section on ALL 3 HOSTS.  master0, master1, and master2

Create k8s pki dir and copy created certs on all 3 hosts
```
cd ~/foundry-k8s-cluster
mkdir -p /etc/kubernetes/pki
cp pki-working/* /etc/kubernetes/pki
```


### Install master etcd manifests

Copy to each respective master host its one corresponding master etcd yaml file. 
master0 should get master0-etcd.yaml,  master1 gets master1-etcd.yaml etc. 
Do not give any one master multiples etcd yaml files!
TODO: Script this

```
# master0
cp master0-etcd.yaml /etc/kubernetes/manifests/
# master1
cp master1-etcd.yaml /etc/kubernetes/manifests/
# master2
cp master2-etcd.yaml /etc/kubernetes/manifests/
```

### Kubeadm config setup

EDIT kubeadm-config-v2.yaml to reflect local environment IP and hostnames
Under the section apiServerCertSANs verify the hostnames master0, master1, and master2 remain. 
Leave 127.0.0.1, replace the other IP addresses with the 3 for your environment.  
Add in your 3 master's IP addresses and pre-existing hostnames.
TODO script this
```
vi kubeadm-config-v2.yaml
scp kubeadm-config-v2.yaml foundry@master1:~/foundry-k8s-cluster/
scp kubeadm-config-v2.yaml foundry@master2:~/foundry-k8s-cluster/
```


### Manual kubeadm phase step execution

Use kubeadm executing each step discretely on each host rather than the typical "init" all at once.  

```
kubeadm alpha phase kubelet config write-to-disk --config kubeadm-config-v2.yaml
kubeadm alpha phase kubelet write-env-file --config kubeadm-config-v2.yaml
kubeadm alpha phase kubeconfig all --config kubeadm-config-v2.yaml
kubeadm alpha phase controlplane all --config kubeadm-config-v2.yaml
```


### Start kubelet

This starts the default manifest pods on each host.
```
systemctl start kubelet
```

Wait until docker shows the needed containers are running and stable (up for more than 5 minutes)
```
# full docker container list with all columns
docker ps

# 2 second refresh
watch -n2 docker ps
```

Wait till all 3 hosts are stable with these 4 containers
each master should have its own individual etcd, master0, master1, and master2
```
  "kube-apiserver --en…" Up About a minute
  "etcd --name=master0…" Up 13 minutes
  "kube-scheduler --le…" Up 13 minutes
  "kube-controller-man…" Up 14 minutes
```


### Troubleshoot as needed

Run inspect to get the containers configuration state.  Look for LogPath to find the container's logging
```
docker logs <container-id> 
docker inspect <container-id> 
```

Check /var/log/syslog as kubelet will log there its attempts and running the static containers in /etc/kubernetes/manifests


## Run this section on a SINGLE HOST. Just from master0

### Proceed with final kubeadm steps

Token creation, config upload into the cluster itself.  And the installation of dns and proxy containers.  Only needs to be run from one host given the results of this end up in k8s etcd (and is clustered).
```
kubeadm config upload from-flags 
kubeadm alpha phase bootstrap-token cluster-info /etc/kubernetes/admin.conf
kubeadm alpha phase bootstrap-token node allow-post-csrs 
kubeadm alpha phase bootstrap-token node allow-auto-approve
kubeadm token create --config kubeadm-config-v2.yaml
kubeadm alpha phase addons coredns --config kubeadm-config-v2.yaml
kubeadm alpha phase addons kube-proxy --config kubeadm-config-v2.yaml
```


Create the needed local config for kubectl to be able to work
```
mkdir ~/.kube/
cp /etc/kubernetes/admin.conf ~/.kube/config
chown -R foundry:foundry /home/foundry
```


### Verify

Verify kubectl works and you can see default pods.  Its normal for kube-dns or coredns to say Pending as there is no CNI networking yet
```
kubectl get pod --all-namespaces -o wide
```

Scale up dns add node balancing affinity
```
kubectl apply -f coredns-deployment-updated.yaml
```

### Install Container Networking.  

Setup container networking.  Use prepped/saved yaml from calico.  Alternatively you can pull these from calico's website https://docs.projectcalico.org/v3.1/getting-started/kubernetes/installation/calico
```
kubectl apply -f calico-rbac-kdd.yaml
kubectl apply -f calico-3.1.3-k8setcd.yaml
```




## Run this section on ALL 3 HOSTS.  master0, master1, and master2

This was already done on master0, do on the other 2 masters so kubectl works on them if needed
```
mkdir ~/.kube/
cp /etc/kubernetes/admin.conf ~/.kube/config
chown -R foundry:foundry /home/foundry
```

## VERIFY

DO NOT PROCEED UNTIL ALL 3 HOSTS can resolve the dig command below.
Verify ALL PODS are running
```
kubectl get pods --all-namespaces -o wide
dig kubernetes.default.svc.cluster.local @10.96.0.10
kubectl run -i --tty network-utils --image=amouat/network-utils --restart=Never --rm=true -- dig kubernetes.default.svc.cluster.local
```



## Run this section on a SINGLE HOST. Just from master0
At this point most verifying, kubectl running, helm installing can occur from master0.  But the others could run it if the 
correct files were put in place.

### Install tools 

Install calicoctl and etcdctl for verification and if needed for debug purposes later
```
wget https://github.com/projectcalico/calicoctl/releases/download/v2.0.5/calicoctl
kubectl cp kube-system/master0-etcd-$(hostname):/usr/local/bin/etcdctl .
chmod 755 etcdctl calicoctl
mv etcdctl calicoctl /usr/local/bin/
```

Verify etcd health. Lots of output is good
```
export ETCDCTL_API=3
etcdctl --endpoints http://127.0.0.1:2379 get /registry --prefix -w fields
```

Verify calico bgp peering
```
ETCD_ENDPOINTS=http://127.0.0.1:2379 calicoctl node status
```


### Install helm

Copy helm binary onto host system.  
```
wget https://storage.googleapis.com/kubernetes-helm/helm-v2.9.1-linux-amd64.tar.gz
mkdir helm-unpack
cd helm-unpack/
tar -zxvf ../helm-v2.9.1-linux-amd64.tar.gz
cp linux-amd64/helm /usr/local/bin/
cd ..
```

Apply helm role and start helm tiller
```
kubectl apply -f helm-role.yaml
helm init --service-account tiller
export HELM_HOME=/home/foundry/.helm
helm repo add incubator https://kubernetes-charts-incubator.storage.googleapis.com/
helm repo update

# Reset non-root user permissions back properly
chown -R foundry:foundry /home/foundry
```

Verify helm/tiller is running
```
kubectl get pods --all-namespaces -o wide |grep tiller

helm list
# should be empty


helm repo list

# should show 2 or 3 repos
NAME     	URL
stable   	https://kubernetes-charts.storage.googleapis.com
local    	http://127.0.0.1:8879/charts
incubator	https://kubernetes-charts-incubator.storage.googleapis.com/
```

## Finished

At this point you have a basic 3 server k8s cluster where each master can take workloads.
From here you can install basic voltha or full seba pod using helm.  



