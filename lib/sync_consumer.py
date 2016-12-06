#!/usr/bin/env python

# Patched version of kafka.client
from devopsclient import DevopsSimpleClient
from kafka import SimpleConsumer
from zk_tools import get_broker 
from sys import exit
import re

# To consume messages

class Consumer:
  def __init__(self, t, broker, pattern, debug=None):
    self._debug = debug 
    if t == "container":
      self._broker = broker
    else:
      self._broker = get_broker(None, broker)
    if not self._broker:
      exit(1)
    self._pattern = re.compile(pattern)
    self._client = None 

  def close(self):
    self._client.close()
  
  def broker(self): 
     # Test specific broker
     self._client = DevopsSimpleClient(self._broker, self._broker)
     consumer = SimpleConsumer(self._client, "devops-group", "devopstest1")
     for message in consumer:
         # message is raw byte string -- decode if necessary!
         # e.g., for unicode: `message.decode('utf-8')`
         if self._pattern.match(message.message.value):
           if self._debug:
             print(message.message.value)
           self._client.close()
           return (0, message)
         else:
           self._client.close()
           return (1, None)

  def cluster(self):
     rc = 1 
     # Test cluster as a whole
     self._client = DevopsSimpleClient(self._broker)

     # Use multiprocessing for parallel consumers
     from kafka import MultiProcessConsumer

     # This will split the number of partitions among two processes
     consumer = MultiProcessConsumer(self._client, "devops-group", "devopstest1", num_procs=2)

     # This will spawn processes such that each handles 2 partitions max
     consumer = MultiProcessConsumer(self._client, "devops-group", "devopstest1",
                                partitions_per_proc=2)

     for message in consumer:
        if self._pattern.match(message.message.value):
           if self._debug:
              print(message.message.value)
           rc = 0

     for message in consumer.get_messages(count=5, block=True, timeout=4):
        if self._pattern.match(message.message.value):
           if self._debug:
             print(message.message.value)
           rc = 0
        else:
           rc = 2 

     self._client.close()
     return (rc, None)

if __name__=='__main__':
  from sys import argv


  if len(argv) < 4:
    print "lib/sync_consumer.py broker brokerid message"
    print "lib/sync_consumer.py container host:port message"
    print "lib/sync_consumer.py cluster borkerid message"
    exit(1)

  c = Consumer(argv[1], argv[2], argv[3])
 
  try:
    if (argv[1] == "broker") or (argv[1] == "container"): 
      rc, resp = c.broker()
    else:
      rc, resp = c.cluster()

  # Specific broker not available
  except ReplicaNotAvailableError:
    c.close()
    exit(3)

  # Something different happened
  except:
    c.close()
    exit(4)

  exit(rc)

