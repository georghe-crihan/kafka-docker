#!/bin/bash

# Script used to bootstrap a cluster
# Assumes the docker compose roots are exported from virthosts
# Assumes the [initial] scale for virthost has been set 
# NB: we run docker-compose in series, as opposed to parallel, to additionally
# make sure the compose-kafka-generated broker id's do not clash.

set -a
if [ -r ./defaults.config ]; then 
  . ./defaults.config
fi

. lib/docker.shlib
. lib/compose.shlib

for H in "${VIRTHOSTS}"; do
  echo "Generating compose template for ${H}..."
  bootstap_host "${H}"
#  echo 'systemctl start kafka-docker.service start' | ssh ${H}
done
exit 0

