#!/bin/sh

set -a

if [ -r ./defaults.config ]; then
  . ./defaults.config
fi

. lib/funcchecks.shlib
. lib/docker.shlib
. lib/compose.shlib

if [ ${#} -lt 1 ]; then
  echo ${0} host numbrokers 
#  echo ${0} brokerID1 brokerID2 ... borkerIDN
  exit 1
fi

HOST="${1}"

kafka_scale_up "${HOST}" "${2}"
BROKERLIST=$( lib/recentdocks.py -z "${ZK_DOCKER_ROOT} -i "${DOCKER_IMAGE_TAG}" -t "${BROKERTIMEOUT}" -H "${HOST}" ) 
for B in "${BROKERLIST}"; do
  BROKERLISTCS="${BROKERLISTCS},${B}"
done

# Move replicas 
#cat <<EOJ>>"${JSONFILE}"
#{"partitions":
#             [{"topic": "devopstest",
#               "partition": 1,
#               "replicas": [1,2,4] }],              
#              }],
#  "version":1
#}
#EOJ
#${KAFKA_HOME}/kafka-reassign-partitions.sh --manual-assignment-json-file "${JSONFILE}" --execute

BACKUPJSONFILE=$( mktemp -t XXXXrollback_partitions.json )
LOGFILE=$( mktemp -t XXXXrollback_partititons.log )
JSONFILE=$( mktemp -t XXXXXtopics-to-move.json )

cat <<EOJ>>"${JSONFILE}"
{"topics":
     [{"topic": "devopstest"}],
     "version":1
}
EOJ

${KAFKA_HOME}/bin/kafka-reassign-partitions.sh --topics-to-move-json-file "${JSONFILE}" --broker-list "${BROKERLISTCS}" --execute
if [ ${?} ]; then
  echo Executing partition reassignment failed with exit code ${?}. 
  exit 1
fi

status_loop "${LOGFILE}" "${JSONFILE}" "${BACKUPJSONFILE}"
if [ ! ${?} ]; then
  echo "Partition reassignment failed with exit code ${?}."
  exit 1
fi

# Allow for the brokers to get ready
sleep ${BROKERTIMEOUT}
# Do functional checks
for b in "${BROKERLIST}"; do
  check_broker ${b}
  last_broker=${b}
  if [ ! $? ]; then
    echo "Broker check failed for ${b} with exit code ${?}."
  fi
done

sh ${KAFKA_HOME}/bin/kafka-preferred-replica-election.sh --zookeeper "${ZK_LIST}"

# Do functional checks for cluster as a whole
check_cluster ${last_broker}
if [ ! $? ]; then
  echo "Cluster check failed with exit code ${?}."
  exit 1
fi
 
rm -f "${JSONFILE}" 
exit 0

