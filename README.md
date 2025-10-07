# Edge Gateway para IA Pessoal baseada em Blockchain

Este repositório organiza os artefatos iniciais do projeto descrito no paper
**EdgeGateway_Paper.pdf**, que detalha a construção de um Edge Gateway capaz de conectar
sensores locais, pipelines de IA embarcada e um Digital Twin protegido por blockchain.
Aqui você encontra a estrutura recomendada de diretórios, documentação base, scripts de
ambiente e apontadores para o desenvolvimento com Yocto Project.

## Estrutura do repositório
```text
├── .vscode/                     # Configurações compartilhadas do Visual Studio Code
│   ├── extensions.json          # Extensões para Yocto, Docker, YAML e Markdown
│   ├── settings.json            # Preferências de formatação, lint e telemetria
│   └── tasks.json               # Tarefas para preparar ambiente e compilar imagens Yocto
├── docs/
│   ├── architecture/            # Modelos de arquitetura e fluxos descritos no paper
│   │   ├── system-architecture.md
│   │   └── communication-and-dataflow.md
│   ├── paper/                   # Anotações e síntese do EdgeGateway_Paper.pdf
│   │   └── edgegateway-paper-summary.md
│   └── roadmaps/                # Backlog inicial e marcos do desenvolvimento
│       └── milestone-plan.md
├── scripts/                     # Scripts utilitários
│   └── setup-env.sh             # Inicialização do ambiente Yocto/BitBake
├── yocto/
│   ├── README.md                # Guia de camadas, imagens e customizações
│   └── layers/
│       └── meta-edgegateway/    # Camada personalizada descrita no paper
│           ├── conf/layer.conf
│           └── recipes-core/images/edgegateway-image.bb
├── .gitignore
├── LICENSE
└── README.md
```

## Referencial técnico do EdgeGateway_Paper.pdf
O paper descreve um gateway que integra dispositivos IoT, microsserviços containerizados e
sincronização com um Digital Twin em blockchain. A principal missão é garantir a soberania
do usuário, oferecendo inferência local de IA, políticas de governança auditáveis e canais
seguros de compartilhamento de dados. Consulte o resumo em `docs/paper/edgegateway-paper-summary.md`
para navegar pelos requisitos funcionais, componentes e implicações para o desenvolvimento.

### Domínios abordados
- **Hardware e conectividade**: suporte a protocolos industriais e residenciais, módulos TPM,
  5G/LTE e redes mesh locais.
- **Pipeline de IA**: modelos embarcados para inferência em tempo real e comunicação com
  pipelines de treinamento em nuvem.
- **Blockchain e Digital Twin**: contratos inteligentes para registrar identidade, políticas de
  acesso e auditoria de eventos.
- **Observabilidade e DevSecOps**: telemetria, gestão de logs, atualizações OTA e integração
  contínua para receitas Yocto e imagens container.

## Como utilizar esta base
1. **Clonar o repositório** e abrir no VSCode. As extensões sugeridas serão oferecidas
   automaticamente. Revise `.vscode/settings.json` para personalizar linting e formatação.
2. **Adicionar o Poky** (e eventualmente BSPs) como submódulos:
   ```bash
   git submodule add git://git.yoctoproject.org/poky yocto/poky
   git submodule update --init --recursive
   ```
3. **Inicializar o ambiente** executando a tarefa `Yocto: setup environment` ou rodando manualmente:
   ```bash
   source scripts/setup-env.sh
   ```
4. **Construir a imagem de referência**:
   ```bash
   bitbake edgegateway-image
   ```
   A receita em `meta-edgegateway` inclui pacotes para containers, broker MQTT, agentes de
   sincronização blockchain e ferramentas de observabilidade conforme descrito no paper.
5. **Documentar decisões** no diretório `docs/`, expandindo os modelos de arquitetura e o plano
de marcos.
6. **Planejar integrações** com pipelines de IA, dashboards e contratos inteligentes seguindo as
   diretrizes capturadas no resumo do paper.

## Próximos passos sugeridos
- Definir o hardware-alvo (SoC, conectividade, memória) e adicionar camadas BSP correspondentes.
- Especificar a pilha de containers (orquestrador, broker MQTT, agentes blockchain, módulos de IA)
  utilizando recipientes em `recipes-containers/` (a serem adicionados).
- Configurar pipelines CI/CD que executem builds Yocto, testes de conformidade e verificação de
  políticas de segurança derivadas do ledger.
- Implementar estratégias de observabilidade e automação OTA alinhadas aos requisitos do paper.
- Elaborar casos de uso detalhados e fluxos de dados na pasta `docs/architecture/`.

## Licença
Este projeto é distribuído sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.
