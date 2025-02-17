FROM grafana/promtail:3.2.0

COPY configs/config.yaml /etc/promtail/config.yaml

CMD ["-config.file=/etc/promtail/config.yaml"]