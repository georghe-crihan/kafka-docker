# Assume we have an internal image repository, for this particular instance, let it be CentOS 7.0, blame myself for all the consequences 
FROM		centos:7
MAINTAINER	myself@example.com

ENV		KAFKA_VERSION="0.9.0.1" SCALA_VERSION="2.11"

#RUN		curl -L http://www-us.apache.org/dist/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz -o /root/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz

ADD		kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz /root/
RUN		mkdir -p /opt/bin
ADD		gosu /opt/bin/gosu
RUN		chmod +x /opt/bin/gosu
ENV		JAVA_HOME="/usr/lib/jvm/jre-1.8.0-openjdk" JRE_HOME="/usr/lib/jvm/jre"
# install Java first
RUN		/opt/bin/gosu root yum -y install java-1.8.0-openjdk.x86_64
RUN		/opt/bin/gosu root yum -y install net-tools.x86_64
#RUN		/opt/bin/gosu root tar -xvf /root/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz -C /opt
RUN		/opt/bin/gosu root mv /root/kafka_${SCALA_VERSION}-${KAFKA_VERSION} /opt/
VOLUME		["/kafka"]

ENV		KAFKA_HOME /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION}
ADD		start-kafka.sh /opt/bin/start-kafka.sh
ADD		create-topics.sh /opt/bin/create-topics.sh
ADD             kafka-watchdog.sh /opt/bin/kafka-watchdog.sh

# The scripts need to have executable permission
RUN		chmod a+x /opt/bin/start-kafka.sh && \
                chmod a+x /opt/bin/kafka-watchdog.sh && \
		chmod a+x /opt/bin/create-topics.sh

# Use "exec" form so that it runs as PID 1 (useful for graceful shutdown)
CMD		["/opt/bin/start-kafka.sh"]
