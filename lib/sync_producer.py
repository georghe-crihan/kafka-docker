#!/usr/bin/env python

# Patched version of kafka.client
from devopsclient import DevopsSimpleClient
from kafka.errors import ReplicaNotAvailableError
from kafka import SimpleProducer
from zk_tools import get_broker
from sys import exit

# To send messages synchronously

class Producer:

  def __init__(self, t, broker):
    if t == "container":
      self._broker = broker
    else:
      self._broker = get_broker(None, broker)
    if not self._broker:
      exit(1)
    if (t == "broker") or (t == "container"):
      self._client = DevopsSimpleClient(self._broker, self._broker)
    else:
      self._client = DevopsSimpleClient(self._broker)

  def close(self):
    self._client.close()

  def produce(self, message, ack):
    if ack != "ack":
      producer = SimpleProducer(self._client, async=False)

      # Note that the application is responsible for encoding messages to type bytes
      response = producer.send_messages('devopstest1', b'' + message)
      self._client.close()
      return (0, response)
    else:
      # To wait for acknowledgements
      # ACK_AFTER_LOCAL_WRITE : server will wait till the data is written to
      #                         a local log before sending response
      # ACK_AFTER_CLUSTER_COMMIT : server will block until the message is committed
      #                            by all in sync replicas before sending a response
      producer = SimpleProducer(self._client,
                                async=False,
                                req_acks=SimpleProducer.ACK_AFTER_LOCAL_WRITE,
                                ack_timeout=2000,
                                sync_fail_on_error=False)

      responses = producer.send_messages('devopstest1', b'' + message)
      self._client.close()
      return (0, responses)

if __name__ == '__main__':
  from sys import argv

  if len(argv) < 5: 
    print "lib/sync_producer.py broker brokerid message ack"
    print "lib/sync_producer.py container host:port message ack"
    print "lib/sync_producer.py cluster brokerid message ack"
    exit(1)

  try:
    p = Producer(argv[1], argv[2])

    rc, resp = p.produce(argv[3], argv[4])

  # Specific broker not available
  except ReplicaNotAvailableError:
    p.close()
    exit(3)

  # Something different happened
  except:
    p.close()
    exit(4)

  exit(rc)
