FROM grafana/grafana:10.2.0

USER root

# Копируем конфиги для провижининга
COPY configs/datasources /etc/grafana/provisioning/datasources
COPY configs/dashboards /etc/grafana/provisioning/dashboards

# Копируем дашборды
COPY configs/dashboards/*.json /var/lib/grafana/dashboards/

# Скрипт инициализации
COPY scripts/init.sh /init.sh

RUN chmod +x /init.sh

USER grafana

ENTRYPOINT ["/init.sh"]