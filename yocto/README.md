# Yocto guide for the Edge Gateway

Translates the requirements from `EdgeGateway_Paper.pdf` into concrete actions for customising the Yocto image.

## Structure
```text
yocto/
  README.md
  layers/
    meta-edgegateway/
      conf/layer.conf
      recipes-core/images/edgegateway-image.bb
      recipes-containers/ (placeholders)
  poky/  # add as a submodule
```

## Prerequisites
- Linux host (or WSL2) with: git, python3, tar, gcc, chrpath, cpio, gawk, make, xz, unzip, Locale en_US.UTF-8.
- Disk space: ≥ 50 GB; RAM: ≥ 16 GB (recommended).
- `TEMPLATECONF` variable pointing to `meta-edgegateway/conf` when initialising the environment.

## Initial steps
1. Add Poky and BSP layers for the target hardware.
2. `source ../scripts/setup-env.sh` (exports `TEMPLATECONF`, `BBPATH`, etc.).
3. Update `bblayers.conf` to include `meta-edgegateway` and BSPs.
4. Run `bitbake edgegateway-image`.

## Recommended content for `edgegateway-image`
- Container support (Docker/Podman) and OCI runtime (crun/runc).
- MQTT broker (Eclipse Mosquitto) + persistent queue (RabbitMQ/NATS JetStream).
- AI tools (TensorFlow Lite, ONNX Runtime) and accelerator drivers.
- Blockchain agents, DIDComm and cryptography libraries (libsodium, openssl).
- Observability stack (Prometheus Node Exporter, Fluent Bit, Grafana Agent).
- OTA tools (swupdate or Mender) and rollback scripts.

## Useful variables
| Variable | Purpose |
| --- | --- |
| `MACHINE` | Defines the target hardware/BSP. |
| `DISTRO` | Distribution base (e.g. `poky`, `edgegateway`). |
| `BB_ENV_EXTRAWHITE` | Allows custom variables to be passed to BitBake. |
| `SSTATE_DIR` and `DL_DIR` | Shared directories to speed up builds. |

## Recommended practices
- Version `conf/notebook/*.conf` (TEMPLATECONF) to ensure reproducible builds.
- Use `devtool` to iterate on local recipes before promoting them to `meta-edgegateway`.
- Document new recipes/overlays in `docs/architecture/` and create pTest tests when applicable.

## Next evolutions
- Add recipes for smart contracts/CLIs.
- Integrate automated tests (pTest) covering drivers, inference and blockchain synchronisation.
- Create auxiliary layers (`meta-edgegateway-security`, `meta-edgegateway-observability`) as the base grows.

> Last reviewed: 2025-11-18
