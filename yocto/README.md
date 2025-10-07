# Guia Yocto para o Edge Gateway

Este guia traduz requisitos do *EdgeGateway_Paper.pdf* em ações concretas para customização da
imagem Yocto.

## Estrutura
```text
yocto/
├── README.md
├── layers/
│   └── meta-edgegateway/
│       ├── conf/layer.conf
│       └── recipes-core/images/edgegateway-image.bb
└── poky/                # (adicionar como submódulo)
```

## Passos iniciais
1. **Adicionar o Poky** e camadas BSP do hardware-alvo.
2. **Configurar ambiente**:
   ```bash
   source ../scripts/setup-env.sh
   ```
3. **Construir imagem**:
   ```bash
   bitbake edgegateway-image
   ```

## Conteúdo recomendado para `edgegateway-image`
- Suporte a containers (Docker ou Podman) e runtime OCI.
- Broker MQTT (Eclipse Mosquitto) e fila persistente (RabbitMQ ou NATS JetStream).
- Ferramentas de IA (TensorFlow Lite, ONNX Runtime) e aceleradores específicos.
- Agentes blockchain e bibliotecas criptográficas.
- Stack de observabilidade (Prometheus Node Exporter, Fluent Bit, Grafana Agent).

## Próximas evoluções
- Adicionar receitas para contratos inteligentes e CLI de gestão.
- Integrar atualizações OTA utilizando swupdate ou Mender.
- Criar testes automatizados (pTest) que cubram drivers, inferência e sincronização blockchain.
ME
