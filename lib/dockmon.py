#!/usr/bin/env python3.5

from __future__ import with_statement
from threading import Lock
from daemon import Daemon
from docker import Client
from logging import basicConfig
from kazoo.client import KazooClient
from os import environ
from sys import argv, exit
from time import sleep
from json import loads,dumps
from signal import signal, SIGTERM
from getopt import getopt, GetoptError

docklist_lock = Lock()
zk_lock = Lock()

def process_removed(docks):
    print("Removed: ", docks)

def handler(signum, frame):
  global daemon
  daemon.cleanup()
  exit(0)

def getDockInfo(host, image, dock):
  public_port = 0
  container_id = 0

  print("Host: %s, dock: %s" % (host, dock))
  # Use the docker utilities here to get the mapping.
  cli = Client(base_url=host)
  for ps in cli.containers(filters={ "status": "running" }):
    if ps['Image'] == image:
      names = ps['Names']
      name0 = names[0]
      ports = ps['Ports']
      port0 = ports[0]
      if port0['Type'] == 'tcp' and ps['Id'].startswith(dock):
        if debug > 1:
          print(name0, port0['IP'], port0['PublicPort'], ps['Id'])
        public_port = port0['PublicPort']
        container_id = ps['Id']

  return (public_port, container_id) 

def process_added(docks):

  print("Added: ", docks)
  global daemon 
  daemon.update_zk_context(docks)


def watch_dock_list(docks, ev):

  print("Docks: %s" % docks)
  global daemon
  daemon.update_docklist(docks, ev)

##############################################################

class MyDaemon(Daemon):
  def __init__(self, zk_hosts, pid, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    self._zk_hosts = zk_hosts
    self._update_interval = 0
    self._zk = None
    self._docklist = [ ]
    self._image = ''
    self._zk_root = ''
    super().__init__(pid, stdin=stdin, stdout=stdout, stderr=stderr)

  def cleanup(self):
    with zk_lock:  
      self._zk.stop()

  # NOT THREAD-SAFE ASYNC CALLBACK (USED BY A GLOBAL)!!!
  def update_docklist(self, docks, ev):
    with docklist_lock:
      removed = set(self._docklist) - set(docks)
      added = set(docks) - set(self._docklist)
      self._docklist = docks
      if removed:
        process_removed(removed)
      if added:
        process_added(added)

  def bootstrap(self, zk_root, image, update_interval):
    self._image = image
    self._zk_root = zk_root
    self._update_interval = update_interval
    self._zk = KazooClient(hosts=self._zk_hosts)
    self._zk.start()
    self._zk.ChildrenWatch(self._zk_root, watch_dock_list, send_event=True)

  def update_zk_context(self, docks):
    with zk_lock:
      if not docks:
        docks = self._docklist
      for dock in docks:
        # Set port
        data, zns = self._zk.get(self._zk_root + '/' + dock)
        # FIXME: Underscore hack, due to a broken zookeeper-shell.sh
        t = loads(data.decode('utf-8'))
        if not 'dockInfoUpdated' in t and t:
          (port, imageId) = getDockInfo(t['virthostip'], self._image, dock)
          # TODO: Currently one broker per dock is assumed.
          t['dockInfoUpdated'] = True
          t['virtHostPort'] =  port
          t['imageId'] = imageId
          data = dumps(t).encode() 
          self._zk.set(self._zk_root + '/' + dock, data)

  def run(self):
    while True:
#      with zk_lock:
#        with docklist_lock:
          self.update_zk_context(self._docklist)
          sleep(self._update_interval)

    self.cleanup()

def usage(argv):
  print("usage: %s foreground|start|stop|restart [-help] [-image-tag image-tag] [-timeout timeout] [-zk_root /zk_root] [-verbose] " % sys.argv[0])

try:
  zk_hosts = environ["ZK_LIST"]
except KeyError:
  zk_hosts = "zookeeper"

try:
  opts, args = getopt(argv[2:], "hi:t:vz:", ["help", "image-tag=", "timeout=", "verbose", "ZK_ROOT="])
except GetoptError as err:
  print(str(err))
  usage(argv)
  exit(2)

debug = 0

# Every 5 minutes we update the context
update_interval = 300

image = 'k_kafka'
zk_root = '/dockerized'

if __name__ == "__main__":
	for o, a in opts:
		if o in ('-v', '-verbose'):
			debug = debug + 1
		elif o in ('-t', '--timeout'):
			update_interval = int(a)
		elif o in ('-i', '--image-tag'):
			image = a
		elif o in ('-h', '--help'):
			usage(argv)
			exit(0)
		elif o in ('-z', '--ZK_ROOT'):
			zk_root = a
		else:
			assert False, "unhandled option"

	global daemon
	daemon = MyDaemon(zk_hosts, '/tmp/dockmon.pid', stdout='/tmp/dockmon.log', stderr='/tmp/dockmon.log')
	if 'start' == argv[1]:
# In backround, handle SIGTERM to close ZK connection properly
		signal(SIGTERM, handler)
		daemon.bootstrap(zk_root, image, update_interval)
		daemon.start()
	elif 'stop' == argv[1]:
		daemon.stop()
	elif 'restart' == argv[1]:
		daemon.restart()
	elif 'foreground' == argv[1]:
		daemon.bootstrap(zk_root, image, update_interval)
		daemon.run()
		daemon.cleanup()
		exit(0)
	else:
		print("Unknown command %s" % argv[1])
		usage(argv)
		exit(2)

