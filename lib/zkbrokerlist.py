#!/usr/bin/env python
# Get list of brokers on a host
from kazoo.client import KazooClient
from zk_tools import get_broker, listBrokers
from os import environ
from sys import argv, exit
from socket import gethostbyname

#if len(argv) < 2:
#  print "lib/zkbrokerlist.py [host]"
#  exit(1)

bl = []
rc = 1

try:
  zk = KazooClient(hosts=environ['ZK_LIST'], read_only=True)
  zk.start()

  if len(argv) > 1:
    for b in listBrokers(zk):
      h, p = get_broker(zk, b).split(':')
      host = gethostbyname(argv[1])
      if host == gethostbyname(h): 
        bl.append(b) 
  else:
    bl = listBrokers(zk)

  rc = 0
  zk.stop()

  print ' '.join(bl)

except:
  rc = 1

exit(rc)

