# Dossier Completo do Projeto EdgeGateway

Guia de leitura integral do repositorio `EdgeGateway`, escrito para uma pessoa que parte do zero e precisa de perceber o que existe, onde esta cada coisa e qual e o estado real da implementacao.

Data da leitura tecnica: 2026-04-09

## 1. Objetivo deste documento

Este dossier tem quatro objetivos muito concretos:

1. Explicar, em linguagem simples, o que o projeto tenta construir.
2. Dizer o que ja existe de facto no codigo.
3. Explicar pasta a pasta e ficheiro a ficheiro o papel de cada artefacto relevante.
4. Explicar todas as classes proprias do repositorio e como elas encaixam na arquitetura.

O foco aqui nao e propor melhorias nem alterar implementacoes. O foco e fotografar o repositorio tal como ele esta hoje.

## 2. Ambito e exclusoes explicitas

### 2.1 Ambito coberto

Este guia cobre:

- raiz do repositorio
- `.github/`
- `docs/`
- `services/`
- `yocto/`
- `scripts/`
- `uni/paper/`
- `uni/study_material/`
- `uni/tese/`

### 2.2 O que fica de fora

Ficam fora do inventario funcional porque sao artefactos gerados, caches, outputs temporarios ou metadata automatica:

- `.git/`
- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- `.codex-temp/`
- `*.pyc` e `*.pyo`
- `services/didcomm-agent/src/didcomm_agent.egg-info/`
- `services/didcomm-agent/data/didcomm.sqlite`
- `uni/tese/main.aux`
- `uni/tese/main.bbl`
- `uni/tese/main.bcf`
- `uni/tese/main.blg`
- `uni/tese/main.fdb_latexmk`
- `uni/tese/main.fls`
- `uni/tese/main.lof`
- `uni/tese/main.log`
- `uni/tese/main.lot`
- `uni/tese/main.pdf`
- `uni/tese/main.run.xml`
- `uni/tese/main.synctex.gz`
- `uni/tese/main.toc`

Tambem nao descrevo classes de dependencias externas como FastAPI, Pydantic, httpx, paho-mqtt, cryptography ou ACA-Py. So entram classes escritas dentro deste repositorio.

O proprio ficheiro deste dossier nao entra no inventario funcional, para evitar auto-referencia infinita.

## 3. Explicacao para iniciantes

### 3.1 O que e este projeto

Este repositorio implementa uma prova de conceito da arquitetura C2DTA, sigla de `Consumer-Controlled Digital Twin Architecture`.

A ideia base e esta:

- um dispositivo inteligente gera dados
- esses dados passam por uma Edge Gateway
- a gateway ajuda a criar e gerir um Digital Twin
- a identidade e a propriedade do dispositivo sao tratadas com SSI e credenciais verificaveis
- alguns factos importantes ficam registados em blockchain
- snapshots dos dados podem ser guardados no IPFS

Em termos simples: o projeto tenta criar uma arquitetura em que o consumidor nao perde completamente o controlo do dispositivo, da identidade e dos dados do seu gemeo digital.

### 3.2 O que e cada bloco principal

| Conceito | Explicacao simples |
| --- | --- |
| Edge Gateway | O computador de fronteira que fica perto dos dispositivos. Recebe dados, faz integracao local e fala com os restantes servicos. |
| Smart Device | O dispositivo fisico. Aqui existe um simulador de smartwatch para gerar telemetria. |
| Digital Twin | A copia digital do dispositivo. No projeto e gerida pelo Eclipse Ditto. |
| SSI | `Self-Sovereign Identity`. Identidade descentralizada onde cada ator controla as suas credenciais. |
| VC | `Verifiable Credential`. Credencial digital verificavel, como se fosse um certificado assinado. |
| DIDComm | Protocolo de comunicacao segura entre agentes de identidade. |
| Fabric | Blockchain usada como ledger do ecossistema, sobretudo para ciclo de vida do dispositivo e datasets. |
| Indy | Ledger de identidade usado para schemas, DIDs e ecossistema SSI. |
| IPFS | Armazenamento descentralizado para snapshots dos dados do twin. |
| MQTT | Protocolo leve de mensagens para transportar telemetria do dispositivo para a gateway/twin. |
| Yocto | Framework para construir uma distribuicao Linux embebida, pensada para a gateway final. |

### 3.3 Glossario minimo

| Termo | Significado pratico neste repositorio |
| --- | --- |
| UC1-UC8 | Os oito use cases descritos no paper. Cada um corresponde a uma fase do ciclo de vida. |
| OOB invitation | Convite `Out-of-Band` para iniciar uma ligacao DIDComm/ACA-Py. |
| Thing | Objeto no Eclipse Ditto que representa o Digital Twin. |
| CID | Identificador de conteudo do IPFS. |
| Chaincode | Nome que o Fabric da aos smart contracts. |
| WoT TD | `Web of Things Thing Description`, ficheiro que descreve as propriedades e capacidades do dispositivo. |
| QoS 1 | Garantia MQTT do tipo "at least once". |
| Askar | Tipo de wallet usado pelos agentes ACA-Py neste ambiente de desenvolvimento. |

## 4. Mapa geral do repositorio

### 4.1 Como o repositorio esta organizado

| Pasta | Papel no projeto |
| --- | --- |
| raiz | Entrada principal: README, compose raiz, regras de git e automacao. |
| `.github/` | Pipelines CI para testes, lint e build Yocto. |
| `docs/` | Documentacao tecnica: arquitetura, fluxos, resumos, reviews e roadmap. |
| `services/` | Implementacao e configuracao dos servicos que compoem a arquitetura. |
| `yocto/` | Layer e receitas para uma imagem Linux da Edge Gateway. |
| `scripts/` | Scripts auxiliares, neste caso para preparar ambiente Yocto. |
| `uni/` | Materiais academicos: paper base, materiais da cadeira e manuscrito da dissertacao. |

### 4.2 Relacao entre as partes

1. `README.md` e `docs/architecture/*.md` explicam a intencao arquitetural.
2. `services/` contem o que realmente corre em containers, testes e codigo Python/Go.
3. `yocto/` tenta traduzir essa stack para um deployment futuro numa gateway real.
4. `uni/paper/EdgeGateway_Paper.pdf` e a origem conceptual do sistema.
5. `uni/tese/` e o manuscrito academico que enquadra e documenta o trabalho.

### 4.3 Ordem de leitura recomendada

Se estivesses a aprender o projeto do zero, a ordem mais eficaz seria:

1. `uni/paper/EdgeGateway_Paper.pdf`
2. `README.md`
3. `docs/architecture/system-architecture.md`
4. `docs/architecture/use-case-flows.md`
5. `services/egw-controller/README.md`
6. `services/egw-controller/src/egw_controller/api.py`
7. `services/egw-controller/src/egw_controller/use_cases/`
8. `services/mosquitto/`, `services/ditto/`, `services/fabric/`, `services/indy/`, `services/ipfs/`
9. `services/didcomm-agent/`
10. `yocto/`
11. `uni/tese/`

## 5. Funcionalidades ja presentes no codigo

### 5.1 Vista rapida por subsistema

| Subsistema | O que ja existe | O que ainda esta parcial, simulado ou placeholder |
| --- | --- | --- |
| EGW Controller | API FastAPI com endpoints para UC1-UC8, modelos, transaction manager e adaptadores para Fabric, Ditto, ACA-Py e IPFS. | O adapter Fabric do controller simula invocacoes; validacoes SSI em alguns UCs ainda sao simplificadas. |
| DIDComm Agent | MVP funcional com chaves X25519, derivacao HKDF, ChaCha20-Poly1305, handshake, envio/rececao e persistencia SQLite opcional. | Nao tem autenticacao HTTP, filas robustas, anexos DIDComm nem hardening de producao. |
| Smart Device Simulator | Gera telemetria a 1 Hz e publica por MQTT/TLS. | E um simulador, nao um driver de hardware real. |
| Mosquitto | Broker MQTT com TLS, ACLs e testes de conectividade. | Configuracao e certificados sao de laboratorio, nao de producao. |
| Ditto | Stack completa de Digital Twin com conectividade MQTT, proxy nginx e WoT TD. | O projeto demonstra o CRUD do twin, mas nao fecha sozinho todo o pipeline de snapshots com politica de retention. |
| Fabric | Rede dev, chaincodes em Go e scripts de arranque/deploy. | O EGW Controller ainda nao invoca esta rede de forma real via SDK/CLI; o adapter local devolve sucesso simulado. |
| Indy + ACA-Py | Pool Indy, schemas de VC, cinco agentes ACA-Py e modulos helper para goal codes/protocolos. | O fluxo end-to-end de emissao/prova nao esta completo no controller para todos os casos. |
| IPFS | No Kubo local e testes de add/cat/pin. | O controller ainda nao executa o pipeline completo de snapshot Ditto -> IPFS -> Fabric dentro dos UCs 6 e 7. |
| Yocto | Layer inicial, imagem base, receitas compose e units systemd. | Ha recipes placeholder e referencias a componentes ainda nao empacotados no layer. |

### 5.2 O que os 8 use cases fazem hoje

| UC | Estado atual no repositorio |
| --- | --- |
| UC1 OEM Enrollment | O controller cria um convite OOB e regista passos transacionais. A emissao de VC esta representada a nivel de chamada/placeholder, nao como fluxo SSI completo ponta a ponta. |
| UC2 Device Model Registration | O controller chama o adapter Fabric para registar o modelo. Conceptualmente esta alinhado, mas o adapter devolve sucesso simulado. |
| UC3 Device Self-Registration | O controller organiza DID/Genesis VC/registo no ledger. A parte de Genesis VC e hash esta simplificada e nao e uma emissao/verificacao real fim a fim. |
| UC4 Consumer Buys Device | A compra/transito e representada no controller e no chaincode de forma coerente. |
| UC5 Device Claiming | O controller trata o claiming, mas a validacao de credenciais esta simplificada; a verificacao de ownership/genesis nao e uma prova SSI completa. |
| UC6 SD Twinning | O controller cria o thing no Ditto e marca twinning no ledger. O pipeline completo de snapshot para IPFS/Fabric ainda nao esta todo materializado no modulo do use case. |
| UC7 SD Untwinning | O controller remove o thing e marca untwinning. O snapshot final/IPFS permanece mais ao nivel da arquitetura/documentacao do que de uma implementacao completa no UC. |
| UC8 SD Selling | O controller trata a transicao de venda, mas a revogacao/reemissao de Ownership VC continua simplificada. |

### 5.3 O que esta mais proximo de "real"

- a stack MQTT
- o simulador do dispositivo
- a stack Ditto
- os chaincodes Fabric em Go
- o no IPFS
- o MVP DIDComm agent
- os testes automatizados de varios modulos

### 5.4 O que esta mais proximo de "laboratorio"

- o adapter Fabric dentro do EGW Controller
- a validacao SSI em UC1, UC3, UC5 e UC8
- a preparacao Yocto, que ainda nao representa uma imagem final pronta para hardware
- o uso de `ACAPY_ADMIN_INSECURE_MODE=true` nas configuracoes de dev

## 6. Inventario pasta a pasta e ficheiro a ficheiro

## 6.1 Raiz do repositorio e CI

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `README.md` | Documento principal do repositorio. Resume a arquitetura C2DTA, os servicos, os use cases, os comandos e a estrutura geral. | Deve ser lido primeiro por qualquer pessoa nova no projeto. | E o mapa de alto nivel mais importante fora do paper. |
| `docker-compose.yml` | Compose raiz que levanta a stack de desenvolvimento completa: Mosquitto, simulator, Ditto, Fabric, Indy, ACA-Py, IPFS, EGW Controller e DIDComm Agent. | Usado em demos locais e integracao manual. | Orquestra cerca de 20 containers e liga tudo pela rede `c2dta-net`. |
| `.gitignore` | Define o que nao deve ser versionado. | Atua sempre que se trabalha com git. | Mostra claramente quais outputs o projeto considera temporarios: Yocto build, caches Python, artefactos Fabric, IPFS, certs, etc. |
| `AGENTS.md` | Instrucoes operacionais do projeto para agentes de desenvolvimento. | Relevante para colaboracao assistida por IA. | Tambem fixa o contexto da dissertacao e a obrigacao de ler o paper. |
| `Claude.md` | Documento paralelo de contexto, semelhante ao `AGENTS.md`. | Mesma situacao do ficheiro anterior. | Nao altera runtime; serve de guia de trabalho. |
| `.github/workflows/ci.yml` | Pipeline CI principal. Corre lint Python, testes Python, `go vet` aos chaincodes e builds Docker. | Usado em push/PR. | E o mecanismo automatico que verifica se o repositorio continua minimamente consistente. |
| `.github/workflows/build-yocto.yml` | Pipeline dedicado ao build Yocto. | Usado quando se pretende validar a imagem `edgegateway-image`. | Depende de runner preparado para Yocto. |

## 6.2 Documentacao tecnica em `docs/`

| Ficheiro | O que faz | Quando ler | Observacoes |
| --- | --- | --- | --- |
| `docs/architecture/system-architecture.md` | Macroarquitetura do sistema: modulos, requisitos transversais, desempenho e roadmap tecnico. | Logo a seguir ao README. | E o melhor documento para perceber a intencao da plataforma completa. |
| `docs/architecture/communication-and-dataflow.md` | Explica como os dados circulam entre dispositivos, edge, twin, IA e cloud. | Quando se quer perceber fluxos de mensagens e resiliencia. | Enfatiza o modelo offline-first e controlos de seguranca. |
| `docs/architecture/didcomm-architecture.md` | Arquitetura conceptual do agente DIDComm. | Ao estudar mensageria segura e SSI. | Vai alem do MVP atual e inclui objetivos de producao como HSM/TPM e policy engine. |
| `docs/architecture/ditto-architecture.md` | Explica o papel do Eclipse Ditto, o modelo do thing, a stack de servicos e a conectividade MQTT. | Ao estudar o Digital Twin. | Traduz Ditto para termos concretos do projeto. |
| `docs/architecture/egw-controller-architecture.md` | Resume o controller, endpoints, transaction manager e dependencias. | Ao entrar no codigo do orquestrador. | E a ponte entre documentacao e implementacao Python do controller. |
| `docs/architecture/fabric-architecture.md` | Descreve a rede Fabric, os estados do dispositivo e os chaincodes. | Antes de ler os chaincodes Go. | Muito util para ligar UC1-UC8 ao ledger do ecossistema. |
| `docs/architecture/indy-architecture.md` | Explica o ledger de identidade, os agentes ACA-Py e os schemas de VCs. | Antes de olhar para SSI/ACA-Py. | E o documento de referencia para Enrollment VC, Genesis VC e Ownership VC. |
| `docs/architecture/ipfs-architecture.md` | Descreve o papel do IPFS nos snapshots do twin e na ancoragem de CIDs ao Fabric. | Ao estudar datasets e historico. | Mostra o pipeline conceptual snapshot -> CID -> ledger. |
| `docs/architecture/mqtt-architecture.md` | Explica topicos, payloads, TLS, ACLs e integracao com Ditto. | Antes de ler Mosquitto e o simulador. | Fundamental para perceber telemetria em tempo real. |
| `docs/architecture/use-case-flows.md` | Lista e descreve em detalhe os oito use cases do paper. | Antes de abrir os modulos `uc1` a `uc8`. | E o documento mais diretamente alinhado com a narrativa funcional do sistema. |
| `docs/paper/edgegateway-paper-summary.md` | Resumo navegavel do paper de referencia. | Quando se quer rever rapidamente o artigo sem abrir o PDF completo. | Serve de ponte entre o paper e o codigo. |
| `docs/research/blockchain-personal-ai-summary.md` | Notas de investigacao sobre blockchain, DIDComm e IA pessoal. | Leitura complementar. | Nao e codigo nem especificacao do sistema; e contexto de investigacao. |
| `docs/reviews/c2dta-paper-conformance-review-2026-04-09.md` | Review tecnica de conformidade entre o repositorio e o paper. | Importante para uma leitura honesta do estado do projeto. | Identifica explicitamente mocks/placeholders e lacunas face ao paper. |
| `docs/roadmaps/milestone-plan.md` | Plano de fases do projeto. | Quando se quer perceber a ordem de implementacao dos blocos. | Mostra que o repositorio cresceu por milestones tematicos. |

## 6.3 `services/aca-py/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `services/aca-py/README.md` | Manual do subsistema SSI com ACA-Py. | Ao estudar identidades, wallets e agentes. | Explica os atores `1@C`, `1@O`, `1@A`, `1@egw` e `1@sd`. |
| `services/aca-py/docker-compose.yml` | Levanta os cinco agentes ACA-Py de desenvolvimento. | Em execucao local da stack SSI. | Configura wallets Askar, endpoints HTTP e portas admin. |
| `services/aca-py/plugins/c2dta_protocols/__init__.py` | Marca o pacote Python dos helpers C2DTA para ACA-Py. | Em importacao dos modulos de protocolo. | Papel estrutural simples. |
| `services/aca-py/plugins/c2dta_protocols/enrollment.py` | Cria o payload da proposta de Enrollment VC para UC1. | Quando o OEM e inscrito no consorcio. | Nao executa o fluxo inteiro; prepara os dados do protocolo. |
| `services/aca-py/plugins/c2dta_protocols/genesis.py` | Cria o payload da proposta de Genesis VC para UC3. | Durante o auto-registo do dispositivo. | E um helper declarativo, nao um agente completo. |
| `services/aca-py/plugins/c2dta_protocols/goal_codes.py` | Define goal codes C2DTA e respetivas descricoes humanas. | Em automacao DIDComm/ACA-Py. | Liga a semantica dos UCs ao protocolo. |
| `services/aca-py/plugins/c2dta_protocols/ownership.py` | Cria payloads para emissao e verificacao de Ownership VC. | Em compra, claiming e venda. | Concentra o lado SSI do ownership. |

## 6.4 `services/didcomm-agent/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `services/didcomm-agent/README.md` | Explica o MVP do agente DIDComm, variaveis de ambiente, API e limites. | Primeiro passo para perceber este microservico. | Assume explicitamente que e um prototipo para POCs. |
| `services/didcomm-agent/docker-compose.yml` | Sobe o container do agente com volume para `/data`. | Em execucao local isolada do agente. | Facilita persistencia SQLite opcional. |
| `services/didcomm-agent/Dockerfile` | Define a imagem Python do agente. | No build container. | Formaliza como a API e empacotada. |
| `services/didcomm-agent/pyproject.toml` | Metadata do pacote Python e tooling. | Em instalacao e packaging. | Importante para `pip install -e` e para o ecossistema Python. |
| `services/didcomm-agent/requirements.txt` | Lista de dependencias do servico. | Em instalacao local/container. | Inclui FastAPI, libs de crypto e testes. |
| `services/didcomm-agent/examples/demo_exchange.py` | Demo sem HTTP de uma troca de mensagens entre Edge e Twin. | Para perceber a logica base antes da API. | E o exemplo mais pequeno e direto do servico. |
| `services/didcomm-agent/examples/smoke_api.py` | Smoke test HTTP contra uma API ja a correr em `localhost:8000`. | Validacao rapida do container/API. | Faz create, accept, complete, send e receive. |
| `services/didcomm-agent/src/didcomm_agent/__init__.py` | Ponto de entrada do pacote; reexporta a API publica. | Em imports do pacote. | Papel estrutural simples. |
| `services/didcomm-agent/src/didcomm_agent/api.py` | Implementa a API FastAPI do agente. | Sempre que o servico corre como HTTP API. | Contem os modelos Pydantic da interface externa. |
| `services/didcomm-agent/src/didcomm_agent/crypto.py` | Biblioteca criptografica local: chaves, derivacao, encrypt/decrypt. | Em todas as operacoes seguras do agente. | E o nucleo tecnico da confidencialidade das mensagens. |
| `services/didcomm-agent/src/didcomm_agent/exceptions.py` | Excecoes de dominio do agente. | Em falhas de peer desconhecido ou adulteracao. | Ajuda a tornar os erros semanticamente claros. |
| `services/didcomm-agent/src/didcomm_agent/message.py` | Modelos de mensagem plaintext e envelope cifrado. | Antes e depois da criptografia. | Traduz objetos Python para JSON DIDComm simplificado. |
| `services/didcomm-agent/src/didcomm_agent/service.py` | Logica principal do agente DIDComm. | Coracao da aplicacao. | Gere convites, peers, envio e rececao cifrada. |
| `services/didcomm-agent/src/didcomm_agent/storage.py` | Persistencia SQLite de agentes e peers. | Quando `DIDCOMM_DB_PATH` esta configurado. | Torna o MVP menos efemero entre reinicios. |
| `services/didcomm-agent/tests/conftest.py` | Ajusta `src/` no path dos testes. | Antes de qualquer teste pytest deste servico. | Ficheiro de suporte, nao logica de negocio. |
| `services/didcomm-agent/tests/test_api.py` | Teste end-to-end da API HTTP do agente. | Na validacao da interface externa. | Prova que o fluxo basico funciona via FastAPI. |
| `services/didcomm-agent/tests/test_didcomm_agent.py` | Testa a logica do agente diretamente, sem HTTP. | Na validacao da camada de dominio. | Cobre fluxo feliz, peer desconhecido e adulteracao. |

Nota importante: `services/didcomm-agent/data/didcomm.sqlite` e `services/didcomm-agent/src/didcomm_agent.egg-info/` existem como artefactos locais, mas nao sao tratados aqui como codigo fonte.

## 6.5 `services/ditto/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `services/ditto/README.md` | Manual da stack Ditto do projeto. | Ao estudar o Digital Twin. | Resume portas, autenticacao e fluxo MQTT -> Ditto. |
| `services/ditto/docker-compose.yml` | Levanta MongoDB, servicos Ditto e nginx. | Em execucao local da plataforma twin. | E a stack runtime do gemeo digital. |
| `services/ditto/connectivity/mqtt-connection.json` | Configuracao de conectividade MQTT do Ditto. | Quando o Ditto deve consumir telemetria do Mosquitto. | Mapeia payload JSON para features do thing. |
| `services/ditto/nginx/nginx.conf` | Reverse proxy do Ditto com auth e encaminhamento de endpoints. | Sempre que se usa `http://localhost:8080`. | Esconde a topologia interna dos servicos Ditto. |
| `services/ditto/nginx/nginx.htpasswd` | Credenciais hash para acesso dev ao nginx do Ditto. | Na autenticacao basic auth. | Adequado para laboratorio; nao para producao. |
| `services/ditto/tests/test_ditto_api.py` | Testes de integracao CRUD sobre a API Ditto. | Na validacao do twin. | Prova criacao, leitura e atualizacao de properties. |
| `services/ditto/wot/smartwatch-td.jsonld` | Thing Description W3C do smartwatch. | Em modelacao do device e do twin. | Diz que propriedades o dispositivo expone no modelo. |

## 6.6 `services/egw-controller/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `services/egw-controller/README.md` | Manual do orquestrador central. | Ponto de entrada do servico mais importante do projeto. | Lista endpoints, variaveis de ambiente e arquitetura interna. |
| `services/egw-controller/docker-compose.yml` | Compose isolado do controller. | Em desenvolvimento local do controller sozinho. | Sobe o servico com as env vars esperadas. |
| `services/egw-controller/Dockerfile` | Imagem Python do controller. | Em build container. | Formaliza o runtime FastAPI do orquestrador. |
| `services/egw-controller/pyproject.toml` | Metadata do pacote e tooling de desenvolvimento. | Em instalacao Python e build tooling. | Importante para testes e modo editavel. |
| `services/egw-controller/requirements.txt` | Dependencias do controller. | Em ambiente local/container. | Define FastAPI, httpx, pytest e restantes bibliotecas. |
| `services/egw-controller/examples/run_full_lifecycle.py` | Demo que chama sequencialmente UC1-UC8 pela API. | Em demonstracoes ou validacao manual. | E o melhor exemplo de "historia completa" do projeto. |
| `services/egw-controller/src/egw_controller/__init__.py` | Ponto de entrada do pacote. | Em imports do modulo. | Papel estrutural simples. |
| `services/egw-controller/src/egw_controller/api.py` | API FastAPI com todos os endpoints do controller. | Sempre que o controller corre. | Inicializa clientes no `lifespan` e encaminha para os use cases. |
| `services/egw-controller/src/egw_controller/config.py` | Le variaveis de ambiente e devolve configuracao normalizada. | No arranque do controller. | Centraliza URLs e parametros operacionais. |
| `services/egw-controller/src/egw_controller/models.py` | Modelos Pydantic e enums do dominio. | Na validacao das requests/responses. | E a "lingua comum" entre API e use cases. |
| `services/egw-controller/src/egw_controller/transaction.py` | Transaction manager em memoria. | Em todos os use cases multi-passo. | Implementa o controlo transacional descrito no paper. |
| `services/egw-controller/src/egw_controller/clients/__init__.py` | Marca o pacote de adaptadores externos. | Em imports internos. | Papel estrutural simples. |
| `services/egw-controller/src/egw_controller/clients/aca_py_client.py` | Wrapper HTTP para a Admin API do ACA-Py. | Nos UCs com SSI e DIDComm. | Cria convites, lista ligacoes, emite VCs e pede provas. |
| `services/egw-controller/src/egw_controller/clients/ditto_client.py` | Wrapper HTTP da API Ditto. | Nos UCs de twinning e consulta de features. | Faz CRUD basico sobre things. |
| `services/egw-controller/src/egw_controller/clients/fabric_client.py` | Adapter do ledger Fabric. | Em praticamente todo o ciclo de vida do dispositivo. | No estado atual, `invoke_chaincode` devolve um resultado simulado. |
| `services/egw-controller/src/egw_controller/clients/ipfs_client.py` | Wrapper HTTP da API IPFS. | Em snapshots/datasets. | Tem `add_json`, `cat` e `pin`. |
| `services/egw-controller/src/egw_controller/use_cases/__init__.py` | Marca o pacote dos use cases. | Em imports da API. | Papel estrutural simples. |
| `services/egw-controller/src/egw_controller/use_cases/uc1_oem_enrollment.py` | Implementa UC1. | Quando o OEM entra no consorcio. | Organiza convite, ligacao e emissao simbolica da Enrollment VC. |
| `services/egw-controller/src/egw_controller/use_cases/uc2_model_registration.py` | Implementa UC2. | No registo do modelo de dispositivo. | Encaminha para o Fabric adapter. |
| `services/egw-controller/src/egw_controller/use_cases/uc3_device_registration.py` | Implementa UC3. | No primeiro registo do dispositivo. | Mistura criacao de identidade/Genesis VC com ledger. |
| `services/egw-controller/src/egw_controller/use_cases/uc4_device_purchase.py` | Implementa UC4. | Na compra do dispositivo. | Move o dispositivo para transito. |
| `services/egw-controller/src/egw_controller/use_cases/uc5_device_claiming.py` | Implementa UC5. | Quando o consumidor reclama o dispositivo. | A verificacao SSI ainda esta simplificada. |
| `services/egw-controller/src/egw_controller/use_cases/uc6_device_twinning.py` | Implementa UC6. | Ao criar o twin no Ditto. | Cria o thing e marca twinning no ledger. |
| `services/egw-controller/src/egw_controller/use_cases/uc7_device_untwinning.py` | Implementa UC7. | Ao remover o twin. | Apaga o thing e regista untwinning. |
| `services/egw-controller/src/egw_controller/use_cases/uc8_device_selling.py` | Implementa UC8. | Na revenda do dispositivo. | A parte SSI da transferencia continua simplificada. |
| `services/egw-controller/tests/conftest.py` | Fixtures e injeccao de mocks para os testes do controller. | Antes de qualquer teste pytest deste servico. | Permite testar a API sem levantar toda a stack real. |
| `services/egw-controller/tests/test_transaction.py` | Testa o transaction manager. | Na validacao da camada de estado transacional. | Cobre create, complete, fail e listagens. |
| `services/egw-controller/tests/test_uc1_enrollment.py` | Testa UC1 e respetivo endpoint. | Na validacao do enrollment. | Verifica fluxo feliz com mocks. |
| `services/egw-controller/tests/test_uc2_model_registration.py` | Testa UC2 e endpoint. | Na validacao do registo de modelos. | Confirma a chamada ao adapter Fabric. |
| `services/egw-controller/tests/test_uc3_device_registration.py` | Testa UC3 e endpoint. | Na validacao do auto-registo. | Foca-se na orquestracao do fluxo. |
| `services/egw-controller/tests/test_uc4_device_purchase.py` | Testa UC4 e endpoint. | Na validacao da compra/transito. | Usa mocks do ledger. |
| `services/egw-controller/tests/test_uc5_device_claiming.py` | Testa UC5 e endpoint. | Na validacao do claiming. | Espelha a validacao simplificada atual. |
| `services/egw-controller/tests/test_uc6_device_twinning.py` | Testa UC6, incluindo falha do Ditto. | Na validacao do twinning. | E importante porque cobre sucesso e erro externo. |
| `services/egw-controller/tests/test_uc7_device_untwinning.py` | Testa UC7 e endpoint. | Na validacao do untwinning. | Confirma remocao do twin e resposta API. |
| `services/egw-controller/tests/test_uc8_device_selling.py` | Testa UC8 e endpoint. | Na validacao da revenda. | Fecha o conjunto dos oito use cases. |

## 6.7 `services/fabric/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `services/fabric/README.md` | Manual da rede Fabric usada no projeto. | Antes de ler chaincodes ou scripts. | Resume topologia, canal e deploy. |
| `services/fabric/docker-compose.yml` | Levanta orderer, peers, CouchDB, CAs e CLI. | Em execucao local da blockchain do ecossistema. | E a infraestrutura ledger em ambiente dev. |
| `services/fabric/chaincode/device-lifecycle/device_lifecycle.go` | Chaincode principal do ciclo de vida do dispositivo. | Nos UCs que alteram estados do device. | Contem os estados, as transicoes e as queries. |
| `services/fabric/chaincode/device-lifecycle/go.mod` | Dependencias Go do chaincode `device-lifecycle`. | Em build do chaincode. | Papel de packaging. |
| `services/fabric/chaincode/dataset-tracking/dataset_tracking.go` | Chaincode para datasets e CIDs do IPFS. | Nos fluxos de snapshot/historico. | Trata registo e transferencia de ownership dos datasets. |
| `services/fabric/chaincode/dataset-tracking/go.mod` | Dependencias Go do chaincode `dataset-tracking`. | Em build do chaincode. | Papel de packaging. |
| `services/fabric/configtx/configtx.yaml` | Configuracao do canal, organizacoes e politicas do Fabric. | Ao gerar genesis block e canal. | E um dos ficheiros mais importantes da rede. |
| `services/fabric/configtx/crypto-config.yaml` | Configuracao da geracao de material criptografico. | Na preparacao de MSPs e TLS. | Define orgs, orderer e peers. |
| `services/fabric/scripts/deploy-chaincode.sh` | Ajuda a fazer deploy dos chaincodes. | Depois da rede subir. | Traduz passos repetitivos de instalacao/aprovacao/commit. |
| `services/fabric/scripts/network-down.sh` | Desliga e limpa a rede dev. | Quando se quer resetar Fabric local. | Operacao de teardown. |
| `services/fabric/scripts/network-up.sh` | Sobe a rede e prepara artefactos iniciais. | Primeiro passo no arranque do ledger local. | E o script operacional mais importante deste modulo. |

## 6.8 `services/indy/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `services/indy/README.md` | Manual do identity ledger e dos schemas de VC. | Antes de SSI/ACA-Py. | Explica o pool Indy e o papel dos schemas. |
| `services/indy/docker-compose.yml` | Levanta a rede local baseada em `von-network`. | Em execucao local do ledger de identidade. | Disponibiliza portas do pool e web UI. |
| `services/indy/schemas/enrollment_vc.json` | Schema da Enrollment VC. | Em UC1. | Formaliza os atributos de inscricao do OEM. |
| `services/indy/schemas/genesis_vc.json` | Schema da Genesis VC. | Em UC3. | Formaliza a identidade de nascimento do dispositivo. |
| `services/indy/schemas/ownership_vc.json` | Schema da Ownership VC. | Em UC4, UC5 e UC8. | Formaliza propriedade e transferencias. |

## 6.9 `services/ipfs/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `services/ipfs/README.md` | Manual do no IPFS no contexto C2DTA. | Ao estudar snapshots e CIDs. | Explica add/cat/pin e a ligacao ao Fabric. |
| `services/ipfs/docker-compose.yml` | Levanta o no Kubo local. | Em execucao local do armazenamento descentralizado. | Exponibiliza API, gateway e swarm. |
| `services/ipfs/tests/test_ipfs_storage.py` | Testes de integracao do IPFS. | Na validacao de add, leitura e pinning. | Mostra o comportamento esperado da camada de storage. |

## 6.10 `services/mosquitto/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `services/mosquitto/README.md` | Manual do broker MQTT. | Antes de ler simulator e Ditto connectivity. | Explica topicos, TLS e ACL. |
| `services/mosquitto/docker-compose.yml` | Levanta o broker Mosquitto dev. | Em execucao local da telemetria. | Base da comunicacao SD -> EGW/DT. |
| `services/mosquitto/certs/generate-certs.sh` | Gera CA, cert do broker e certs de clientes. | Antes dos testes TLS ou da primeira subida segura. | Ficheiro operacional importante para o laboratorio. |
| `services/mosquitto/config/acl.conf` | ACL do broker. | Sempre que o broker valida permissoes. | Controla quem pode publicar e subscrever que topicos. |
| `services/mosquitto/config/mosquitto.conf` | Configuracao principal do Mosquitto. | Em runtime do broker. | Ativa listeners, TLS, persistencia e limites. |
| `services/mosquitto/tests/test_mqtt_connectivity.py` | Testes de conectividade TLS e pub/sub. | Na validacao da camada MQTT. | Prova handshake TLS e trafego no topico de telemetria. |

## 6.11 `services/smart-device-simulator/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `services/smart-device-simulator/README.md` | Manual do simulador de smartwatch. | Antes de correr o simulador. | Explica dados gerados, env vars e topico MQTT. |
| `services/smart-device-simulator/docker-compose.yml` | Levanta o simulador como container. | Em testes ou demos locais. | Espera um broker MQTT ja disponivel. |
| `services/smart-device-simulator/Dockerfile` | Imagem container do simulador. | Em build do servico. | Empacota o runtime Python. |
| `services/smart-device-simulator/pyproject.toml` | Metadata do pacote Python. | Em instalacao e tooling. | Papel de packaging. |
| `services/smart-device-simulator/requirements.txt` | Dependencias Python do simulador. | Em setup local/container. | Inclui paho-mqtt, pydantic e pytest. |
| `services/smart-device-simulator/examples/run_simulator.py` | Ponto de entrada CLI do simulador. | Na execucao manual do servico. | Le a configuracao, cria simulador e publisher e arranca o loop. |
| `services/smart-device-simulator/src/smart_device_simulator/__init__.py` | Ponto de entrada do pacote. | Em imports internos/externos. | Papel estrutural simples. |
| `services/smart-device-simulator/src/smart_device_simulator/config.py` | Le configuracao a partir de env vars. | No arranque do simulador. | Concentra UUID, broker, certs e parametros do sensor. |
| `services/smart-device-simulator/src/smart_device_simulator/models.py` | Define os modelos de dados do payload. | Sempre que ha uma leitura de sensor. | Contem `GeoLocation` e `SensorReading`. |
| `services/smart-device-simulator/src/smart_device_simulator/mqtt_publisher.py` | Publicador MQTT/TLS. | No streaming das leituras. | Traduz leituras do simulador em mensagens MQTT. |
| `services/smart-device-simulator/src/smart_device_simulator/simulator.py` | Motor de geracao de heartbeat e geolocalizacao. | No centro do servico. | E a fonte dos dados sinteticos. |
| `services/smart-device-simulator/tests/conftest.py` | Ajusta `src/` no path dos testes. | Antes dos testes pytest. | Ficheiro de suporte. |
| `services/smart-device-simulator/tests/test_mqtt_publisher.py` | Teste de integracao do publisher. | Na validacao da ligacao ao broker. | Verifica inicializacao do publisher e topico esperado. |
| `services/smart-device-simulator/tests/test_simulator.py` | Testes unitarios do simulador. | Na validacao da qualidade basica dos dados. | Cobre limites de BPM, drift e formato do payload. |

## 6.12 `yocto/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `yocto/README.md` | Guia de alto nivel para traduzir a arquitetura para uma imagem Yocto. | Ao planear a gateway real. | E aspiracional em varias partes. |
| `yocto/layers/meta-edgegateway/conf/layer.conf` | Configuracao base do layer Yocto. | Ao integrar o layer no build. | Diz ao BitBake onde estao recipes e prioridades. |
| `yocto/layers/meta-edgegateway/recipes-core/images/edgegateway-image.bb` | Receita da imagem principal da gateway. | No `bitbake edgegateway-image`. | Instala Docker, containerd, ferramentas de IA, observabilidade e recipes compose; hoje referencia `sd-simulator-compose`, que nao existe no layer. |
| `yocto/layers/meta-edgegateway/recipes-containers/edgegateway-containers.bb` | Receita placeholder para meta-pacotes de containers. | Atualmente mais como exemplo do que como implementacao real. | E uma lacuna clara do estado atual do layer. |
| `yocto/layers/meta-edgegateway/recipes-containers/didcomm-agent-compose/didcomm-agent-compose.bb` | Empacota os ficheiros de compose do DIDComm Agent para a imagem Yocto. | No deployment on-target. | Conecta o servico containerizado ao sistema embebido. |
| `yocto/layers/meta-edgegateway/recipes-containers/didcomm-agent-compose/didcomm-agent.service` | Unit systemd do DIDComm Agent. | No arranque do sistema operativo da gateway. | Responsavel por arrancar o compose correspondente. |
| `yocto/layers/meta-edgegateway/recipes-containers/didcomm-agent-compose/didcomm-agent/docker-compose.yml` | Compose on-target do DIDComm Agent. | Em runtime na imagem Yocto. | Define como o servico corre no dispositivo. |
| `yocto/layers/meta-edgegateway/recipes-containers/egw-controller-compose/egw-controller-compose.bb` | Empacota o compose do controller. | No deployment on-target. | Faz a ponte entre o servico e o mundo Yocto. |
| `yocto/layers/meta-edgegateway/recipes-containers/egw-controller-compose/egw-controller.service` | Unit systemd do controller. | No arranque do dispositivo. | Formaliza a execucao do compose do controller. |
| `yocto/layers/meta-edgegateway/recipes-containers/egw-controller-compose/egw-controller/docker-compose.yml` | Compose on-target do controller. | Em runtime na gateway embebida. | Traz a definicao do container para dentro da imagem. |
| `yocto/layers/meta-edgegateway/recipes-containers/mosquitto-compose/mosquitto-compose.bb` | Empacota o compose do broker MQTT. | No deployment on-target. | Ajuda a incluir o broker dentro da imagem. |
| `yocto/layers/meta-edgegateway/recipes-containers/mosquitto-compose/mosquitto.service` | Unit systemd do Mosquitto. | No boot da gateway. | Gere o arranque automatico do broker containerizado. |
| `yocto/layers/meta-edgegateway/recipes-containers/mosquitto-compose/mosquitto/docker-compose.yml` | Compose on-target do Mosquitto. | Em runtime na imagem. | Variante de deployment para dispositivo, separada do compose de desenvolvimento. |

## 6.13 `scripts/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `scripts/setup-env.sh` | Script bash que prepara o ambiente Yocto e chama `oe-init-build-env`. | No arranque do workflow Yocto. | Verifica se `yocto/poky` existe e guia os proximos passos do build. |

## 6.14 Materiais de referencia em `uni/paper/` e `uni/study_material/`

| Ficheiro | O que faz | Quando ler | Observacoes |
| --- | --- | --- | --- |
| `uni/paper/EdgeGateway_Paper.pdf` | Paper base da arquitetura Edge Gateway/C2DTA. | Antes de qualquer analise profunda do codigo. | E a principal referencia conceptual do projeto. |
| `uni/study_material/1.Dissertation_part_HowtoStart.pdf` | Material academico sobre como arrancar uma dissertacao. | Planeamento inicial. | Contexto metodologico, nao runtime. |
| `uni/study_material/2.Dissertation_part_DesignScienceResearch.pdf` | Material sobre `Design Science Research`. | Definicao da metodologia da tese. | Ajuda a justificar a natureza artefactual do projeto. |
| `uni/study_material/3.Dissertation_SLR.pdf` | Material sobre revisao sistematica da literatura. | Trabalho academico de estado da arte. | Relaciona-se sobretudo com o capitulo 2. |
| `uni/study_material/4.Dissertation_part_SR_PRISMA.pdf` | Material sobre PRISMA e revisoes sistematicas. | Na metodologia da revisao de literatura. | Complementa o ficheiro anterior. |
| `uni/study_material/5.Dissertation_part_CaseStudy.pdf` | Material sobre metodologia de estudo de caso. | Apoio academico. | Serve de referencia metodologica adicional. |
| `uni/study_material/6.Dissertation_part_Guidelines for a successful thesis writing.pdf` | Guia geral de escrita de tese. | Durante a escrita. | Foco academico, nao tecnico. |
| `uni/study_material/7.Dissertation_part_Applying-the-SLR-and-Mapping-Methodology.pdf` | Material sobre aplicacao de SLR e mapping study. | Na consolidacao do estado da arte. | Complementa o capitulo 2. |
| `uni/study_material/8.EscritaArtigo.pptx.pdf` | Slides sobre escrita de artigo. | Escrita academica. | Apoio metodologico. |
| `uni/study_material/9.LiteratureReviewTools.pdf` | Ferramentas para revisao de literatura. | Pesquisa bibliografica. | Contexto de processo academico. |
| `uni/study_material/10.MoreAboutPublications.pdf` | Material sobre publicacoes cientificas. | Na preparacao de outputs academicos. | Apoio complementar. |
| `uni/study_material/11.TypesDissertationProjects.pdf` | Explica tipos de projetos de dissertacao. | Definicao do enquadramento do trabalho. | Ajuda a posicionar a tese. |
| `uni/study_material/12.FinalCommentsPresentationDefense.pdf` | Material sobre defesa/apresentacao final. | Fase final da dissertacao. | Nao afeta implementacao tecnica. |

## 6.15 `uni/tese/`

| Ficheiro | O que faz | Quando entra em jogo | Observacoes |
| --- | --- | --- | --- |
| `uni/tese/main.tex` | Ficheiro principal LaTeX da dissertacao. | Na compilacao do manuscrito. | Importa os capitulos, define frontmatter, acronimos, bibliografia e estilo. |
| `uni/tese/references.bib` | Base bibliografica da tese. | Sempre que ha citacoes. | E a fonte de referencias usadas pelos capitulos. |
| `uni/tese/chapters/01-introduction.tex` | Capitulo 1 da tese. | Na leitura do enquadramento e do problema. | Ja contem texto substancial sobre IoT, PDE, SSI e DT. |
| `uni/tese/chapters/02-state-of-art.tex` | Capitulo 2 da tese. | Na leitura do estado da arte. | Ja contem metodologia SLR e enquadramento do corpus. |
| `uni/tese/chapters/03-c2dta-architecture.tex` | Capitulo 3 da tese. | Na fase de escrita da arquitetura. | Hoje ainda esta como placeholder curto. |
| `uni/tese/chapters/04-results-discussion.tex` | Capitulo 4 da tese. | Na fase de resultados e discussao. | Hoje ainda esta como placeholder curto. |
| `uni/tese/chapters/05-conclusions.tex` | Capitulo 5 da tese. | Na fase de conclusoes. | Hoje ainda esta como placeholder curto. |
| `uni/tese/imagens/iscte.png` | Logotipo usado na capa/folha inicial. | Na composicao visual do manuscrito. | Ativo em `main.tex`. |
| `uni/tese/imagens/ista.png` | Segundo logotipo institucional da capa. | Na composicao visual do manuscrito. | Ativo em `main.tex`. |

## 7. Explicacao classe a classe

Nesta secao entram apenas classes proprias do repositorio. Onde um modulo nao usa classes, a explicacao ficou na secao de ficheiros.

Tambem convem notar uma diferenca importante:

- em Python, o projeto usa classes, dataclasses, models Pydantic e enums
- em Go, os chaincodes usam `structs`, nao classes
- em YAML/JSON/Shell, o comportamento e declarativo, nao orientado a objetos

## 7.1 Classes em `services/egw-controller/src/egw_controller/models.py`

### `DeviceState`

- Tipo: enum.
- Serve para representar os estados do ciclo de vida do dispositivo.
- Valores:
  `MANUFACTURED` significa que o dispositivo ja nasceu no sistema.
  `AVAILABLE` significa que esta disponivel para venda/atribuicao.
  `IN_TRANSIT` significa que esta em processo de entrega/transferencia.
  `CLAIMED` significa que ja foi reclamado por um controlador/dono.
  `TWINNED` significa que ja tem gemeo digital ativo.
  `DECOMMISSIONED` significa que foi retirado de circulacao.
- Quem usa: `DeviceInfo`, os use cases e o chaincode conceptual do ciclo de vida.

### `DeviceType`

- Tipo: enum.
- Distingue dois tipos de dispositivos no projeto.
- Valores:
  `EGW` identifica a Edge Gateway.
  `SD` identifica um Smart Device.
- Quem usa: `DeviceRegistrationRequest` e `DeviceInfo`.

### `DeviceInfo`

- Tipo: modelo Pydantic.
- Representa o registo logico de um dispositivo no ecossistema.
- Campos:
  `device_id` e o identificador unico do dispositivo.
  `model_id` e a referencia ao modelo registado.
  `device_type` diz se e gateway ou smart device.
  `state` guarda o estado atual do ciclo de vida.
  `manufacturer_id` identifica o fabricante.
  `owner_did` guarda o DID do proprietario.
  `controller_did` guarda o DID de quem controla o dispositivo.
  `ditto_thing_id` aponta para o thing no Ditto.
  `genesis_vc_hash` guarda a referencia da Genesis VC.
  `ownership_vc_hash` guarda a referencia da Ownership VC.
- Quem usa: API e fluxos de lifecycle.

### `DatasetInfo`

- Tipo: modelo Pydantic.
- Representa um snapshot ou dataset associado ao twin.
- Campos:
  `dataset_id` identifica o dataset.
  `device_id` liga o dataset ao dispositivo.
  `ipfs_hash` guarda o CID/hash no IPFS.
  `owner_did` indica o dono logico do dataset.
  `size_bytes` e o tamanho do conteudo.
  `record_count` e o numero de registos incluidos.
  `start_time` e `end_time` delimitam o periodo temporal coberto.
- Quem usa: integracoes futuras de snapshots e dataset tracking.

### `EnrollmentRequest`

- Tipo: modelo Pydantic de request.
- Serve de input do UC1.
- Campos:
  `organization_name` e o nome do OEM.
  `organization_did` e o DID dessa organizacao.

### `ModelRegistrationRequest`

- Tipo: modelo Pydantic de request.
- Serve de input do UC2.
- Campos:
  `model_id` identifica o modelo.
  `manufacturer` indica o fabricante.
  `wot_td_hash` referencia o hash da Thing Description.

### `DeviceRegistrationRequest`

- Tipo: modelo Pydantic de request.
- Serve de input do UC3.
- Campos:
  `device_id` identifica o dispositivo.
  `model_id` aponta para o modelo.
  `device_type` distingue EGW de SD.
  `manufacturer_did` identifica o OEM emissor.

### `PurchaseRequest`

- Tipo: modelo Pydantic de request.
- Serve de input do UC4.
- Campos:
  `device_id` identifica o dispositivo comprado.
  `buyer_did` identifica o comprador.

### `ClaimRequest`

- Tipo: modelo Pydantic de request.
- Serve de input do UC5.
- Campos:
  `device_id` identifica o dispositivo reclamado.
  `controller_did` identifica o DID que vai controlar o dispositivo.
  `ownership_vc_hash` leva uma referencia simplificada a prova de ownership.

### `TwinRequest`

- Tipo: modelo Pydantic de request.
- Serve de input do UC6.
- Campos:
  `device_id` identifica o smart device.
  `twin_config` e um dicionario livre para configuracoes adicionais de twinning.

### `UntwinRequest`

- Tipo: modelo Pydantic de request.
- Serve de input do UC7.
- Campo:
  `device_id` identifica o twin a remover.

### `SellRequest`

- Tipo: modelo Pydantic de request.
- Serve de input do UC8.
- Campos:
  `device_id` identifica o dispositivo a vender.
  `buyer_did` identifica o novo comprador.
  `sale_config` reserva espaco para parametros adicionais da venda.

### `UCResponse`

- Tipo: modelo Pydantic de resposta.
- E a resposta generica dos use cases.
- Campos:
  `success` indica se o UC terminou com sucesso.
  `use_case` identifica qual UC respondeu.
  `device_id` devolve o device relevante.
  `message` resume o resultado.
  `data` transporta dados adicionais quando existirem.
- Quem usa: todos os endpoints `/uc/*`.

## 7.2 Classes em `services/egw-controller/src/egw_controller/transaction.py`

### `StepStatus`

- Tipo: enum.
- Valores:
  `PENDING` quando o passo ainda nao arrancou.
  `IN_PROGRESS` quando esta em execucao.
  `COMPLETED` quando terminou com sucesso.
  `FAILED` quando falhou.
- Quem usa: `TransactionStep`, `Transaction` e `TransactionManager`.

### `TransactionStep`

- Tipo: dataclass.
- Representa um passo individual de uma transacao multi-step.
- Campos:
  `step_id` e o identificador tecnico do passo.
  `description` explica o passo em linguagem humana.
  `status` guarda o estado do passo.
  `result` permite anexar um resultado estruturado.
  `error` guarda texto de erro quando falha.
  `started_at` e `completed_at` registam timestamps.
- Papel pratico: permite que cada UC decomponha o trabalho e exponha historico.

### `Transaction`

- Tipo: dataclass.
- Representa uma transacao completa de um use case.
- Campos:
  `transaction_id` e um UUID unico.
  `use_case` identifica o UC.
  `device_id` liga a transacao ao dispositivo.
  `steps` guarda a lista de passos.
  `created_at` regista quando nasceu.
  `status` resume o estado agregado.
- Metodos principais:
  `add_step()` cria um novo passo.
  `start_step()` marca um passo como iniciado.
  `complete_step()` marca um passo concluido e fecha a transacao quando todos terminam.
  `fail_step()` marca falha e falha a transacao inteira.
- Papel pratico: e o equivalente local de uma tabela de controlo transacional.

### `TransactionManager`

- Tipo: classe de servico em memoria.
- Estado interno:
  `_transactions` e um dicionario `transaction_id -> Transaction`.
- Metodos principais:
  `create()` cria e regista uma transacao.
  `get()` recupera uma transacao pelo ID.
  `list_active()` devolve pendentes e em progresso.
  `list_all()` devolve historico completo em memoria.
- Limite atual: nao persiste em disco nem em base de dados.

## 7.3 Classes em `services/egw-controller/src/egw_controller/clients/`

### `AcaPyClient`

- Papel: adapter HTTP para a Admin API dos agentes ACA-Py.
- Estado:
  `admin_url` guarda o endpoint base do agente.
- Metodos principais:
  `get_status()` faz health/status do agente.
  `create_oob_invitation()` cria um convite `Out-of-Band`.
  `receive_oob_invitation()` aceita um convite recebido.
  `list_connections()` lista ligacoes conhecidas.
  `issue_credential()` envia uma emissao de VC.
  `request_proof()` envia um pedido de prova.
  `create_public_did()` cria DID no ledger.
- Quem o usa: UCs relacionados com SSI, sobretudo UC1 e UC3.

### `DittoClient`

- Papel: adapter HTTP para a API do Eclipse Ditto.
- Estado:
  `base_url` define o servidor Ditto.
  `_auth` guarda a autenticacao basic auth.
- Metodos principais:
  `create_thing()` cria o Digital Twin no UC6.
  `get_thing()` le um thing completo.
  `delete_thing()` apaga o twin no UC7.
  `get_thing_features()` le apenas as features para futuros snapshots.
- Quem o usa: UCs de twinning/untwinning e consultas do twin.

### `FabricClient`

- Papel: adapter do ledger Fabric.
- Estado:
  `peer_url` identifica o peer alvo.
  `channel` identifica o canal.
  `cc_lifecycle` e `cc_dataset` guardam os nomes dos dois chaincodes.
- Metodos principais:
  `invoke_chaincode()` e o metodo base.
  `register_device_model()`, `manufacture_device()`, `make_available()`, `initiate_transit()`, `claim_device()`, `twin_device()`, `untwin_device()`, `decommission_device()` e `query_device()` cobrem lifecycle.
  `register_dataset()` e `query_datasets()` cobrem datasets.
- Limite importante: no estado atual, `invoke_chaincode()` nao executa de facto no Fabric; devolve um dicionario de sucesso simulado.

### `IPFSClient`

- Papel: adapter HTTP para o no IPFS.
- Estado:
  `api_url` define a API do Kubo.
- Metodos principais:
  `add_json()` adiciona JSON e devolve o CID.
  `cat()` recupera conteudo por CID.
  `pin()` fixa o CID para persistencia.
- Quem o usa: hoje sobretudo como capacidade pronta para snapshots, ainda nao totalmente explorada nos use cases.

## 7.4 Classes em `services/didcomm-agent/src/didcomm_agent/api.py`

### `CreateAgentRequest`

- Tipo: modelo Pydantic.
- Serve para criar ou recuperar um agente local via API.
- Campos:
  `agent_id` e o identificador interno do agente na API.
  `did` e o DID do agente.
  `endpoint` e o endpoint de inbox do agente.
  `label` e uma descricao humana opcional.

### `InvitationResponse`

- Tipo: modelo Pydantic.
- Representa um convite DIDComm serializado para HTTP.
- Campos:
  `did`, `endpoint`, `public_key`, `label` e `created_time`.
- Papel: e o contrato de saida do endpoint `/agent` e de aceites de convite.

### `AcceptInvitationRequest`

- Tipo: modelo Pydantic.
- Serve tanto para `/accept` como para `/complete`.
- Campos:
  `agent_id` identifica que agente local vai tratar o convite.
  `invitation` transporta o convite recebido.

### `SendMessageRequest`

- Tipo: modelo Pydantic.
- Input de `/send`.
- Campos:
  `agent_id` identifica o remetente local.
  `to_did` identifica o destinatario.
  `body` contem o payload de negocio.
  `msg_type` permite especificar o tipo DIDComm.

### `EnvelopeModel`

- Tipo: modelo Pydantic.
- Representa o envelope cifrado que atravessa a API.
- Campos:
  `ciphertext` contem os bytes cifrados em base64 urlsafe.
  `nonce` contem o nonce AEAD.
  `to` e `frm` guardam destinatario e remetente.
  `created_time` preserva o timestamp.
  `typ` indica o tipo de envelope.

### `MessageModel`

- Tipo: modelo Pydantic.
- Representa a mensagem plaintext devolvida por `/receive`.
- Campos:
  `id` e o identificador da mensagem.
  `type` e o tipo DIDComm.
  `body` e o conteudo.
  `to`, `frm` e `created_time` guardam routing e tempo.

### `ReceiveMessageRequest`

- Tipo: modelo Pydantic.
- Input de `/receive`.
- Campos:
  `agent_id` identifica o agente local.
  `envelope` transporta o envelope cifrado.

### `AppState`

- Tipo: classe simples de estado da app.
- Estado:
  `agents` e um dicionario de agentes em memoria.
  `storage` guarda a camada SQLite opcional.
- Papel: permite que a API FastAPI partilhe estado entre requests.

## 7.5 Classes em `services/didcomm-agent/src/didcomm_agent/crypto.py`

### `KeyPair`

- Tipo: dataclass imutavel.
- Representa um par de chaves X25519.
- Campos:
  `private_key` e a chave privada.
  `public_key` e a chave publica correspondente.
- Propriedades/metodos:
  `public_bytes` devolve bytes raw da chave publica.
  `private_bytes` devolve bytes raw da chave privada.
  `public_b64()` devolve a chave publica em base64 urlsafe.
  `private_b64()` devolve a chave privada em base64 urlsafe.
- Papel: e a unidade base de identidade criptografica do agente.

## 7.6 Classes em `services/didcomm-agent/src/didcomm_agent/exceptions.py`

### `UnknownPeerError`

- Tipo: excecao de dominio.
- Significa que se tentou falar com um DID que o agente ainda nao conhece.
- Papel: falha controlada e sem ambiguidade quando falta handshake.

### `MessageTamperingError`

- Tipo: excecao de dominio.
- Significa que a autenticidade/integridade do envelope falhou.
- Papel: transforma falhas AEAD numa mensagem de erro de dominio legivel.

## 7.7 Classes em `services/didcomm-agent/src/didcomm_agent/message.py`

### `DIDCommMessage`

- Tipo: dataclass.
- Representa a mensagem plaintext antes da cifra.
- Campos:
  `type` define o tipo de mensagem.
  `body` contem o conteudo de negocio.
  `to` e o destinatario.
  `frm` e o remetente.
  `id` e o identificador unico.
  `created_time` regista quando a mensagem nasceu.
- Metodos:
  `to_json()` serializa para JSON consistente.
  `from_json()` reconstrui a mensagem a partir de JSON.

### `EncryptedDIDCommMessage`

- Tipo: dataclass.
- Representa o envelope cifrado que viaja entre agentes.
- Campos:
  `ciphertext` contem o conteudo cifrado.
  `nonce` e o nonce do AEAD.
  `to` e `frm` preservam routing.
  `created_time` preserva o tempo original.
  `typ` indica o tipo MIME do envelope DIDComm.
- Metodos:
  `to_json()` serializa o envelope.
  `from_json()` reconstrui o envelope a partir de JSON.

## 7.8 Classes em `services/didcomm-agent/src/didcomm_agent/service.py`

### `DIDCommInvitation`

- Tipo: dataclass.
- Representa um convite de onboarding entre dois agentes.
- Campos:
  `did` identifica o agente que convida.
  `endpoint` indica onde esse agente pode ser alcancado.
  `public_key` publica a chave para handshake.
  `label` acrescenta contexto humano.
  `created_time` marca a criacao do convite.

### `_Peer`

- Tipo: dataclass interna.
- Representa um peer conhecido pelo agente.
- Campos:
  `did`, `endpoint`, `public_key_b64`, `label`.
- Metodo:
  `public_key()` reconstrui a chave publica do peer.
- Papel: e um registo interno; nao faz parte da API publica.

### `DIDCommAgent`

- Tipo: classe principal do servico.
- Estado:
  `did`, `endpoint` e `label` definem a identidade do agente.
  `_keypair` guarda as chaves locais.
  `_peers` guarda peers conhecidos.
- Propriedade:
  `public_key_b64` devolve a chave publica em base64 urlsafe.
- Metodos principais:
  `create_invitation()` cria convite para partilha.
  `accept_invitation()` guarda um peer e devolve contra-convite.
  `complete_handshake()` termina o onboarding apos receber o contra-convite.
  `list_peers()` lista DIDs conhecidos.
  `send_message()` constroi plaintext, deriva chave partilhada, cifra e devolve envelope.
  `receive_message()` valida peer, deriva chave, decifra e reconstrui a mensagem.
  `_store_peer()`, `_build_aad()` e `_build_aad_from_envelope()` sao helpers internos.
- Papel: concentra toda a logica do MVP DIDComm.

## 7.9 Classes em `services/didcomm-agent/src/didcomm_agent/storage.py`

### `Storage`

- Tipo: classe de persistencia SQLite.
- Estado:
  `db_path` guarda o caminho do ficheiro sqlite.
- Metodos principais:
  `_connect()` abre ligacao SQLite.
  `_init_db()` cria tabelas `agents` e `peers` se nao existirem.
  `upsert_agent()` guarda ou atualiza um agente.
  `get_agent()` recupera um agente com chaves.
  `upsert_peer()` guarda ou atualiza um peer conhecido.
  `list_peers()` lista DIDs de peers.
  `load_peers()` devolve convites reconstruidos para restaurar memoria.
  `export_state()` devolve um dump simples do estado persistido.
- Papel: e a camada que transforma o agente de efemero em semi-persistente.

## 7.10 Classes em `services/smart-device-simulator/src/smart_device_simulator/models.py`

### `GeoLocation`

- Tipo: modelo Pydantic.
- Representa coordenadas WGS84.
- Campos:
  `lat` e latitude valida entre -90 e 90.
  `lon` e longitude valida entre -180 e 180.
- Papel: garante que a geolocalizacao esta em formato coerente.

### `SensorReading`

- Tipo: modelo Pydantic.
- Representa uma leitura completa do smartwatch.
- Campos:
  `device_uuid` identifica o dispositivo.
  `heartbeat_bpm` guarda a pulsacao em bpm.
  `geolocation` guarda a posicao.
  `timestamp` guarda o instante UTC.
- Metodo principal:
  `to_mqtt_payload()` serializa a leitura para JSON.
- Papel: e o payload que sai do simulador para o MQTT.

## 7.11 Classes em `services/smart-device-simulator/src/smart_device_simulator/mqtt_publisher.py`

### `MQTTPublisher`

- Tipo: classe de runtime.
- Estado:
  `simulator` aponta para o gerador de dados.
  `broker_host` e `broker_port` definem o broker.
  `publish_interval_ms` define a frequencia de envio.
  `_running` controla o loop.
  `_client` guarda o cliente paho-mqtt.
  `_topic` guarda o topico `egw/<uuid>/telemetry`.
- Metodos principais:
  `_on_connect()`, `_on_disconnect()` e `_on_publish()` sao callbacks MQTT.
  `start()` abre ligacao, arranca o loop, le sensores e publica telemetria ate ser parado.
  `stop()` para o loop de publicacao.
- Papel: e a ponte entre o simulador e o broker.

## 7.12 Classes em `services/smart-device-simulator/src/smart_device_simulator/simulator.py`

### `SmartDeviceSimulator`

- Tipo: classe de simulacao.
- Constantes:
  `MIN_BPM` e `MAX_BPM` definem limites fisiologicos.
  `BPM_STEP_MAX` define a amplitude do random walk.
  `GEO_DRIFT_STD` define o desvio do drift geografico.
- Estado:
  `device_uuid` identifica o device.
  `_heartbeat`, `_lat` e `_lon` guardam o estado corrente do simulador.
- Metodos principais:
  `_next_heartbeat()` gera o proximo batimento com random walk e suave regressao ao normal.
  `_next_geolocation()` gera a proxima localizacao com drift gaussiano e clamp geografico.
  `read_sensors()` monta uma `SensorReading` completa com timestamp UTC.
- Papel: simula comportamento plausivel de um smartwatch.

## 7.13 Classes de teste

### `TestDittoAPI`

- Ficheiro: `services/ditto/tests/test_ditto_api.py`
- Papel: garante que a API do Ditto aceita criacao, leitura e atualizacao de things.
- O que protege: o contrato HTTP minimo esperado pelo resto da arquitetura.

### `TestIPFSStorage`

- Ficheiro: `services/ipfs/tests/test_ipfs_storage.py`
- Papel: garante que o no IPFS aceita ficheiros JSON, devolve CIDs e mantem pinning.
- O que protege: a camada de armazenamento descentralizado usada para datasets.

### `TestMQTTConnectivity`

- Ficheiro: `services/mosquitto/tests/test_mqtt_connectivity.py`
- Papel: garante ligacao TLS e pub/sub no topico de telemetria.
- O que protege: a espinha dorsal de comunicacao em tempo real do projeto.

### `TestMQTTPublisher`

- Ficheiro: `services/smart-device-simulator/tests/test_mqtt_publisher.py`
- Papel: garante que o publisher arranca com a configuracao esperada.
- O que protege: a ligacao basica entre simulador e broker.

### `TestSmartDeviceSimulator`

- Ficheiro: `services/smart-device-simulator/tests/test_simulator.py`
- Papel: garante ranges, drift, payload JSON e timestamps.
- O que protege: a qualidade minima dos dados sinteticos.

## 8. Apindice A - indice completo de classes por ficheiro

| Ficheiro | Classes |
| --- | --- |
| `services/egw-controller/src/egw_controller/models.py` | `DeviceState`, `DeviceType`, `DeviceInfo`, `DatasetInfo`, `EnrollmentRequest`, `ModelRegistrationRequest`, `DeviceRegistrationRequest`, `PurchaseRequest`, `ClaimRequest`, `TwinRequest`, `UntwinRequest`, `SellRequest`, `UCResponse` |
| `services/egw-controller/src/egw_controller/transaction.py` | `StepStatus`, `TransactionStep`, `Transaction`, `TransactionManager` |
| `services/egw-controller/src/egw_controller/clients/aca_py_client.py` | `AcaPyClient` |
| `services/egw-controller/src/egw_controller/clients/ditto_client.py` | `DittoClient` |
| `services/egw-controller/src/egw_controller/clients/fabric_client.py` | `FabricClient` |
| `services/egw-controller/src/egw_controller/clients/ipfs_client.py` | `IPFSClient` |
| `services/didcomm-agent/src/didcomm_agent/api.py` | `CreateAgentRequest`, `InvitationResponse`, `AcceptInvitationRequest`, `SendMessageRequest`, `EnvelopeModel`, `MessageModel`, `ReceiveMessageRequest`, `AppState` |
| `services/didcomm-agent/src/didcomm_agent/crypto.py` | `KeyPair` |
| `services/didcomm-agent/src/didcomm_agent/exceptions.py` | `UnknownPeerError`, `MessageTamperingError` |
| `services/didcomm-agent/src/didcomm_agent/message.py` | `DIDCommMessage`, `EncryptedDIDCommMessage` |
| `services/didcomm-agent/src/didcomm_agent/service.py` | `DIDCommInvitation`, `_Peer`, `DIDCommAgent` |
| `services/didcomm-agent/src/didcomm_agent/storage.py` | `Storage` |
| `services/smart-device-simulator/src/smart_device_simulator/models.py` | `GeoLocation`, `SensorReading` |
| `services/smart-device-simulator/src/smart_device_simulator/mqtt_publisher.py` | `MQTTPublisher` |
| `services/smart-device-simulator/src/smart_device_simulator/simulator.py` | `SmartDeviceSimulator` |
| `services/ditto/tests/test_ditto_api.py` | `TestDittoAPI` |
| `services/ipfs/tests/test_ipfs_storage.py` | `TestIPFSStorage` |
| `services/mosquitto/tests/test_mqtt_connectivity.py` | `TestMQTTConnectivity` |
| `services/smart-device-simulator/tests/test_mqtt_publisher.py` | `TestMQTTPublisher` |
| `services/smart-device-simulator/tests/test_simulator.py` | `TestSmartDeviceSimulator` |

## 9. Apindice B - inventario de cobertura por area

| Area | O que ficou coberto neste dossier |
| --- | --- |
| Raiz e CI | README, compose raiz, regras git e workflows de GitHub Actions |
| Documentacao tecnica | Todos os ficheiros de `docs/architecture`, `docs/paper`, `docs/research`, `docs/reviews` e `docs/roadmaps` existentes no momento da leitura |
| Servicos SSI | `services/aca-py`, `services/indy` e `services/didcomm-agent` |
| Servicos de dados e twin | `services/mosquitto`, `services/smart-device-simulator`, `services/ditto`, `services/ipfs` |
| Orquestracao central | Todo `services/egw-controller`, incluindo testes |
| Blockchain do ecossistema | Todo `services/fabric`, incluindo chaincodes, scripts e configs |
| Deployment embebido | Todo `yocto/` e `scripts/setup-env.sh` |
| Materiais academicos | `uni/paper`, `uni/study_material` e `uni/tese` |

## 10. Apindice C - correspondencia entre funcionalidades e modulos

| Funcionalidade | Modulos principais |
| --- | --- |
| Subir a stack toda em desenvolvimento | `docker-compose.yml` |
| Orquestrar UC1-UC8 por API | `services/egw-controller/src/egw_controller/api.py` e `services/egw-controller/src/egw_controller/use_cases/` |
| Controlar estado transacional dos UCs | `services/egw-controller/src/egw_controller/transaction.py` |
| Falar com ACA-Py | `services/egw-controller/src/egw_controller/clients/aca_py_client.py` e `services/aca-py/plugins/c2dta_protocols/` |
| Falar com Fabric a partir do controller | `services/egw-controller/src/egw_controller/clients/fabric_client.py` |
| Implementar ledger de lifecycle real | `services/fabric/chaincode/device-lifecycle/device_lifecycle.go` |
| Implementar ledger de datasets real | `services/fabric/chaincode/dataset-tracking/dataset_tracking.go` |
| Criar/remover twins | `services/egw-controller/src/egw_controller/clients/ditto_client.py`, `services/ditto/` |
| Transportar telemetria | `services/mosquitto/`, `services/smart-device-simulator/` |
| Guardar snapshots em storage descentralizada | `services/ipfs/` e `services/egw-controller/src/egw_controller/clients/ipfs_client.py` |
| Mensageria segura DIDComm | `services/didcomm-agent/src/didcomm_agent/` |
| Construir imagem Linux para a gateway | `yocto/layers/meta-edgegateway/` e `scripts/setup-env.sh` |
| Enquadrar academicamente a implementacao | `uni/paper/EdgeGateway_Paper.pdf`, `docs/`, `uni/tese/` |

## 11. Conclusao pratica

Se for preciso resumir o repositorio numa unica frase, ela seria esta:

Este projeto ja tem quase todos os blocos arquiteturais da C2DTA representados no repositorio, com um nivel forte de demonstracao e integracao local, mas ainda com varias partes criticas do fluxo SSI/Fabric/Yocto em modo simplificado, mockado ou preparatorio.

O lado mais "software de sistema" ja esta bastante visivel:

- controller
- simulador
- MQTT
- Ditto
- Fabric chaincodes
- Indy/ACA-Py de laboratorio
- IPFS
- MVP DIDComm

O lado mais "produto pronto para gateway real" ainda esta em preparacao:

- deployment Yocto final
- persistencia operacional do controller
- integracao real ponta a ponta com wallets
- invocacao real do Fabric a partir do controller
- pipeline completo de snapshots com IPFS/Fabric dentro dos UCs

Como documento de analise, este ficheiro deve ser suficiente para decidires com calma onde mexer primeiro sem teres de percorrer o repositorio as cegas.
