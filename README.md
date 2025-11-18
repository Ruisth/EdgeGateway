# Edge Gateway for Personal AI based on Blockchain

Knowledge base and code for the Edge Gateway described in `EdgeGateway_Paper.pdf`. The goal is to connect local sensors, embedded AI pipelines and a blockchain-protected Digital Twin while preserving data sovereignty, low-latency inference and auditable governance.

## Quick overview
- **Primary stack**: Yocto Project + OCI containers, embedded AI pipelines and blockchain/DIDComm agents.
- **Documentation**: architectural models in `docs/`, a summary of the paper and milestone plans.
- **Services**: DIDComm agent prototype in `services/didcomm-agent/`.
- **Infrastructure**: scripts and VS Code tasks to prepare the build environment.

## Getting started
1. **Clone and open in VS Code** – suggested extensions are in `.vscode/extensions.json`.
2. **Add Yocto/BSP submodules**
   ```bash
   git submodule add git://git.yoctoproject.org/poky yocto/poky
   git submodule update --init --recursive
   ```
3. **Initialise the environment** – run `source scripts/setup-env.sh` (or the `setup environment` VS Code task).
4. **Build the reference image** – run `bitbake edgegateway-image` inside the environment.
5. **Document decisions** – keep the files in `docs/` updated as architectural and hardware choices evolve.

## Repository structure
```text
.vscode/                     Task definitions, linting and recommended extensions
docs/                        Architecture foundations, research and roadmap
  architecture/              System architecture, flows and DIDComm
  paper/                     Navigable summary of EdgeGateway_Paper.pdf
  research/                  Complementary studies on personal AI and blockchain
  roadmaps/                  Technical milestones and initial backlog
scripts/                     Utility scripts (e.g. setup-env.sh)
services/
  didcomm-agent/             FastAPI service + tests for the DIDComm agent
yocto/
  README.md                  Quick guide to layers and recipes
  layers/meta-edgegateway/   edgegateway-image recipe and space for containers
EdgeGateway_Paper.pdf        Complete project reference
LICENSE                      MIT licence
```

## Recommended documentation
| Topic | Where to start | Why it matters |
| --- | --- | --- |
| System architecture | `docs/architecture/system-architecture.md` | 360° view of the gateway modules |
| Dataflow and communication | `docs/architecture/communication-and-dataflow.md` | QoS rules, protocols and operational requirements |
| DIDComm subsystem | `docs/architecture/didcomm-architecture.md` + `services/didcomm-agent/README.md` | Guide for the secure messaging MVP |
| Paper summary | `docs/paper/edgegateway-paper-summary.md` | Quick index of the original PDF |
| Roadmap | `docs/roadmaps/milestone-plan.md` | Sequencing of project phases |

## Yocto guide in 5 minutes
1. Ensure `yocto/poky` and BSP layers are present.
2. Use the `scripts/setup-env.sh` script to export BitBake variables.
3. Ensure `yocto/layers/meta-edgegateway/conf/layer.conf` is enabled in `bblayers.conf`.
4. Adjust `yocto/layers/meta-edgegateway/recipes-core/images/edgegateway-image.bb` by adding packages (containers, MQTT, blockchain agents, AI tools and observability).
5. Add specific recipes in `recipes-containers/` and `recipes-security/` to reflect the paper requirements.

Further details are in `yocto/README.md` and should be expanded as customisations grow.

## DIDComm service
- Code and tests in `services/didcomm-agent/`.
- Stack: FastAPI + libsodium (X25519 + ChaCha20-Poly1305), with example scripts (`examples/demo_exchange.py`).
- Run `python -m pytest` for local tests and `docker compose up --build` for the containerised API.
- The conceptual architecture aligns with `docs/architecture/didcomm-architecture.md`.

## Roadmap and next steps
1. **Phase 0** – define target hardware, BSPs and security/compliance requirements.
2. **Phase 1** – stabilise the `meta-edgegateway` layer, MQTT broker and blockchain agents.
3. **Phase 2** – observability, data governance and OTA automation.
4. **Phase 3** – pilots with real devices and audit readiness.

Update `docs/roadmaps/milestone-plan.md` and the diagrams in `docs/architecture/` as new decisions are made (hardware, AI models, smart contracts, etc.).

## Licence
Distributed under the MIT licence – see `LICENSE` for details.
