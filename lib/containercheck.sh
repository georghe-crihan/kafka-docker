#!/bin/sh

set -a
if [ -r ./defaults.config ]; then
  . ./defaults.config
fi

. lib/docker.shlib

for B in $( lib/zkbrokerlist.py ); do
  H=$( docker_host_from_broker_id "${B}" )
  CP=$( docker_container_id_port_from_broker_id "${B}" )
  P=${CP#* }
  C=${CP% *}
  echo Checking container ${C} at ${H}:${P}...
  lib/brockercheck.py ${H}:${P} 
done

exit 0
