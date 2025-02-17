FROM grafana/loki:3.4.1

COPY configs/config.yaml /etc/loki/local-config.yaml

CMD ["-config.file=/etc/loki/local-config.yaml"]