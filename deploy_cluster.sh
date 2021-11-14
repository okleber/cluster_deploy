#!/usr/bin/env bash
n=5
for i in $(seq ${n}) ; do
echo $(date) $@
sleep 1
done
