FROM grafana/loki:latest

COPY configs/config.yaml /etc/loki/local-config.yaml

CMD ["-config.file=/etc/loki/local-config.yaml"]