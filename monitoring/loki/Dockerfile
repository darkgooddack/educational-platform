FROM grafana/loki:2.9.0

COPY configs/config.yaml /etc/loki/local-config.yaml

CMD ["-config.file=/etc/loki/local-config.yaml"]