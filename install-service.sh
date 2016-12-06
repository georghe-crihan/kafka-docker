#!/bin/bash
#sudo /sbin/adduser docker-compose -s /sbin/nologin

sudo cat<<EOS>/lib/systemd/system/kafka-docker.service
[Unit]
Description=Kafka Docker Compose Service
After=docker.service
BindsTo=docker.service
Conflicts=shutdown.target reboot.target halt.target

[Service]
Environment=APP='kafka'
TimeoutStartSec=30
TimeoutStopSec=30
Restart=always
RestartSec=10
WorkingDirectory=/root/k
#User=docker-compose
User=root

#ExecStartPre=-/opt/bin/docker-compose -f /root/k/docker-compose.yml kill \$APP
#ExecStartPre=-/opt/bin/docker-compose -f /root/k/docker-compose.yml rm \$APP
#ExecStartPre=-/opt/bin/docker-compose -f /root/k/docker-compose.yml rm -f \$APP

#ExecStart=/opt/bin/docker-compose -f /root/k/docker-compose.yml up --force-recreate --no-deps

ExecStart=/opt/bin/docker-compose -f /root/k/docker-compose.yml up 

ExecStop=/opt/bin/docker-compose -f /root/k/docker-compose.yml stop \$APP

#ExecStatus=/opt/bin/docker-compose -f /root/k/docker-compose.yml status
NotifyAccess=all

[Install]
WantedBy=multi-user.target
EOS

sudo systemctl enable kafka-docker.service

