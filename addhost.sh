#!/bin/bash

set -a
if [ -r ./defaults.config ]; then 
  . ./defaults.config
fi

. lib/docker.shlib
. lib/compose.shlib

if [ -z "${1}" ]; then
  echo ${0} virthostip
else
  H="${1}"
  echo "Generating compose template for ${H}..."
  bootstrap_host "${H}"
  
#  echo 'systemctl start kafka-docker.service start' | ssh ${H}
fi

exit 0

