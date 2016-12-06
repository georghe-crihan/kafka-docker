#!/usr/bin/env python3.5

# Get a list of recent docks added on a host. Assume both brokers and dockmon need timeout to catch up 
# Python 3.5 required by docker-py

from docker import Client
from datetime import datetime 
from time import mktime, sleep
from logging import basicConfig
from sys import exit, argv
from kazoo.client import KazooClient
from os import environ
from json import loads
from getopt import getopt, GetoptError

def getDockInfo(debug, host, image, timediff):
  container_id = 0
  containers = [ ]

  # Use the docker utilities here to get the mapping.
  cli = Client(base_url=host)
  for ps in cli.containers(filters={ "status": "running" }):
    if ps['Image'] == image:
      names = ps['Names']
      name0 = names[0]
      ports = ps['Ports']
      port0 = ports[0]
      stripnanoseconds = int(ps['Created']) #// 1000000000
      today = datetime.today()
      td = int((mktime(today.timetuple())) + today.microsecond/1000000.0)
      d = td - stripnanoseconds
      if port0['Type'] == 'tcp' and d <= timediff or debug > 0:
        if debug > 0:
          print(name0, str(d), port0['IP'], ps['Id'])
        containers.append(ps['Id'])
        if debug > 1:
          print(ps)
          break

  return containers 

def convert_dockid_to_brokerlist(debug, zk, zk_path, docklist):
  brokers = [ ]

  for dock in zk.get_children(zk_path):
    data, zn = zk.get(zk_path + '/' + dock)
    d = loads(data.decode('utf-8'))
    if 'dockInfoUpdated' in d:
      if d['imageId'] in docklist:
        broker = zk.get_children(zk_path + '/' + dock + '/brokers')
        # TODO: Currently one broker per dock is assumed
        if debug > 0:
          print(dock, broker[0])
        brokers.append(broker[0])

  return brokers

def usage(argv):
  print("%s [-h] [-timeout sec] [-verbose] [-i image-tag] [-HOST ip] [-Z /zk_root]" % argv[0])

try:
  zk_hosts = environ["ZK_LIST"]
except KeyError:
  zk_hosts = "zookeeper"

try:
  opts, args = getopt(argv[1:], "hi:t:vH:Z:", ["help", "image-tag=", "timeout=", "verbose", "HOST=", "ZK_ROOT="])
except GetoptError as err:
  print(str(err))
  usage(argv)
  exit(2)

zk = KazooClient(hosts=zk_hosts)
zk.start()

debug = 0
# It's assumed reasonable to give 5 minutes to a kafka dock to become fully ready.
timeout = 300
zk_root = '/dockerized'
image = 'k_kafka'
host = ''

for o, a in opts:
  if o in ('-v', '-verbose'):
    debug = debug + 1
  elif o in ('-t', '--timeout'):
    timeout = int(a)
  elif o in ('-H', '--HOST'):
    host = a
  elif o in ('-i', '--image-tag'):
    image = a
  elif o in ('-h', '--help'):
    usage(argv)
    exit(0)
  elif o in ('-Z', '--ZK_ROOT'):
    zk_root = a
  else:
    assert False, "unhandled option"

if not host:
  usage(argv)
  exit(2)

containers = getDockInfo(debug, host, image, timeout)
# Make sure the dockmon catches up the brokers' info
sleep(timeout)
brokers = convert_dockid_to_brokerlist(debug, zk, zk_root, containers)
print(' '.join(brokers))
zk.stop()
exit(0)
