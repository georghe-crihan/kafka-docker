from kazoo.client import KazooClient
from os import environ
from json import loads 

# Get broker on a host
def get_broker(zk, broker):
  try:
    if not zk:
      _zk = KazooClient(hosts=environ['ZK_LIST'], read_only=True)
      _zk.start()
    else:
      _zk = zk

    path="/brokers/ids/" + str(broker)
    if _zk.exists(path):
      n,znstat=_zk.get(path)
      bd = loads(n)
      h=bd["host"]
      p=bd["port"]
  except:
#    if not zk: _zk.stop()
    return

  if not zk: _zk.stop()

  if h:
    return str(h) + ':' + str(p)  

  return

def listBrokers(zk):
  return zk.get_children("/brokers/ids", False)

def listTopics(zk):
  return zk.get_children("/brokers/topics")

def listPartitions(zk, topic):
  path = "/brokers/topics/" + topic + "/partitions"
  if zk.exists(path):
    return zk.get_children(path)
#  else: 
#    raise KafkaException("Topic " + topic + " doesn't exist")

def getLeaderAddress(zk, topic, partitionId):
  path = "/brokers/topics/" + topic + "/partitions/" + str(partitionId) + "/state"
  if zk.exists(path):
    stateN = zk.get(path)
    stateDic = loads(stateN[0])
    leaderId = stateDic["leader"]
    return get_broker(zk, leaderId)
#  else:
#    raise KafkaException("Topic (" + topic + ") or partition (" + partitionId + ") doesn't exist")

