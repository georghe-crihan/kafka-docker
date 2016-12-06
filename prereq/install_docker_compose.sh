#!/bin/bash

if [ ! -x /opt/bin/docker-compose ]; then
  sudo mkdir -p /opt/bin
  sudo curl -L "https://github.com/docker/compose/releases/download/1.9.0/docker-compose-$(uname -s)-$(uname -m)" -o /opt/bin/docker-compose
  sudo chmod +x /opt/bin/docker-compose
fi

#if [ ! -x /opt/bin/docker-machine ]; then
#  sudo curl -L https://github.com/docker/machine/releases/download/v0.8.2/docker-machine-`uname -s`-`uname -m` -o /opt/bin/docker-machine
#  sudo chmod +x /opt/bin/docker-machine
#fi
