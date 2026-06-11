# Plano de Melhorias do Repositório — EdgeGateway (C2DTA)

**Data da revisão:** 2026-06-11
**Branch de trabalho:** `claude/review-repo-improvements-NdFMS`
**Âmbito:** todo o repositório — `services/`, `docker-compose.yml` (raiz e standalone),
`.github/workflows/`, `docs/`, `yocto/`, `scripts/`, `uni/`, configs de editor.

Este documento consolida a revisão completa do repositório: o que já foi corrigido
nesta branch, e **todas as alterações ainda necessárias**, ordenadas por prioridade,
com referência a ficheiro/linha, ação proposta, critério de aceitação e esforço estimado.

---

## 1. Requisitos pedidos e estado

| # | Pedido | Estado |
|---|--------|--------|
| R1 | Rever o repositório e dar sugestões de melhoria | ✅ Feito — revisão entregue em chat (27 achados em 4 níveis) |
| R2 | Resolver o bloco crítico | ✅ Feito — commits `f82ee53`, `425d091`, `d5ed516`, `bb8ecd2` |
| R3 | Dividir em 3 commits granulares | ✅ Feito — histórico reescrito com `--force-with-lease` |
| R4 | Avançar para o bloco Alto | 🟡 Parcial — 3 de 8 itens feitos (commits `3612ead`, `6414774`, `eb51aca`); restantes na secção 4 |
| R5 | Documento consolidado com todas as alterações necessárias | ✅ Este documento |

---

## 2. Trabalho já concluído nesta branch

| Commit | Conteúdo |
|--------|----------|
| `f82ee53` | Untrack de `nginx.htpasswd`, `didcomm.sqlite`, `.claude/settings.local.json`; `.gitignore` alargado (sqlite, htpasswd, artefactos LaTeX) |
| `425d091` | `.env.example` criado; `docker-compose.yml` raiz passa a exigir `${VAR:?}` para todas as credenciais (Ditto, CouchDB ×4, 5 wallet keys ACA-Py); `config.py` do egw-controller exige `DITTO_USER`/`DITTO_PASS` via `_require()`; `generate-htpasswd.sh` + `nginx.htpasswd.example` |
| `d5ed516` | README deduplicado (bloco PT removido, −143 linhas); Quick Start documenta fluxo `.env` |
| `bb8ecd2` | `.claude/settings.local.json` adicionado ao `.gitignore` |
| `3612ead` | 3 Dockerfiles: multi-stage, `USER app` não-root, `HEALTHCHECK` (egw-controller, didcomm-agent) |
| `6414774` | `pyproject.toml` raiz com ruff (E,F,W,B,I,UP) + mypy; 62 auto-fixes + 4 manuais (`StrEnum`, `F841`); ruff/mypy nos extras dev de cada serviço |
| `eb51aca` | CI alargado: mypy, bandit, hadolint, actionlint, gosec, testes de integração (ditto/ipfs/mosquitto), concurrency group |

Estado validado: `ruff` limpo, `mypy` limpo (com 2 exclusões documentadas), `bandit` limpo,
24 testes egw-controller + 6 simulator a passar.

---

## 3. P0 — Crítico (corrigir antes de qualquer outra coisa)

### 3.1 Merge conflicts não resolvidos em 6 ficheiros ⚠️ NOVO ACHADO

Conteúdo corrompido com marcadores `<<<<<<< HEAD` / `=======` / `>>>>>>> 02ed0cf…`
ficou commitado num merge antigo e está em `main`:

| Ficheiro | Linhas com marcadores |
|----------|----------------------|
| `docs/architecture/system-architecture.md` | 1, 178, 210, 239, 243, 245 (dois blocos de conflito) |
| `docs/architecture/didcomm-architecture.md` | 1, 208, 245 |
| `docs/architecture/communication-and-dataflow.md` | 1, 219, 261 |
| `docs/paper/edgegateway-paper-summary.md` | 1, 160, 180 |
| `docs/roadmaps/milestone-plan.md` | 1, 142, 215 |
| `yocto/layers/meta-edgegateway/recipes-core/images/edgegateway-image.bb` | 17–24 |

O caso do `.bb` é o mais grave: o conflito está dentro de `IMAGE_INSTALL`, pelo que a
layer Yocto **não compila** — o lado `HEAD` apaga os pacotes compose, o outro lado
instala-os.

- **Ação:** resolver cada conflito manualmente (escolher/fundir o conteúdo correto);
  no `.bb` manter a lista de pacotes compose. Adicionar um passo de CI que falhe se
  `grep -rln "^<<<<<<< " .` devolver resultados.
- **Aceitação:** zero marcadores no repo; `bitbake -p` valida a receita (ou pelo menos
  parse local da sintaxe); guard no CI.
- **Esforço:** 1–2 h.

### 3.2 Rotação de credenciais + histórico Git

Os hashes do `nginx.htpasswd` e todas as passwords/wallet keys de dev continuam
acessíveis no histórico (`71ba0fc`, `74c169d` e anteriores).

- **Ação:** (a) rodar as credenciais reais — nunca reutilizar `c2dta`, `c2dta-devops`,
  `adminpw`, `*-key-dev`; (b) decidir se se purga o histórico com `git filter-repo`
  (reescreve SHAs — coordenar com colaboradores antes).
- **Aceitação:** credenciais antigas inválidas em qualquer ambiente; decisão documentada.
- **Esforço:** 30 min (rotação) + 1–2 h (filter-repo, opcional).

### 3.3 Compose standalone ainda com credenciais hardcoded

O refactor `${VAR:?}` cobriu apenas o compose raiz. Ficaram 9 ocorrências em 4 ficheiros:

| Ficheiro | Linha | Credencial |
|----------|-------|------------|
| `services/aca-py/docker-compose.yml` | 22, 49, 76, 103, 130 | `ACAPY_WALLET_KEY=*-key-dev` (×5) |
| `services/ditto/docker-compose.yml` | 65 | `DEVOPS_PASSWORD=c2dta-devops` |
| `services/egw-controller/docker-compose.yml` | 13 | `DITTO_PASS=c2dta` |
| `services/fabric/docker-compose.yml` | 45, 90 | `COUCHDB_PASSWORD=adminpw` (×2) |

- **Ação:** aplicar o mesmo padrão `${VAR:?}` (os standalone leem o `.env` da raiz via
  `env_file` ou caminho relativo), ou eliminar os compose standalone e usar
  `docker compose -f docker-compose.yml --profile <serviço>` (ver 5.6).
- **Aceitação:** `grep -rE "(key-dev|adminpw|c2dta)" services/*/docker-compose.yml` vazio.
- **Esforço:** 1–2 h.

### 3.4 FabricClient é uma simulação — README sobre-promete

`services/egw-controller/src/egw_controller/clients/fabric_client.py:45-53`:
`invoke_chaincode()` apenas faz log e devolve `{"status": "ok", ...}` hardcoded.
**Nenhum use case toca realmente no Fabric.** Os chaincodes Go existem e são
instalados pelos scripts, mas o controller nunca lhes chama. O README afirma
"All 8 use cases … are fully implemented and runnable", o que não corresponde
à integração real — relevante também para a credibilidade da dissertação.

- **Ação (curto prazo):** corrigir o README para "Fabric integration is currently
  simulated at the client layer; chaincodes are deployed but not yet invoked by the
  controller". **Ação (médio prazo):** implementar invocação real — `fabric-sdk-py`,
  gateway gRPC (Fabric Gateway API, recomendado para 2.5), ou `docker exec` no
  `fabric-cli` como passo intermédio.
- **Aceitação:** curto prazo — README fiel à realidade; médio prazo — teste de
  integração que regista um device e o lê de volta do ledger real.
- **Esforço:** 15 min (README) / 2–4 dias (integração real).

### 3.5 Validação TLS desativada em dois pontos

| Ficheiro | Problema |
|----------|----------|
| `services/smart-device-simulator/src/smart_device_simulator/mqtt_publisher.py:51` | `ctx.check_hostname = False` — anula a verificação de hostname apesar de `CERT_REQUIRED` |
| `services/ditto/connectivity/mqtt-connection.json:14` | `"validateCertificates": false` — Ditto liga ao Mosquitto sem validar o certificado |

- **Ação:** no simulador, tornar configurável (`MQTT_TLS_INSECURE`, default `false`) e
  emitir warning explícito quando ativo; nos certs, garantir SAN `DNS:mosquitto` no
  certificado do broker (ajustar `generate-certs.sh`) para a validação passar dentro
  da rede compose. No JSON do Ditto, `validateCertificates: true` + `ca` configurado.
- **Aceitação:** ligação MQTT estabelece com validação completa; teste de integração
  mosquitto verifica que um cert inválido é rejeitado.
- **Esforço:** 2–3 h.

---

## 4. P1 — Alto (itens restantes do bloco Alto + novos achados)

### 4.1 Tratamento de exceções genérico (9 ocorrências)

Todos os use cases capturam `except Exception` e devolvem `UCResponse(success=False)`,
escondendo erros de programação e devolvendo sempre HTTP 200:

`uc1_oem_enrollment.py:56`, `uc2_model_registration.py:45`, `uc3_device_registration.py:72`,
`uc4_device_purchase.py:32`, `uc5_device_claiming.py:38`, `uc6_device_twinning.py:61`,
`uc7_device_untwinning.py:45`, `uc8_device_selling.py:48`
(+ `didcomm-agent/src/didcomm_agent/service.py:107`, este aceitável — mapeia para
`MessageTamperingError`).

- **Ação:** capturar apenas `httpx.HTTPError`/`httpx.TimeoutException` (falhas de
  serviços externos → 502/504) e exceções de domínio próprias; deixar bugs propagarem
  para o handler global do FastAPI (500 + log). Definir hierarquia
  `C2DTAError → FabricError | DittoError | AcaPyError | IPFSError`.
- **Aceitação:** nenhum `except Exception` em `use_cases/`; testes cobrem caminho de
  erro de serviço externo (mock a lançar `httpx.ConnectError` → 502).
- **Esforço:** 1 dia (toca 8 ficheiros + testes; muda códigos HTTP devolvidos — **decisão
  de contrato de API a confirmar**).

### 4.2 Validação de input nos modelos e endpoints

`models.py`: ~14 campos `str` sem qualquer restrição (`organization_name:35`,
`organization_did:37`, `model_id:73-75`, `device_id:81-84`, `buyer_did`,
`controller_did`, `ownership_vc_hash`, etc.).
`api.py:176,183`: `device_id`, `state`, `owner` crus passados ao chaincode.

- **Ação:** `Field(min_length=…, max_length=…, pattern=…)` em todos os campos:
  DIDs → `^did:[a-z0-9]+:[A-Za-z0-9.\-_:]+$`; device/model IDs →
  `^[A-Za-z0-9_\-]{1,64}$`; hashes → `^[A-Fa-f0-9]{64}$` (SHA-256) ou multibase;
  `state` → `Literal`/`DeviceState` enum no query param.
- **Aceitação:** payload inválido → 422 com mensagem clara; testes parametrizados de
  rejeição por endpoint.
- **Esforço:** ½ dia. **Regex/limites exatos a confirmar contigo.**

### 4.3 Sync-em-async: 14 métodos `httpx.Client` chamados de handlers `async`

`aca_py_client.py` (7 métodos), `ditto_client.py` (4), `ipfs_client.py` (3) — todos
bloqueiam o event loop quando chamados pelos endpoints `async def` de `api.py`.

- **Ação:** migrar para `httpx.AsyncClient` partilhado (criado no `lifespan`, fechado
  no shutdown) e `await` em toda a cadeia use case → client. Em alternativa mínima,
  tornar os handlers `def` síncronos (FastAPI usa threadpool) — menos trabalho mas
  menos correto a prazo. **Recomendado: AsyncClient.**
- **Aceitação:** zero `httpx.Client` em `clients/`; testes continuam verdes
  (`pytest-asyncio` já configurado).
- **Esforço:** 1 dia.

### 4.4 Refactor para `Depends()` e remoção das exclusões mypy

`pyproject.toml` raiz exclui `egw_controller/api.py` e `didcomm_agent/api.py` do mypy
porque ambos usam singletons de módulo inicializados a `None` (18 violações
`Optional[T]` vs `T` legítimas).

- **Ação:** mover os clientes para `app.state` no `lifespan` e injetar com
  `Depends()`; apagar as duas exclusões do mypy. Combina naturalmente com o 4.3.
- **Aceitação:** `mypy` limpo sem exclusões; conftest dos testes adaptado
  (override de dependencies em vez de monkeypatch de globals).
- **Esforço:** ½ dia (junto com 4.3).

### 4.5 Robustez do didcomm-agent

- `message.py:36,71` — `from_json()` acede `data["…"]` sem tratamento; JSON malformado
  → `KeyError`/stack trace em vez de 400.
- `message.py`, `crypto.py`, `storage.py` — sem qualquer logger (operações cripto e BD
  invisíveis nos logs).
- **Ação:** validar payloads com Pydantic ou `try/except (KeyError, json.JSONDecodeError)`
  → `InvalidMessageError` (→ 400 na API); adicionar `logging.getLogger(__name__)` aos
  3 módulos com eventos chave (peer criado, mensagem cifrada/decifrada, falha de auth).
- **Aceitação:** POST com JSON malformado devolve 400; logs registam operações.
- **Esforço:** ½ dia.

### 4.6 Erros ignorados nos chaincodes Go (~15 ocorrências)

- `dataset_tracking.go:65-66` — `fmt.Sscanf(args[4], "%d", …)` sem verificar erro:
  input não-numérico grava dataset com zeros silenciosamente.
- `dataset_tracking.go:148` — `json.Unmarshal` sem verificação de erro.
- `device_lifecycle.go:110,111,138,216,300,326` e `dataset_tracking.go:80,81,130,151,152`
  — `_ :=` em `CreateCompositeKey`/`json.Marshal`.
- **Ação:** substituir `Sscanf` por `strconv.Atoi` com retorno de erro ao cliente;
  verificar todos os erros (gosec no CI, adicionado em `eb51aca`, passará a apanhar
  regressões). Adicionar testes Go (`shimtest` ou `counterfeiter`) — hoje os chaincodes
  têm **zero testes**.
- **Aceitação:** `errcheck`/`gosec` limpos; `go test ./...` com cobertura dos caminhos
  de erro; CI corre `go test`.
- **Esforço:** 1 dia.

### 4.7 Inconsistência do LEDGER_SEED do Indy

`docker-compose.yml:390` usa `000000000000000000000000Steward1`;
`services/indy/docker-compose.yml:19` usa `C2DTA000000000000000000Steward1`.
Genesis incompatível se ambos forem usados; wallets registadas num não funcionam no outro.

- **Ação:** unificar via `${INDY_LEDGER_SEED:?}` no `.env` (acrescentar ao
  `.env.example` com nota de que é dev-only).
- **Aceitação:** um único valor de seed em todo o repo, vindo do `.env`.
- **Esforço:** 15 min.

### 4.8 Lockfiles e reprodutibilidade de dependências

Nenhum serviço tem lockfile; tudo `>=` aberto.

- **Ação:** adotar `uv` (recomendado — rápido, `uv lock`/`uv sync`, um lockfile por
  serviço) ou `pip-tools`; atualizar Dockerfiles para instalar a partir do lock;
  ativar Dependabot/Renovate (`.github/dependabot.yml` com ecossistemas `pip`,
  `gomod`, `docker`, `github-actions`).
- **Aceitação:** builds reproduzíveis; PRs automáticos de atualização.
- **Esforço:** 1 dia. **Escolha de ferramenta a confirmar contigo.**

### 4.9 Placeholder em produção de VC

`uc3_device_registration.py:56` — `genesis_vc_hash="genesis-vc-hash-placeholder"`
gravado no ledger (simulado) em vez do hash real da credencial emitida.

- **Ação:** calcular SHA-256 do Genesis VC devolvido pelo ACA-Py
  (`issue_credential` response) e usar esse valor.
- **Aceitação:** hash real, teste verifica formato `[a-f0-9]{64}`.
- **Esforço:** 1–2 h.

---

## 5. P2 — Médio (manutenibilidade e operação)

### 5.1 Healthchecks e `depends_on` no compose raiz

Sem healthcheck: `orderer.c2dta.example.com`, `couchdb0`, `couchdb1`,
`ca.consortium`, `ca.oem`, `fabric-cli`, e os 5 serviços Ditto internos.
`depends_on` sem `condition: service_healthy`: peers → couchdb (linhas 265-266,
313-314), fabric-cli → peers.

- **Ação:** healthchecks (CouchDB: `curl -f localhost:5984/_up`; orderer: porta TCP
  7053; CA: `curl -fk https://localhost:7054/cainfo`); converter `depends_on` para
  forma longa com `condition`.
- **Esforço:** 2–3 h.

### 5.2 Exposição de portas e docker.sock

- `fabric-cli` e ambos os peers montam `/var/run/docker.sock` (linhas 259, 307) —
  necessário no Fabric clássico para chaincode-em-container, mas vale a pena migrar
  para **chaincode-as-a-service (CCaaS)** e eliminar o socket.
- Portas desnecessárias no host: CAs (7054/8054), orderer admin (7053), IPFS swarm
  (4001), Indy 9701–9708 (basta 9000 para a UI).
- **Ação:** remover `ports:` dos serviços só-internos (a rede compose chega);
  documentar exceções.
- **Esforço:** 1–2 h + teste de regressão do demo.

### 5.3 Perfis dev/prod no compose

`ENABLE_DUMMY_AUTH=true`, `ACAPY_ADMIN_INSECURE_MODE=true`, `AUTO_ACCEPT_*=true`
são aceitáveis em demo mas não há nada que impeça deploy assim.

- **Ação:** `docker-compose.override.yml` (dev, auto-carregado) com os flags inseguros
  + compose base limpo; ou profiles `dev`/`prod`. Adicionar `ACAPY_ADMIN_API_KEY`
  no perfil prod.
- **Esforço:** ½ dia.

### 5.4 Receitas Yocto em falta

`edgegateway-image.bb:61-66` referencia receitas "a criar" que não existem:
`python3-aries-cloudagent`, `python3-fabric-sdk`, `eclipse-ditto`, `kubo`.
Mesmo após resolver o conflito (3.1), `bitbake edgegateway-image` falha.
`build-yocto.yml` exige runner `[self-hosted, yocto]` inexistente.

- **Ação:** ou criar as receitas mínimas, ou comentar as referências e reduzir a imagem
  ao que existe (docker + compose units); no workflow, manter só `workflow_dispatch`
  até existir runner, e documentar o provisionamento em `yocto/README.md`.
- **Esforço:** 2 h (limpeza) ou 2–3 dias (receitas completas).

### 5.5 Ficheiros de governança

Não existem: `CONTRIBUTING.md` (estratégia de branches main/dev incluída),
`SECURITY.md` (projeto de segurança/SSI — importante), `CODE_OF_CONDUCT.md`,
`.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`, `CHANGELOG.md`.

- **Esforço:** ½ dia.

### 5.6 Duplicação compose raiz vs standalone

7 compose standalone duplicam (e divergem de) o raiz — já causou o bug do seed (4.7)
e as креdenciais órfãs (3.3). O standalone do aca-py tem 8 agentes vs 5 no raiz;
o do egw-controller exige rede externa `c2dta-net` pré-criada.

- **Ação recomendada:** um único compose raiz com `profiles:` (`mqtt`, `ditto`,
  `fabric`, `indy`, `ssi`, `full`) e apagar os standalone; alternativa: mantê-los
  como `include:` do compose raiz (Compose v2.20+).
- **Esforço:** 1 dia.

### 5.7 Higiene de artefactos tracked

- `services/didcomm-agent/src/didcomm_agent.egg-info/` — 5 ficheiros de build tracked
  (o `.gitignore` já cobre, falta `git rm --cached`).
- `uni/` com 23 MB no repo de código: artefactos LaTeX já gitignorados, mas os PDFs
  pesados e a tese continuam aqui. **Decisão pendente: repo separado para a tese**
  (recomendado — produto e licenciamento distintos) vs manter.
- **Esforço:** 15 min (egg-info) / 1 dia (split do uni/).

### 5.8 Correções de metadados

| Item | Ficheiro | Correção |
|------|----------|----------|
| Caminho do paper errado | `README.md` (árvore do repo, ~linha 125) | `EdgeGateway_Paper.pdf` está em `uni/paper/`, não na raiz |
| `requires-python` inconsistente | `didcomm-agent` e `smart-device-simulator` dizem `>=3.11`; README e CI usam 3.12 | uniformizar para `>=3.12` |
| Licença contraditória | `scripts/setup-env.sh:4` tem SPDX `Apache-2.0`; repo é MIT | mudar para `MIT` ou remover o header |
| READMEs de serviço com creds antigas | `services/ditto/README.md:12,46,85`, `services/egw-controller/README.md:70-76` | atualizar para o fluxo `.env` |
| Data futura | `services/aca-py/README.md:66` ("2026-03-19") | verificar/corrigir |
- **Esforço:** 1–2 h total.

### 5.9 Permissões e parâmetros dos certificados MQTT

`generate-certs.sh`: chaves cliente/servidor 2048-bit (CA é 4096 ✓), sem `chmod 600`
nas chaves privadas, sem SAN (necessário para 3.5).

- **Ação:** 4096-bit ou EC P-256 em tudo; `umask 077`/`chmod 600`; adicionar
  `subjectAltName = DNS:mosquitto` ao cert do broker.
- **Esforço:** 1–2 h.

### 5.10 Pipeline de testes — gaps remanescentes

- Chaincodes Go: **zero testes** (ver 4.6).
- Plugins `services/aca-py/plugins/c2dta_protocols/`: sem testes nem job de CI.
- Smoke E2E real: os testes de integração correm no CI mas fazem skip sem serviços;
  falta um job (`workflow_dispatch` ou nightly) com `docker compose up` dos serviços
  leves (mosquitto+ditto+ipfs) + `run_full_lifecycle.py`.
- **Esforço:** 1–2 dias.

---

## 6. P3 — Polish

| Item | Detalhe | Esforço |
|------|---------|---------|
| `E501` backlog | 29 linhas longas; remover `ignore = ["E501"]` do `pyproject.toml` raiz após wrap | 1–2 h |
| `Claude.md` → `CLAUDE.md` | Convenção do Claude Code é maiúsculas | 5 min |
| `Makefile`/`justfile` na raiz | `make demo / test / lint / smoke / certs` | 1–2 h |
| `docs/GUIA_COMPLETO.md` solto | Mover para `docs/guides/` ou fundir com o codebase guide | 15 min |
| Conventional commits | Já em uso nesta branch; formalizar (commitlint ou nota no CONTRIBUTING) | 30 min |
| Hadolint threshold | Subir de `error` para `warning` quando os Dockerfiles estiverem limpos | 15 min |
| Idioma das docs | READMEs de serviço em PT, docs/architecture em EN, README raiz em EN — escolher convenção e anotar no CONTRIBUTING | — |
| Tese (contexto) | `uni/tese`: capítulos 3–5 por escrever (conforme `Claude.md`); fora do âmbito do código | — |

---

## 7. Sequência recomendada

```
Semana 1  ─ P0 completo:
            3.1 merge markers (primeiro — corrige conteúdo corrompido em main)
            3.2 rotação de credenciais
            3.3 compose standalone (ou decisão 5.6 de os eliminar já)
            3.4 README fiel (curto prazo) · 3.5 TLS
Semana 2  ─ P1 código:
            4.3+4.4 async + Depends (juntos)  →  4.1 exceções  →  4.2 validação
            4.5 didcomm robustez · 4.7 seed · 4.9 placeholder
Semana 3  ─ P1/P2 infra:
            4.6 chaincode Go + testes · 4.8 lockfiles+dependabot
            5.1 healthchecks · 5.3 perfis dev/prod · 5.8 metadados
Backlog   ─ 3.4 integração Fabric real · 5.4 receitas Yocto · 5.6 unificação compose
            5.7 split uni/ · 5.10 E2E nightly · P3
```

**Decisões que precisam do dono do repo antes de avançar:**
1. Purgar histórico Git (3.2) — sim/não.
2. Códigos HTTP de erro da API (4.1) — 502/504 para falhas externas ok?
3. Regex/limites de validação (4.2).
4. `uv` vs `pip-tools` (4.8).
5. Eliminar compose standalone a favor de profiles (5.6) — sim/não.
6. Split do `uni/` para repo próprio (5.7) — sim/não.
