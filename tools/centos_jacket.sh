#!/bin/bash

mysqldbadm="root"
mysqldbpassword="P@ssw0rd"
mysqldbport="3306"


jacketdbname="jacketdb"
jacketdbuser="jacketdbuser"
jacketdbpass="P@ssw0rd"

HOST_IP=`ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"`
jacket_host="$HOST_IP"
dbbackendhost="$HOST_IP"
keystonehost="$HOST_IP"
keystonedomain="default"
keystoneservicestenant="services"

jacketuser="jacket"
jacketpass="P@ssw0rd"

mysqlcommand="mysql"

echo "CREATE DATABASE IF NOT EXISTS $jacketdbname default character set utf8;"|$mysqlcommand
echo "GRANT ALL ON $jacketdbname.* TO '$jacketdbuser'@'%' IDENTIFIED BY '$jacketdbpass';"|$mysqlcommand
echo "GRANT ALL ON $jacketdbname.* TO '$jacketdbuser'@'localhost' IDENTIFIED BY '$jacketdbpass';"|$mysqlcommand
echo "GRANT ALL ON $jacketdbname.* TO '$jacketdbuser'@'$jackethost' IDENTIFIED BY '$jacketdbpass';"|$mysqlcommand

mkdir -p /var/log/jacket


crudini --set /etc/jacket/jacket.conf database connection "mysql+pymysql://${jacketdbuser}:${jacketdbpass}@${dbbackendhost}:${mysqldbport}/${jacketdbname}"
crudini --set /etc/jacket/jacket.conf database retry_interval 10
crudini --set /etc/jacket/jacket.conf database idle_timeout 3600
crudini --set /etc/jacket/jacket.conf database min_pool_size 1
crudini --set /etc/jacket/jacket.conf database max_pool_size 10
crudini --set /etc/jacket/jacket.conf database max_retries 100
crudini --set /etc/jacket/jacket.conf database pool_timeout 10


crudini --set /etc/jacket/jacket.conf keystone_authtoken auth_uri http://$keystonehost:5000
crudini --set /etc/jacket/jacket.conf keystone_authtoken auth_url http://$keystonehost:35357
crudini --set /etc/jacket/jacket.conf keystone_authtoken auth_type password
crudini --set /etc/jacket/jacket.conf keystone_authtoken project_domain_name $keystonedomain
crudini --set /etc/jacket/jacket.conf keystone_authtoken user_domain_name $keystonedomain
crudini --set /etc/jacket/jacket.conf keystone_authtoken project_name $keystoneservicestenant
crudini --set /etc/jacket/jacket.conf keystone_authtoken username $jacketuser
crudini --set /etc/jacket/jacket.conf keystone_authtoken password $jacketpass
crudini --set /etc/jacket/jacket.conf keystone_authtoken memcached_servers $keystonehost:11211

crudini --set /etc/jacket/jacket.conf DEFAULT osapi_jacket_listen "${jacket_host}"
crudini --set /etc/jacket/jacket.conf DEFAULT debug "true"
crudini --set /etc/jacket/jacket.conf DEFAULT log_dir "/var/log/jacket"
crudini --set /etc/jacket/jacket.conf wsgi api_paste_config "/etc/jacket/jacket-api-paste.ini"
