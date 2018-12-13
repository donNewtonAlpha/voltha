#!/bin/bash

CID=$1

PID=$(docker inspect --format {{.State.Pid}} $CID)
echo $PID

