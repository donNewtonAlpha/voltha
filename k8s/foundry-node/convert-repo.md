# Convert "insecure" access to foundry docker repo to TLS secured

This assumes you have been running an "insecure" Foundry docker repo using http. These notes will convert that installation to secure using https.  This requires the installation of a trusted CA certificate on the system running docker.


Run the following as root till told otherwise
```
sudo bash
```

Stop docker/kubelet as this is a global change.  This may take a while
```
systemctl stop docker
systemctl stop kubelet
```

Remove old insecure repo exception by deleting the entire docker config file. Or edit and remove the insecure lines:
```
rm /etc/docker/daemon.json
# or
vi /etc/docker/daemon.json
```

Install the AT&T Foundry Atlanta CA cert at the system level.
```
cat <<EOF > /usr/local/share/ca-certificates/att-foundry-atlanta-ca.crt
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

Restart services.  This will restart all containers/pods.  Can take a while
```
systemctl start docker
systemctl start kubelet
```

No longer run as root
```
exit
```


Test local CA approves https server cert
```
curl -v https://docker-repo.dev.atl.foundry.att.com:5000/v2/_catalog
```

Test docker pull
```
docker pull docker-repo.dev.atl.foundry.att.com:5000/ubuntu:16.04
```

