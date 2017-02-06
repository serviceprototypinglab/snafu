#!/bin/bash

if [ ! -d rabbitmq_server-3.6.6 ]
then
	if [ ! -f rabbitmq-server-generic-unix-3.6.6.tar.xz ]
	then
		wget -c http://www.rabbitmq.com/releases/rabbitmq-server/v3.6.6/rabbitmq-server-generic-unix-3.6.6.tar.xz
	fi
	tar xf rabbitmq-server-generic-unix-3.6.6.tar.xz
fi

cd rabbitmq_server-3.6.6
echo "** runing RabbitMQ **"
./sbin/rabbitmq-server
