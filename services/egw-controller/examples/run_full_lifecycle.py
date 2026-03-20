#!/usr/bin/env python3
"""Demo completa do ciclo de vida UC1-UC8.

Executa sequencialmente todos os use cases contra a API do EGW Controller,
demonstrando o fluxo completo descrito no paper C2DTA.

Uso:
    python run_full_lifecycle.py [--base-url http://localhost:8090]
"""

from __future__ import annotations

import argparse
import json
import sys
import time

import httpx

DEFAULT_BASE_URL = "http://localhost:8090"


def call_uc(client: httpx.Client, endpoint: str, payload: dict, label: str) -> dict:
    """Chama um endpoint de use case e apresenta o resultado."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"POST {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    resp = client.post(endpoint, json=payload)
    data = resp.json()

    status = "OK" if data.get("success") else "FALHOU"
    print(f"Resultado: [{status}] {data.get('message', '')}")
    if data.get("data"):
        print(f"Dados: {json.dumps(data['data'], indent=2)}")

    if not data.get("success"):
        print(f"AVISO: {label} falhou — {data.get('message')}")

    return data


def main():
    parser = argparse.ArgumentParser(description="Demo ciclo de vida C2DTA UC1-UC8")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()

    print(f"EGW Controller: {args.base_url}")
    print("A iniciar demo do ciclo de vida completo...\n")

    with httpx.Client(base_url=args.base_url, timeout=30) as client:
        # Health check
        resp = client.get("/health")
        if resp.status_code != 200:
            print("ERRO: EGW Controller nao esta acessivel")
            sys.exit(1)
        print(f"Health: {resp.json()}")

        # UC1 — OEM Enrollment
        call_uc(client, "/uc/enrollment", {
            "organization_name": "SmartWatch Corp",
            "organization_did": "did:sov:oem-smartwatch-001",
        }, "UC1 — OEM Enrollment")

        # UC2 — Model Registration
        call_uc(client, "/uc/register-model", {
            "model_id": "smartwatch-v1",
            "manufacturer": "SmartWatch Corp",
            "wot_td_hash": "sha256:td-smartwatch-v1",
        }, "UC2 — Model Registration")

        # UC3 — Device Self-Registration
        device_id = "sd-demo-001"
        call_uc(client, "/uc/register-device", {
            "device_id": device_id,
            "model_id": "smartwatch-v1",
            "device_type": "SmartDevice",
            "manufacturer_did": "did:sov:oem-smartwatch-001",
        }, "UC3 — Device Self-Registration")

        # UC4 — Consumer Buys Device
        buyer_did = "did:sov:consumer-alice"
        call_uc(client, "/uc/purchase", {
            "device_id": device_id,
            "buyer_did": buyer_did,
        }, "UC4 — Consumer Buys Device")

        # UC5 — Device Claiming
        call_uc(client, "/uc/claim", {
            "device_id": device_id,
            "controller_did": buyer_did,
            "ownership_vc_hash": "sha256:ownership-alice-001",
        }, "UC5 — Device Claiming")

        # UC6 — SD Twinning
        call_uc(client, "/uc/twin", {
            "device_id": device_id,
        }, "UC6 — SD Twinning")

        # UC7 — SD Untwinning
        call_uc(client, "/uc/untwin", {
            "device_id": device_id,
        }, "UC7 — SD Untwinning")

        # UC8 — SD Selling
        call_uc(client, "/uc/sell", {
            "device_id": device_id,
            "buyer_did": "did:sov:consumer-bob",
        }, "UC8 — SD Selling")

        # Listar transacoes
        print(f"\n{'='*60}")
        print("  Transacoes registadas")
        print(f"{'='*60}")
        resp = client.get("/transactions")
        txs = resp.json()
        for tx in txs:
            print(f"  [{tx['status']}] {tx['use_case']} — {tx['transaction_id'][:8]}...")

    print(f"\nDemo concluida — {len(txs)} transacoes executadas.")


if __name__ == "__main__":
    main()
