# Foundry Single instance kubernetes (k8s)
 
Minimum 8vcpu 8gb memory, 40GB disk.  NO SWAP.  kubernetes, kubelet, and kubeadm will not run with swap enabled.
And a basic install of Ubuntu 16.04, patched and updated

```
sudo apt update
sudo apt dist-upgrade
reboot
```

Disable swap if it was installed.  Left as an exersize to the reader on making this permanent and reclaiming the disk space.
```
swapoff -a
```



Add docker-ce gpg key and repo
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```


Add kubernetes gpg key and repo
```
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo add-apt-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
```

Install docker-ce, kubelet, kubeadm and kubectl from the newly added repos.
```
sudo apt update
sudo apt install docker-ce=17.03.3~ce-0~ubuntu-xenial kubelet=1.11.3-00 kubeadm=1.11.3-00 kubectl=1.11.3-00 kubernetes-cni=0.6.0-00 cri-tools=1.11.1-00 -y

sudo systemctl stop docker
sudo systemctl stop kubelet
```

Install the AT&T Foundry Atlanta CA cert at the system level.  The docker-repo hosted at the Foundry uses a cert signed by this CA.  Pulling images from that repo will require this.
```
sudo bash -c 'cat > /usr/local/share/ca-certificates/att-foundry-atlanta-ca.crt' << EOF
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
sudo update-ca-certificates
```

Startup docker and kubelet.  Kubelet will say loaded and exit-loop.  This is ok because there is no kube system pods running yet.  There will be soon enough.
```
sudo systemctl start docker
sudo systemctl start kubelet
sudo systemctl enable docker
sudo systemctl enable kubelet
sudo systemctl status docker
sudo systemctl status kubelet
```

Give a non-root user ability to manage docker
```
sudo usermod -aG docker <non-root-user>
```

## Intialize base k8s environment

Disable swap. kubelet nor kubeadm will run with it.
```
sudo swapoff -a
```

Run the kubeadm init.  This starts the k8s core pods and sets the configuration.  Can take a while as kube system docker images have to be downloaded.  You should save the output if you need to refer to it later.
```
sudo kubeadm init --pod-network-cidr=192.168.224.0/19
```


Make non-root user able to use kubectl
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```


## Install CNI and Verify basics

Verify kube system pods are up.  
```
kubectl get all --all-namespaces
```

Allow master node to run deployments
```
kubectl taint nodes --all node-role.kubernetes.io/master-

```

Git clone ATT voltha.  Contains known working container networking (calico) configuration
```
mkdir -p ~/source
cd ~/source
git clone https://github.com/donNewtonAlpha/voltha.git
cd ~/source/voltha/k8s/
```

Setup container networking.  Use prepped/saved yaml from calico.  Alternatively you can pull these from calico's website https://docs.projectcalico.org/v3.1/getting-started/kubernetes/installation/calico
```
kubectl apply -f foundry-node/foundry-k8s-cluster/calico-rbac-kdd.yaml
kubectl apply -f foundry-node/foundry-k8s-cluster/calico-3.1.3-k8setcd.yaml 
```


## Verify full k8s functionality

Everything should eventually become 'Running'
```
kubectl get pods --all-namespaces
kubectl get all --all-namespaces
```

Verify calico networking a dns
```
dig +short @10.96.0.10 kubernetes.default.svc.cluster.local
dig +short @10.96.0.10 SRV _https._tcp.kubernetes.default.svc.cluster.local
```


## Install helm

Copy helm binary onto host system.  
```
cd ~/source
wget https://storage.googleapis.com/kubernetes-helm/helm-v2.9.1-linux-amd64.tar.gz
mkdir helm-unpack
cd helm-unpack/
tar -zxvf ../helm-v2.9.1-linux-amd64.tar.gz
cp linux-amd64/helm /usr/local/bin/
cd ..
```

Apply helm role and start helm tiller
```
cd ~/source/voltha/k8s/
kubectl apply -f foundry-node/foundry-k8s-cluster/helm-role.yaml
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

At this point you have a basic single instance k8s.
From here you can install basic voltha or full seba pod using helm.  Or manually apply yaml files.

