#!/bin/bash

function getBrokerId()
{
local RC=1
local ZK_ROOT_PATH="${1}"
local CONTAINER_ID="${2}"
local PREV_BROKER_ID="${3}"
local BROKER_ID=0
local DATE=$( /bin/date )
local stamp

    stamp=$( /usr/bin/stat -c "%Y" "${KAFKA_HOME}/logs/server.log" )
    if [ "${stamp}" -ne "${STAMP}" ]; then
#      echo "Update"
      RC=0
      STAMP="${stamp}"
#      BROKER_ID=$( /usr/bin/awk -F ']' "/Group Metadata Manager on Broker/ { split(\$2, b, \" \"); print b[7]; exit }" "${KAFKA_HOME}/logs/server.log" )
# There's a better way to look up the BROKER_ID...
      BROKER_ID=$( /usr/bin/awk -F '=' "/broker\.id=/{ print \$2 }" /kafka/kafka-logs-${CONTAINER_ID}/meta.properties )

      if [ ${BROKER_ID} -ne 0 ]; then
        if [ ${PREV_BROKER_ID} -ne ${BROKER_ID} ]; then
          zk_cleanup "${ZK_ROOT_PATH}/${CONTAINER_ID}/brokers/${PREV_BROKER_ID}"
        fi
        zk_ensure "${ZK_ROOT_PATH}/${CONTAINER_ID}/brokers/${BROKER_ID}"
        zk_set "${ZK_ROOT_PATH}/${CONTAINER_ID}/brokers/${BROKER_ID}" "{\"heartbeat\":\"${DATE}\"}"
      fi
    fi
    echo "${BROKER_ID}"
    return ${RC}
}

function zk_set()
{
local ZK_PATH="${1}"
local VALUE="${2}"
local KLUDGE_VALUE

# FIXME: Someone would eventually patch the zookeeper-shell to allow escaping spaces...
  KLUDGE_VALUE=$( echo "${VALUE}" | sed -e 's/ /_/g' )
  "${ZK_SHELL}" "${KAFKA_ZOOKEEPER_CONNECT}"<<EOS 2>&1 > /dev/null
set ${ZK_PATH} ${KLUDGE_VALUE}
close
quit
EOS
}

# Ensure path
function zk_ensure()
{
local IFS
local PREV_IFS
local ZK_PATH
local p
local l="create "
local t

  PREV_IFS=${IFS}
  IFS=/
  ZK_PATH=( $@ )
  IFS=${PREV_IFS}
#  echo ${#ZK_PATH[@]}
  for p in ${ZK_PATH[@]}; do
     l="${l}/${p}"
#    echo $r
    if [ -z ${t} ]; then
      t=${l}
    else
      t=$( printf "%s \"\"\n%s" $t $l )
    fi   
  done

# acl = ip:0.0.0.0:cdwra
# WRITE/ADMIN. CREATE and DELETE broken out of WRITE
  "${ZK_SHELL}" "${KAFKA_ZOOKEEPER_CONNECT}"<<EOS 2>&1 > /dev/null
${t} ""
close
quit
EOS
}

# Cleanup after a crash
function zk_cleanup()
{
local ZK_PATH="${1}"

  "${ZK_SHELL}" "${KAFKA_ZOOKEEPER_CONNECT}"<<EOS 2>&1 > /dev/null
rmr ${ZK_PATH}
close
quit
EOS
}

cleanup()
{
local ZK_ROOT_PATH="${1}"
local CONTAINER_ID="${2}"

  zk_cleanup "${ZK_ROOT_PATH}/${CONTAINER_ID}"
  exit 0
}

STAMP=0
BROKER_ID=0
CONTAINER_ID="${HOSTNAME}"
ZK_SHELL="${KAFKA_HOME}/bin/zookeeper-shell.sh" 
WATCH_PID="${1:-"1"}"
ZK_ROOT_PATH=${2:-"/dockerized"}
SLEEP_TIME="${3:-"180"}"

#echo "${0} [WATCHPID] [/ZK_ROOT_PATH] [SLEEP_TIME]"

trap "cleanup ${ZK_ROOT_PATH} ${CONTAINER_ID}" SIGINT SIGTERM SIGHUP EXIT 

zk_cleanup "${ZK_ROOT_PATH}/${CONTAINER_ID}"
zk_ensure "${ZK_ROOT_PATH}/${CONTAINER_ID}"
zk_set "${ZK_ROOT_PATH}/${CONTAINER_ID}" "{\"virthostip\":\"${KAFKA_VIRT_HOST_IP}\"}"

while true; do
  if kill -0 "${WATCH_PID}"; then
    BROKER_ID=$( getBrokerId ${ZK_ROOT_PATH} ${CONTAINER_ID} ${BROKER_ID} )
  else
    # Looks like the process is dead... 
    break
  fi
  sleep ${SLEEP_TIME} &
  # To allow the script cleanup when shutting down the machine, we let deliver the signals asynchronously
  wait ${!}
done

zk_cleanup "${ZK_ROOT_PATH}/${CONTAINER_ID}"

exit 0
