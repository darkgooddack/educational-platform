#!/bin/sh

mkdir -p /var/log
touch /var/log/app.log
chmod 644 /var/log/app.log

/usr/bin/promtail -config.file=/etc/promtail/config.yml