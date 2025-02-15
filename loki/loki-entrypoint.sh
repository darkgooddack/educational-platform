#!/bin/sh
mkdir -p /tmp/loki/chunks /tmp/loki/index /tmp/loki/cache
chown -R loki:loki /tmp/loki
exec /usr/bin/loki -config.file=/etc/loki/local-config.yaml