# Worklog de melhorias autónomas — 2026-06-11

**Branch:** `claude/review-repo-improvements-NdFMS`
**Documento mãe:** [`docs/reviews/repo-improvement-plan.md`](repo-improvement-plan.md)

Este worklog regista, na ordem em que foram aplicadas, todas as alterações
feitas na sessão autónoma que se seguiu ao plano consolidado. Cada secção
corresponde a um commit, identifica o item do plano que fecha e descreve
*o que* mudou e *porquê*.

---

## Sumário

| # | Commit | Item do plano | Resumo | Estado |
|---|--------|---------------|--------|--------|
| 1 | `e4c11d4` | P0 · 3.1 | Resolver conflict markers em 6 ficheiros + guard no CI | ✅ |
| 2 | `b529958` | P3 · novo | Opt-in para Node 24 (deadline 16/6 em GH Actions) | ✅ |
| 3 | `c5bb152` | P0 · 3.3 + P1 · 4.7 | Credenciais nos compose standalone via `${VAR:?}` + seed do Indy unificada | ✅ |
| 4 | `d83da7b` | P0 · 3.5 | TLS hostname + cert validation end-to-end (simulator, Ditto, certs) | ✅ |
| 5 | `adea289` | P1 · 4.9 | Hash real (SHA-256) do Genesis VC no UC3 | ✅ |
| 6 | `f34c4a8` | P1 · 4.5 | Parsing JSON seguro, handlers de excepção e loggers em falta no didcomm-agent | ✅ |
| 7 | `2c4db75` | P1 · 4.6 | Verificação de **todos** os erros nos dois chaincodes Go | ✅ |
| 8 | `77161c5` | P2 · 5.8 | Metadados: paper path, `requires-python` 3.12, SPDX MIT, READMEs de serviço | ✅ |
| 9 | `e830761` | P2 · 5.7 | Untrack do `.egg-info` do didcomm-agent | ✅ |

---

## 1. Resolver merge markers (commit `e4c11d4`)

**Item do plano:** P0 · 3.1.

Seis ficheiros vinham com blocos `<<<<<<< HEAD … ======= … >>>>>>> 02ed0cf` por
resolver desde um merge antigo. Resoluções:

| Ficheiro | Decisão | Razão |
|---|---|---|
| `docs/paper/edgegateway-paper-summary.md` | Lado HEAD | Documento alinhado ao paper C2DTA (rev. 2026-03-19) vs stub genérico de 2025 |
| `docs/architecture/didcomm-architecture.md` | Lado HEAD | Idem |
| `docs/architecture/communication-and-dataflow.md` | Lado HEAD | Idem |
| `docs/roadmaps/milestone-plan.md` | Lado OTHER | Documenta as 7 fases já implementadas e o seu estado real |
| `docs/architecture/system-architecture.md` | Merge manual | Corpo HEAD; a tabela de mapeamento serviço→docs do OTHER preservada como nova secção "Módulos implementados" (sem as linhas especulativas sobre IA/k3s) |
| `yocto/.../edgegateway-image.bb` | Merge manual | Conflito dentro de `IMAGE_INSTALL` — partia a receita. Manti `mosquitto-compose` e `egw-controller-compose` (recipes existem); descartei `didcomm-agent-compose` (substituído por ACA-Py, conforme a própria DESCRIPTION) e `sd-simulator-compose` (sem receita; ferramenta dev) |

Acrescentei um job `merge-markers` ao CI: `grep -rEln "^(<{7}\|>{7}) " --exclude-dir=.git .`
falha o build se algum marcador reaparecer. O padrão é construído via repetition
syntax para o próprio workflow não se auto-flaggar.

---

## 2. Opt-in para Node.js 24 (commit `b529958`)

**Item:** novo, surgiu durante o run #22 (mas com deadline em 5 dias).

Cada job no run #22 emitia *"Node.js 20 actions are deprecated. … forced to
Node 24 by default starting June 16th, 2026."* Aproveitei a janela para fazer
opt-in agora, expondo qualquer incompatibilidade enquanto monitorizo:

```yaml
env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"
```

Em `ci.yml` e `build-yocto.yml` ao nível do workflow (aplica-se a `actions/
checkout`, `setup-python`, `setup-go`).

---

## 3. Credenciais nos compose standalone + seed Indy (commit `c5bb152`)

**Itens:** P0 · 3.3 e P1 · 4.7.

O refactor de `425d091` só tinha tocado no compose raiz. Resolução agora dos 9
restantes:

| Ficheiro | Linhas | Antes | Depois |
|---|---|---|---|
| `services/aca-py/docker-compose.yml` | 22, 49, 76, 103, 130 | `ACAPY_WALLET_KEY=<algo>-key-dev` | `${ACAPY_<...>_WALLET_KEY:?…}` |
| `services/ditto/docker-compose.yml` | 65 | `DEVOPS_PASSWORD=c2dta-devops` | `${DITTO_DEVOPS_PASSWORD:?…}` |
| `services/egw-controller/docker-compose.yml` | 12, 13 (+ removido `version: "3.9"`) | `DITTO_USER=ditto / DITTO_PASS=c2dta` | `${DITTO_USER:?…}` / `${DITTO_PASS:?…}` |
| `services/fabric/docker-compose.yml` | 44, 45, 71, 72, 89, 90, 116, 117 | `admin` / `adminpw` | `${COUCHDB_USER:?…}` / `${COUCHDB_PASSWORD:?…}` |

Mensagem de erro de todos os `:?` aponta para o `.env` da raiz e mostra o comando:
`set via repo-root .env (run with --env-file ../../.env)`.

**Inconsistência do `LEDGER_SEED`** (item 4.7): o compose raiz usava
`000000000000000000000000Steward1` e o standalone do Indy
`C2DTA000000000000000000Steward1`. Genesis files diferentes, wallets
incompatíveis. Unifiquei via `${INDY_LEDGER_SEED:?…}` e documentei a variável no
`.env.example` com o valor von-network por omissão e aviso de "dev-only".

Validação: `docker compose --env-file <fake> config --quiet` passa para o root
e os 5 standalone tocados.

---

## 4. TLS validation end-to-end (commit `d83da7b`)

**Item:** P0 · 3.5.

Dois pontos enfraqueciam o TLS:

**4.1 Simulador — `mqtt_publisher.py:51`:** `ctx.check_hostname = False`
hardcoded. Tornei configurável:

```python
def __init__(..., tls_insecure: bool = False) -> None:
    ...
    ctx.verify_mode = ssl.CERT_REQUIRED
    if tls_insecure:
        ctx.check_hostname = False
        logger.warning("MQTT_TLS_INSECURE ativo: …")
```

`config.py` lê `MQTT_TLS_INSECURE` (default falsy) e injecta em `run_simulator.py`.
Logo, o **default é seguro**; só com um env var explícito é que se reactiva o
comportamento antigo, e gera um warning em cada arranque.

**4.2 Ditto MQTT connection — `services/ditto/connectivity/mqtt-connection.json`:**
trocado `"validateCertificates": false` por `true` e introduzido placeholder
`"ca": "__CA_PEM__"`. Criei `services/ditto/connectivity/create-connection.sh`
que substitui o placeholder pelo conteúdo de `services/mosquitto/certs/ca.crt`
e aplica a conexão via devops API, lendo credenciais do `.env`. O README do
Ditto passou a apontar para este script.

**4.3 Certificados — `services/mosquitto/certs/generate-certs.sh`:**

Para a verificação de hostname passar é preciso SAN no cert do broker (Python
`ssl` ignora CN). Re-escrevi o script:

- `subjectAltName = DNS:mosquitto, DNS:localhost, IP:127.0.0.1` no `server.crt`
- 4096-bit em todas as chaves (era 2048 em algumas)
- `umask 077` no script + `chmod 600` nas chaves privadas
- Avisa quando um `server.crt` antigo (sem SAN) precisa de ser regenerado

Validações: tests do simulador 6/7 (1 skip esperado), `ruff` e `mypy` limpos, ambos
os shell scripts passam `bash -n`, JSON do Ditto válido.

---

## 5. Hash real do Genesis VC no UC3 (commit `adea289`)

**Item:** P1 · 4.9.

`uc3_device_registration.py:56` gravava a string literal
`"genesis-vc-hash-placeholder"` no ledger. Agora:

```python
def _genesis_vc_hash(credential: dict) -> str:
    canonical = json.dumps(credential, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

genesis_credential = {
    "type": "GenesisVC",
    "device_id": ..., "model_id": ..., "manufacturer_did": ...,
    "device_type": ..., "issued_at": datetime.now(UTC).isoformat(),
}
genesis_vc_hash = _genesis_vc_hash(genesis_credential)
```

O passo `genesis` da transação grava agora tanto o conteúdo da credencial
como o hash; o `manufacture_device` ancora o hash real. A emissão ACA-Py
real continua a ser item 3.4 (a integração Fabric/ACA-Py inteira ainda é o
client simulado).

24 testes egw-controller passam, `ruff` e `mypy` limpos.

---

## 6. Robustez do didcomm-agent (commit `f34c4a8`)

**Item:** P1 · 4.5.

Três frentes:

**6.1 Parsing JSON seguro** — `message.py`:

Antes:
```python
data = json.loads(raw)
return cls(id=data["id"], ...)  # KeyError no caminho infeliz
```

Agora, helpers partilhados:
```python
def _decode_json(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.warning(...)
        raise InvalidMessageError("malformed-json") from exc
    if not isinstance(data, dict):
        raise InvalidMessageError("not-a-json-object")
    return data

def _require(data, *keys): ...  # missing-fields:<csv>
```

Cobre tanto `DIDCommMessage.from_json` como `EncryptedDIDCommMessage.from_json`.

**6.2 Exception handlers na API** — `api.py`:

Três handlers registados (todos com `from fastapi.responses import JSONResponse`):
- `InvalidMessageError` → 400 com `{"detail": "<reason>"}` (sem stack trace)
- `UnknownPeerError` → 404 `{"detail": "unknown-peer"}`
- `MessageTamperingError` → 400 `{"detail": "message-tampering"}`

**6.3 Loggers em falta** — `crypto.py`, `storage.py`:

- `crypto.py`: `logger.debug` em `generate_keypair`
- `storage.py`: `logger.info` no `__init__` (com `db_path`), `upsert_agent`
  (com `agent_id`/`did`) e `upsert_peer` (com `did`/`agent_id`/`endpoint`)

**6.4 Nova excepção** — `exceptions.py` ganhou
`InvalidMessageError(ValueError)` com atributo `reason`. Re-exportada via
`__init__.py`.

**Testes:** `services/didcomm-agent/tests/test_message_parsing.py` cobre o
roundtrip e os 3 modos de falha (`malformed-json`, `not-a-json-object`,
`missing-fields:`). O sandbox não consegue importar `cryptography` (problema do
pyo3 com Python 3.11 vs 3.12), mas a lógica de parsing foi validada em
standalone (carregando o módulo `message.py` sem passar pelo `__init__.py` do
pacote). Os testes vão correr no CI com Python 3.12.

---

## 7. Erros ignorados nos chaincodes Go (commit `2c4db75`)

**Item:** P1 · 4.6.

Substituí os ~15 `_ := …` por verificação real:

**`dataset_tracking.go`:**
- `RegisterDataset`: `fmt.Sscanf("%d", &sizeBytes)` e idem `recordCount`
  aceitavam input não-numérico silenciosamente e gravavam zeros. Substituídos
  por `strconv.ParseInt(args[4], 10, 64)` e `strconv.Atoi(args[5])` com retorno
  de erro ao caller. **Este era o bug que motivou o item.**
- `CreateCompositeKey`, `json.Marshal`, `SetEvent` (3 callsites) e o
  `json.Unmarshal` em `TransferDatasetOwnership` propagam erros. O código
  antigo sobrescrevia o owner de um dataset mesmo se os bytes em estado
  estivessem corrompidos.

**`device_lifecycle.go`:**
- `RegisterDeviceModel`, `ManufactureDevice`, `DecommissionDevice`,
  `transition()` e `richQuery()`: todos os erros de `CreateCompositeKey`,
  `json.Marshal`, `PutState` e `SetEvent` agora propagam.
- O `DecommissionDevice` ignorava até o erro do `PutState`.

`go vet` clean em ambos os módulos; `gosec` corre por cima no CI.

Testes Go para os chaincodes continuam por escrever — segue como follow-up no
plano (4.6 segunda metade).

---

## 8. Metadados (commit `77161c5`)

**Item:** P2 · 5.8.

| Mudança | Ficheiro | Antes → Depois |
|---|---|---|
| Caminho do paper na árvore do repo | `README.md` | `EdgeGateway_Paper.pdf` (raiz) → `uni/paper/EdgeGateway_Paper.pdf` |
| `requires-python` | `services/didcomm-agent/pyproject.toml`, `services/smart-device-simulator/pyproject.toml` | `>=3.11` → `>=3.12` (alinhado com CI e README) |
| Header SPDX | `scripts/setup-env.sh` | `Apache-2.0` → `MIT` (repo é MIT) |
| Credenciais documentadas | `services/ditto/README.md` | Linha "Credenciais dev (ditto/c2dta)" e tabela com `c2dta`/`c2dta-devops` → tabela aponta para `.env` e `generate-htpasswd.sh` |
| Defaults inseguros documentados | `services/egw-controller/README.md` | `DITTO_USER=ditto`/`DITTO_PASS=c2dta` → `_(sem default)_, obrigatorio` + nota sobre falha cedo |
| Data "futura" | `services/aca-py/README.md` | `2026-03-19` → `2026-06-11` |

---

## 9. Untrack do `.egg-info` (commit `e830761`)

**Item:** P2 · 5.7 (parte higiene).

Os 5 ficheiros em `services/didcomm-agent/src/didcomm_agent.egg-info/` já
estavam no `.gitignore` (`*.egg-info/`, linha 14) mas tinham sido commitados
antes da regra. `git rm --cached` mantém-nos no disco e fora do índice.

---

## CI

A entrada na sessão tinha o CI a verde no `fe192d2` (run #23). A todos estes
commits foi feito push em conjunto; estou a observar o run subsequente e
emendo qualquer regressão que apareça (o monitor está armado e dispara
automaticamente quando o run termina).

Falhas anteriores nesta branch (runs #21 e #22) — diagnosticadas e
fechadas — estão documentadas nos commits `aa4a30c` e `fe192d2`.

---

## Decisões deixadas para o utilizador

Continuam pendentes — não foram tocadas porque exigem decisão tua, como
referido no `repo-improvement-plan.md` secção 7:

1. Purgar credenciais do histórico Git (`git filter-repo`) — destrutivo.
2. Códigos HTTP de erro nos use cases (item 4.1) — muda contrato da API.
3. Regex/limites exatos para validação de input (item 4.2).
4. Ferramenta de lockfile: `uv` vs `pip-tools` (item 4.8).
5. Eliminar compose standalone a favor de Compose profiles (item 5.6).
6. Split do `uni/` para repo próprio (item 5.7 segunda metade).

E a integração real Fabric (item 3.4, médio prazo) — o `FabricClient`
continua a ser uma simulação que devolve `{"status": "ok"}`. Os hashes que
agora ancoramos no UC3 são reais, mas só ficam no ledger simulado até
fazermos a integração Fabric Gateway/SDK.
