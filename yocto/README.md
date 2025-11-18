# Guia Yocto para o Edge Gateway

Traduz requisitos do `EdgeGateway_Paper.pdf` em ações concretas para customização da imagem Yocto.

## Estrutura
```text
yocto/
  README.md
  layers/
    meta-edgegateway/
      conf/layer.conf
      recipes-core/images/edgegateway-image.bb
      recipes-containers/ (placeholders)
  poky/  # adicionar como submódulo
```

## Pré-requisitos
- Host Linux (ou WSL2) com: git, python3, tar, gcc, chrpath, cpio, gawk, make, xz, unzip, Locale en_US.UTF-8.
- Espaço em disco: ≥ 50 GB; RAM: ≥ 16 GB (recomendado).
- Variável `TEMPLATECONF` apontando para `meta-edgegateway/conf` ao inicializar o ambiente.

## Passos iniciais
1. Adicionar Poky e camadas BSP do hardware-alvo.
2. `source ../scripts/setup-env.sh` (exporta `TEMPLATECONF`, `BBPATH`, etc.).
3. Atualizar `bblayers.conf` para incluir `meta-edgegateway` e BSPs.
4. Executar `bitbake edgegateway-image`.

## Conteúdo recomendado para `edgegateway-image`
- Suporte a containers (Docker/Podman) e runtime OCI (crun/runc).
- Broker MQTT (Eclipse Mosquitto) + fila persistente (RabbitMQ/NATS JetStream).
- Ferramentas de IA (TensorFlow Lite, ONNX Runtime) e drivers de aceleradores.
- Agentes blockchain, DIDComm e bibliotecas criptográficas (libsodium, openssl).
- Stack de observabilidade (Prometheus Node Exporter, Fluent Bit, Grafana Agent).
- Ferramentas OTA (swupdate ou Mender) e scripts de rollback.

## Variáveis úteis
| Variável | Função |
| --- | --- |
| `MACHINE` | Define o hardware-alvo/BSP. |
| `DISTRO` | Base da distribuição (ex.: `poky`, `edgegateway`). |
| `BB_ENV_EXTRAWHITE` | Permite passar variáveis customizadas para o BitBake. |
| `SSTATE_DIR` e `DL_DIR` | Diretórios compartilhados para acelerar builds. |

## Práticas recomendadas
- Versionar `conf/notebook/*.conf` (TEMPLATECONF) para garantir builds reproduzíveis.
- Usar `devtool` para iterar em receitas locais antes de promover para `meta-edgegateway`.
- Documentar novas receitas/overlays em `docs/architecture/` e criar testes pTest quando aplicável.

## Próximas evoluções
- Adicionar receitas para contratos inteligentes/CLIs.
- Integrar testes automatizados (pTest) cobrindo drivers, inferência e sincronização blockchain.
- Criar camadas auxiliares (`meta-edgegateway-security`, `meta-edgegateway-observability`) conforme a base crescer.

> Última revisão: 2025-11-18

