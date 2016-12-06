#!/usr/bin/env python

from sync_producer import Producer 
from sync_consumer import Consumer
from kazoo.client import KazooClient
from zk_tools import listBrokers
from os import environ
from sys import argv, exit

p = None
c = None

def check_broker(t, b, m, debug=None):
    p = Producer(t,b)
    rc, resp = p.produce(m, "ack")
    offset=resp[0].offset
    p.close()
    c = Consumer(t, b, m, debug)
    rc, resp = c.broker()
    if (offset==resp.offset) and (rc == 0):
      print "OK offset=", resp.offset
    else:
      print "FAILED offset=", resp.offset
    c.close()
    return rc

try:
  zk = KazooClient(hosts=environ['ZK_LIST'], read_only=True)
  zk.start()

  if len(argv) > 1:
    rc = check_broker("container", argv[1], "containerping", True)
  else:
    last_broker=0
    for b in listBrokers(zk):
      last_broker = b
      print "Checking broker " + str(b)
      rc = check_broker("broker", b, "ping")

    print "Checking whole cluster"
    p = Producer("cluster",last_broker)
    p.produce("clusterping", "ack") 
    p.close()
    c = Consumer("cluster", last_broker, "clusterping")
    rc, resp = c.cluster()

except:
  if p: p.close()
  if c: c.close()
  zk.stop()
  exit(1)

c.close()

if rc == 0:
  print "OK"
else:
  print "FAILED"

zk.stop()
exit(0)
