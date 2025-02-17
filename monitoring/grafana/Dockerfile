FROM grafana/grafana:11.3.0

USER root

# Копируем конфиги для провижининга
COPY datasources /etc/grafana/provisioning/datasources
COPY dashboards /etc/grafana/provisioning/dashboards

# Копируем дашборды
COPY dashboards/*.json /var/lib/grafana/dashboards/

# Скрипт инициализации
COPY grafana-entrypoint.sh /grafana-entrypoint.sh

RUN chmod +x /grafana-entrypoint.sh

USER grafana

ENTRYPOINT ["/grafana-entrypoint.sh"]