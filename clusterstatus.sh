#!/bin/sh

set -a
if [ -r ./defaults.config ]; then
  . ./defaults.config
fi

echo "Checking Zookeeper instances from ZK_LIST:"
lib/zkcheck.py
echo ${?}
echo "Checking Kafka brokers:"
lib/brockercheck.py
echo ${?}
echo "Checking virtual hosts and containers:"
lib/containercheck.sh
echo ${?}
