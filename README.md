# Edge Gateway para IA Pessoal baseada em Blockchain

Base de conhecimento e código do Edge Gateway descrito no paper `EdgeGateway_Paper.pdf`. O objetivo é conectar sensores locais, pipelines de IA embarcada e um Digital Twin protegido por blockchain, mantendo soberania de dados, inferência de baixa latência e governança auditável.

## Visão geral rápida
- **Stack principal**: Yocto Project + containers OCI, pipelines de IA embarcada e agentes blockchain/DIDComm.
- **Documentação**: modelos arquiteturais em `docs/`, resumo do paper e planos de marcos.
- **Serviços**: protótipo do agente DIDComm em `services/didcomm-agent/`.
- **Infra**: scripts e tarefas de VS Code para preparar o ambiente de build.

## Como começar
1. **Clonar e abrir no VS Code** – as extensões sugeridas estão em `.vscode/extensions.json`.
2. **Adicionar submódulos Yocto/BSP**
   ```bash
   git submodule add git://git.yoctoproject.org/poky yocto/poky
   git submodule update --init --recursive
   ```
3. **Inicializar ambiente** – rode `source scripts/setup-env.sh` (ou a task `setup environment` do VS Code).
4. **Construir imagem de referência** – execute `bitbake edgegateway-image` dentro do ambiente.
5. **Documentar decisões** – atualize os arquivos em `docs/` conforme as escolhas de arquitetura e hardware evoluírem.

## Estrutura do repositório
```text
.vscode/                     Definições de tarefas, lint e extensões recomendadas
docs/                        Bases de arquitetura, pesquisa e roadmap
  architecture/              Arquitetura de sistema, fluxos e DIDComm
  paper/                     Resumo navegável do EdgeGateway_Paper.pdf
  research/                  Estudos complementares sobre IA pessoal e blockchain
  roadmaps/                  Marcos técnicos e backlog inicial
scripts/                     Scripts utilitários (ex.: setup-env.sh)
services/
  didcomm-agent/             Serviço FastAPI + testes para o agente DIDComm
yocto/
  README.md                  Guia rápido de camadas e receitas
  layers/meta-edgegateway/   Receita edgegateway-image e espaço para containers
EdgeGateway_Paper.pdf        Referência completa do projeto
LICENSE                      Licença MIT
```

## Documentação recomendada
| Tema | Onde começar | Por que importa |
| --- | --- | --- |
| Arquitetura de sistema | `docs/architecture/system-architecture.md` | Visão 360° dos módulos do gateway |
| Fluxos de dados e comunicação | `docs/architecture/communication-and-dataflow.md` | Regras de QoS, protocolos e requisitos operacionais |
| Subsistema DIDComm | `docs/architecture/didcomm-architecture.md` + `services/didcomm-agent/README.md` | Guia para o MVP de mensageria segura |
| Resumo do paper | `docs/paper/edgegateway-paper-summary.md` | Índice rápido do PDF original |
| Roadmap | `docs/roadmaps/milestone-plan.md` | Sequenciamento das fases do projeto |

## Guia Yocto em 5 minutos
1. Garanta que `yocto/poky` e camadas BSP estejam presentes.
2. Use o script `scripts/setup-env.sh` para exportar variáveis do BitBake.
3. Certifique-se de que `yocto/layers/meta-edgegateway/conf/layer.conf` esteja habilitado no `bblayers.conf`.
4. Ajuste `yocto/layers/meta-edgegateway/recipes-core/images/edgegateway-image.bb` adicionando pacotes (containers, MQTT, agentes blockchain, ferramentas de IA e observabilidade).
5. Adicione receitas específicas em `recipes-containers/` e `recipes-security/` para refletir os requisitos do paper.

Detalhes extras estão em `yocto/README.md` e devem ser expandidos conforme as customizações aumentarem.

## Serviço DIDComm
- Código e testes em `services/didcomm-agent/`.
- Stack: FastAPI + libsodium (X25519 + ChaCha20-Poly1305), com scripts de exemplo (`examples/demo_exchange.py`).
- Rode `python -m pytest` para testes locais e `docker compose up --build` para a API containerizada.
- A arquitetura conceitual está alinhada a `docs/architecture/didcomm-architecture.md`.

## Roadmap e próximos passos
1. **Fase 0** – definir hardware-alvo, BSPs e requisitos de segurança/compliance.
2. **Fase 1** – estabilizar a camada `meta-edgegateway`, broker MQTT e agentes blockchain.
3. **Fase 2** – observabilidade, governança de dados e automação OTA.
4. **Fase 3** – pilotos com dispositivos reais e preparação para auditorias.

Atualize `docs/roadmaps/milestone-plan.md` e os diagramas em `docs/architecture/` à medida que novas decisões forem tomadas (hardware, modelos de IA, contratos inteligentes etc.).

## Licença
Distribuído sob a licença MIT – consulte `LICENSE` para detalhes.
