#!/bin/bash

CID=$1

PID=$(docker inspect --format {{.State.Pid}} $CID)
nsenter --target $PID --mount --uts --ipc --net --pid

