#!/bin/bash

cd `dirname $0`/..
if [ -z "$APPSCALE_HOME_RUNTIME" ]; then
    export APPSCALE_HOME_RUNTIME=`pwd`
fi

. debian/appscale_install_functions.sh

DESTDIR=$2
APPSCALE_HOME=${DESTDIR}${APPSCALE_HOME_RUNTIME}
DIST=`lsb_release -c -s`

echo "Install AppScale into ${APPSCALE_HOME}"
echo "APPSCALE_HOME in runtime=${APPSCALE_HOME_RUNTIME}"

case "$1" in
    core)
	installappscaleprofile
	installgems
	installhaproxy
	installnginx
	installappserverjava
	installmonitoring
	installthrift_fromsource
        installtornado
	installhadoop
#	if [ "$DIST" = "jaunty" -o "$DIST" = "karmic" ]; then
	installzookeeper
#	fi
	installneptune
	installservice
	;;
    cassandra)
	installcassandra
	;;
    voldemort)
	installprotobuf
	installvoldemort
	;;
    hbase)
	installhbase
	;;
    hypertable)
	installhypertable
	installhypertablemonitoring
	;;
    mysql)
	installmysql
	;;
    mongodb)
	installmongodb
	;;
    memcachedb)
	installmemcachedb
	;;
    timesten)
	installtimesten
	;;
    scalaris)
	installscalaris
	;;
    simpledb)
	;;
    # for test only. this should be included in core and all.
    zookeeper)
	installzookeeper
	postinstallzookeeper
	;;
    hadoop)
	installhadoop
	postinstallhadoop
	;;
    neptune)
	installneptune
	postinstallneptune
	;;
    protobuf-src)
	installprotobuf_fromsource
	postinstallprotobuf
	;;
    all)
	# scratch install of appscale including post script.
	installappscaleprofile
	. /etc/profile.d/appscale.sh
	installgems
	postinstallgems
	installhaproxy
	postinstallhaproxy
	installnginx
	postinstallnginx
	installappserverjava
	postinstallappserverjava
	installmonitoring
	postinstallmonitoring
	installthrift_fromsource
	postinstallthrift_fromsource
        installtornado
        postinstalltornado
	installprotobuf
	postinstallprotobuf
	installhadoop
	postinstallhadoop
#	if [ "$DIST" = "jaunty" -o "$DIST" = "karmic" ]; then
	    installzookeeper
#	fi
	postinstallzookeeper
	installcassandra
	postinstallcassandra
	installvoldemort
	postinstallvoldemort
	installhbase
	postinstallhbase
	installhypertable
	postinstallhypertable
	installhypertablemonitoring
	postinstallhypertablemonitoring
	installmysql
	postinstallmysql
	installmongodb
	postinstallmongodb
	installmemcachedb
	postinstallmemcachedb
	installtimesten
	postinstalltimesten
	installscalaris
	postinstallscalaris
	installneptune
	postinstallneptune
	installservice
	postinstallservice
	updatealternatives
	sethosts
	keygen
	;;
esac
