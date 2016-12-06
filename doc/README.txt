INITIAL REQUIREMENTS

First read assumptions.txt to make sure at least the minimum requrements are met.

Provided the environment is set up, edit defaults.cfg accordingly.

DEFINITIONS

One broker per container is assumed.
However, multiple containers can be hosted on a virtual host, which among others, allows to exploit cpu parallelism.
The virtual host setup is similar to the reference setup described below (refer to assumptions.txt for further detail), but is beyound the scope of this document, as it is highly dependent on the target hypervisor and its infrastructure, which is even more beyound its scope.

ENABLE MONITORING

On the techost, do:
sudo lib/docmon.py start -v 
sudo tail -f /tmp/dockmon.log

BOOTSTRAP CLUSTER

0. Make sure the new virtual hosts adhere to the conditions set forth in the assumptions.txt file.

1. Edit the defaults.config file. Make sure all the new virtual host have been properly listed.

2. Insert proper values in k/Dockerfile and k/Dockercompose.yml.
edit k/docker-compose.yml to meet your specific needs, in particular the zookeper host addresses
 
3. sudo bootstrap_cluster.sh

Provided the virtual hosts and the techhost have been setup correctly, the script should generate proper config files and place them on target virtual hosts.

BOOTSTRAP A NEW VIRTUAL HOST

NB: VIRTUAL HOST BOOTSTRAP CAN BE FULLY AUTOMATED, PROVIDED SPECIFIC DETAILS ARE GIVEN AS TO THE SITE INFRASTRUCTURE.

0. Add the host's configuration parameter to defaults.cfg

1. sudo ./addhost.sh IP
2. Make sure it runs OK. If not, re-read the assumptions.txt to make sure you understand the minimal infrastructure requrements and meet them
do a docker ps to see that the process is indeed there

ADD BROKERS

1. sudo ./addbroker.sh IP COUNT

REMOVE BROKER

1. sudo ./removebroker.sh BROKERID 

REMOVE HOST

1. sudo ./removehost.sh IP

Make sure to delete the target virthost ip from the VIRTHOSTS list in defaults.cfg. You may keep other settings of the virthost in question.

THE TOOLS REFERENCE 

The tools directory contains a set of cluster management scripts to be used on a techhost.

* clusterstatus.sh Requires no arguments.

Does functional checks for the whole cluster, as well as individual brokers.
Currently outputs the results to terminal, but could easily be customized to fit
into a monitoring system of choice.

* addbroker.sh IP COUNT 

Adds COUNT brokers to the specified virtual host.

* removebroker.sh killedBrokerID firstBrokerID lastBrokerID

Removes the broker with specified ID from the cluster. Moves its partitions to specified broker range.

* removehost.sh host firstBrokerID lastBrokerID

Removes the host from the cluster. Supports multi-broker single-host configurations. Partitions of all the brokers on the host are moved to the specified broker range. While it is possible to proceed with host removal in a single batch, I preferred to have the multi-stage broker removal, making sure to check the cluster is sane to stop immediately, should an error occur. However, an option could be provided to do the move in a single batch, if required.

* lib/dockmon.py

Asynchronous docker monitoring daemon. Could be easily extended to plug in various monitoring or incorporated in many monitoring agents.

AUTOMATIC STARTUP/SHUTDOWN

The containers ensamble could be started at boot time. Use the ./install-service.sh to install appropriate service.

Then the usual:
  sudo systemctl service start kafka-docker.service
  sudo systemctl service stop kafka-docker.service
  sudo systemctl service status kafka-docker.service
can be used.

NOTES:

Long time operations (e.g. cluster re-partitioning, re-balancing) are performed
in an automated manner. The scripts make sure the success/failure status and logs
are delivered to the specified mail distribution list.

The scripts do functional checking after each stage of repartitioning.

FINAL REMARK:

The toolkit is crude, but is a good starting point. The required functionality can be added on promptly, as the criteria are adjusted or re-stated. For example, additional steps could be taken after adding a broker or decomissioning a host.

I assume its value to be in customizing these tools to fit together for a particular business purpose.

Some portions of the toolkit are based on open source code from various sources,
some are public domain tools. While I could write all of the code from scratch,
it is the debugging effort and time of the others that I put forward to deliver
a stable solution in a reasonable time. This, however, could be turned into genuine from scratch own product, if required.

