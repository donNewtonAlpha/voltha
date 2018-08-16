#!/bin/bash

updfile=$1

if [ -n "$updfile" ]
then
  set -x
  curl -v --user onos:rocks -X POST -H "Content-Type: application/json" http://10.64.1.124:30120/onos/v1/network/configuration/ -d @$updfile
else
  echo "$0 <onos-netcfg-update-json file>"
fi
