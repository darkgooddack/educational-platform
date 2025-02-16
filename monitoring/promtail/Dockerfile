FROM grafana/promtail:2.9.0

COPY configs/config.yml /etc/promtail/config.yml

CMD ["-config.file=/etc/promtail/config.yml"]