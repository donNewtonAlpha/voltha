#!/bin/bash

NAMESPACE=$1
POD_NAME=$2

set -x
#kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath="{.status.hostIP} {.status.containerStatuses[*].containerID}{'\n'}"
kubectl get pod $POD_NAME -n $NAMESPACE -o jsonpath="{.status.containerStatuses[*].containerID}{'\n'}" | cut -d'/' -f3

