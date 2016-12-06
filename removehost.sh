#!/bin/bash
# Supports multibroker hosts, though extremely slow at the moment, should rewrite
# kafka-move-leadership.sh to generate batch config 

set -a
if [ -r ./defaults.config ]; then
  . ./defaults.config
fi

. lib/funcchecks.shlib 
. lib/docker.shlib

function decom_host()
{
local H="${1}"
local B="${2}"

# Do whatever is needed to decom the host

# do functional test for the whole cluster
  check_cluster ${B}
  return ${?}
}

if [ ${#} -lt 3 ]; then
  echo "${0} host first-broker-id last-broker-id"
  exit 1
fi

#for B in $( lib/zkbrokerlist.py ${1} ); do
for B in $( docker_brocker_id_container_id_from_host ${1} ); do
  b=${b% *}
  c=${b#* }
  PROPFILE=$( printf ${PROPFILEFORM} ${b} )
  ./removebroker.sh ${PROPFILE} ${b} ${2} ${3}
  if [ ! ${?} ]; then
    echo Removing the broker failed with exit code ${?}. 
    exit 1
  fi
done

decom_host "${1}" "${2}"
if [ ! ${?} ]; then
  echo "Host decomission for ${1} failed with exit code ${?}."
  exit 1
fi

exit Host decomission for ${1} successful.
exit 0

