# Foundry Single instance kubernetes (k8s)
 
Minimum 8vcpu 8gb memory, 40GB disk. 
And a basic install of Ubuntu 16.04, patched and updated

```
sudo apt update
sudo apt dist-upgrade
reboot
```


Get docker-ce
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```


Get k8s
```
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo add-apt-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"

sudo apt update
sudo apt install docker-ce kubelet kubeadm kubectl -y

sudo systemctl stop docker
sudo systemctl stop kubelet
```

Install the AT&T Foundry Atlanta CA cert at the system level.
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

Startup docker and kubelet
```
sudo systemctl start docker
sudo systemctl start kubelet
sudo systemctl enable docker
sudo systemctl enable kubelet
sudo systemctl status docker
sudo systemctl status kubelet
# loaded is ok for kubelet. it will exit-loop until a k8s cluster is setup
```

```
sudo usermod -aG docker <non-root-user>
```

Add the k8s resolver into the top of the hosts resolver search list
The actual resolver will be installed below.  
Also lower the timeout and attempts so the system default resolver is attempted quicker
in the event the k8s resolver isnt responding.
```
sudo sh -c 'echo "nameserver 10.96.0.10" >> /etc/resolvconf/resolv.conf.d/head'
sudo sh -c 'echo "options ndots:5 timeout:1 attempts:1" >> /etc/resolvconf/resolv.conf.d/base'
sudo resolvconf -u
```


## Intialize base k8s environment

Disable swap. kubelet nor kubeadm with run with it.
```
sudo swapoff -a
```

Run the init
```
sudo kubeadm init --pod-network-cidr=192.168.0.0/16
```


Make non-root user able to use kubectl
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```


## Install CNI and Verify basics

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

Setup container networking.  Use prepped yaml from calico
```
kubectl apply -f foundry-node/foundry-k8s-cluster/calico-rbac-kdd.yaml
kubectl apply -f foundry-node/foundry-k8s-cluster/calico-3.1.3-k8setcd.yaml 
```




## Verify full k8s functionality

```
kubectl get pods --all-namespaces
kubectl get all --all-namespaces
```

Verify calico networking a dns
```
dig +short @10.96.0.10 kubernetes.default.svc.cluster.local
dig +short @10.96.0.10 SRV _https._tcp.kubernetes.default.svc.cluster.local
```

At this point you have a basic single instance kubernetes.  From here install helm or install basic voltha deployments.

