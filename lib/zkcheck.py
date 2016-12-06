#!/usr/bin/env python

# NB: The below script is intended for testing the ZooKeeper itself.
# The Zookeeper API doesn't provide a way to find leader, hence the below script

import socket
from ip_tools import collect_hosts

'''
    leader_takes an array of (host:port) tuples and returns leader, array-of-followers,
    array-of-down-hosts
'''
def leader_detect(hostports):
    sk = None
    leader = None
    followers = []
    down = []
    for h, p, a in collect_hosts(hostports):
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if len(argv) > 1:
            sk.settimeout(int(argv[1]))
        try:
            sk.connect((h,p))
            sk.send(b'isro')
            resp = sk.recv(1024)
            if resp == r'rw':
                leader = str(h)+':'+str(p)
            else:
                followers.append(str(h)+':'+str(p))

        except Exception as e:
            down.append(str(h)+':'+str(p))
        if sk:
            sk.close()
    return leader, followers, down

if __name__=='__main__':
  from sys import argv, exit
  from os import environ

  ## Run....
  leader, followers, downs = leader_detect(environ['ZK_LIST'])
  print 'leader: {0}, followers: {1}, downs: {2}'.format(leader, followers, downs)
  exit(0)

