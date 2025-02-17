#!/bin/bash

# Устанавливаем плагины
grafana-cli plugins install grafana-piechart-panel
grafana-cli plugins install grafana-clock-panel

# Создаем директории
mkdir -p /etc/grafana/provisioning/datasources
mkdir -p /etc/grafana/provisioning/dashboards
mkdir -p /var/lib/grafana/dashboards

# Копируем конфиги
cp /etc/grafana/provisioning/datasources/loki.yml /etc/grafana/provisioning/datasources/
cp /etc/grafana/provisioning/dashboards/dashboard.yml /etc/grafana/provisioning/dashboards/
cp /etc/grafana/provisioning/dashboards/*.json /var/lib/grafana/dashboards/

# Запускаем Grafana
exec /run.sh