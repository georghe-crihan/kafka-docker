#!/bin/sh

set -a
if [ -r defaults.config ]; then
  . ./defaults.config
fi

. lib/status.shlib
. lib/funcchecks.shlib
. lib/docker.shlib
. lib/compose.shlib

function decom_broker()
{
local KILLBROKER="${1}"
local PROPFILE="${2}"
local FIRSTBROKER="${3}"
local R="${4}"
local H
local C

# Do whatever is needed to decom the broker.
  H=$( docker_host_from_broker_id "${KILLBROKER}" )
  C=$( docker_container_id_from_broker_id "${KILLBROKER}" )
  docker --host=$( getdogckersock "${H}" ) stop "${C}"
  if [ ! ${?} ]; then
    echo Docker container stop failed with exit code ${?}.
    return ${?}
  fi 
  sh ${KAFKA_HOME}/bin/kafka-preferred-replica-election.sh --zookeeper "${ZK_LIST}"
# do functional test for the whole cluster 
  check_cluster ${FIRSTBROKER}

# Ammend the scale file
  kafka_scale_down "${H}" "1"

# Optionally, remove the container
  if [ ! -z "${R}" ]; then
    /opt/bin/docker-compose --host $( getdockersock "${H}" ) -f $( get_docker_compose_template "${H}" ) rm -f
  fi
  return ${?}
}

if [ ${#} -lt 3 ]; then
  echo "${0} kill-broker-id first-broker-id last-broker-id [--remove-container]"
  exit 1
fi

JSONFILE=$( mktemp -t XXXXreassign_partitions.json )
BACKUPJSONFILE=$( mktemp -t XXXXXrollback_partitions.json )
LOGFILE=$( mktemp -t XXXXrollback_partititons.log )
PROPFILE=$( printf "${PROPFILEFORM}" ${1} )

lib/kafka-move-leadership.sh --broker-id ${1} --first-broker-id ${2} --last-broker-id ${3} --zookeeper "${ZK_LIST}" > "${JSONFILE}" 
if [ ! ${?} ]; then
  echo Generating new partition assignment failed with exit code ${?}.
  exit 1
fi

${KAFKA_HOME}/bin/kafka-reassign-partitions.sh --zookeeper "${ZK_LIST}" --reassignment-json-file "${JSONFILE}" --execute > "${BACKUPJSONFILE}"
if [ ! ${?} ]; then
  echo Executing partition reassignment failed with exit code ${?}.
  exit 1
fi

status_loop "${LOGFILE}" "${JSONFILE}" "${JSONBACKUPFILE}"
if [ ! ${?} ]; then
# Do decomission
  decom_broker "${1}" "${PROPFILE}" "${2}" "${4}"
  if [ ! ${?} ]; then
    echo "Broker decomission for ${1} failed with exit code ${?}." 
    exit 1
  fi 
else
  echo "Partition reassignment for ${1} failed with exit code ${?}."
  exit 1
fi

echo "Successful broker ${1} decomission."
exit 0
