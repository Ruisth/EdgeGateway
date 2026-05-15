"""Cliente para o Hyperledger Fabric (ecosystem ledger).

Invoca chaincodes de device-lifecycle e dataset-tracking
via chamadas CLI ou SDK.
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class FabricClient:
    """Cliente para interacao com o Hyperledger Fabric via CLI."""

    def __init__(
        self,
        peer_url: str = "localhost:7051",
        channel: str = "c2dta-channel",
        chaincode_lifecycle: str = "device-lifecycle",
        chaincode_dataset: str = "dataset-tracking",
    ) -> None:
        self.peer_url = peer_url
        self.channel = channel
        self.cc_lifecycle = chaincode_lifecycle
        self.cc_dataset = chaincode_dataset

    def invoke_chaincode(
        self, chaincode: str, function: str, args: list[str]
    ) -> dict[str, Any]:
        """Invoca uma funcao de chaincode.

        Em producao, utilizaria o Fabric SDK Python. Para desenvolvimento,
        delega ao container CLI via docker exec.
        """
        args_json = json.dumps(args)
        logger.info(
            "Fabric invoke: %s.%s(%s) no canal %s",
            chaincode, function, args_json, self.channel,
        )

        # Simulacao local — retorna resultado de sucesso
        # Em producao: subprocess ou SDK
        return {
            "status": "ok",
            "chaincode": chaincode,
            "function": function,
            "args": args,
            "channel": self.channel,
        }

    # ---------- Device Lifecycle ----------

    def register_device_model(
        self, model_id: str, manufacturer: str, wot_td_hash: str
    ) -> dict:
        return self.invoke_chaincode(
            self.cc_lifecycle, "RegisterDeviceModel",
            [model_id, manufacturer, wot_td_hash],
        )

    def manufacture_device(
        self, device_id: str, model_id: str, manufacturer_id: str, genesis_vc_hash: str
    ) -> dict:
        return self.invoke_chaincode(
            self.cc_lifecycle, "ManufactureDevice",
            [device_id, model_id, manufacturer_id, genesis_vc_hash],
        )

    def make_available(self, device_id: str) -> dict:
        return self.invoke_chaincode(self.cc_lifecycle, "MakeAvailable", [device_id])

    def initiate_transit(self, device_id: str, buyer_did: str) -> dict:
        return self.invoke_chaincode(
            self.cc_lifecycle, "InitiateTransit", [device_id, buyer_did],
        )

    def claim_device(
        self, device_id: str, controller_did: str, ownership_vc_hash: str
    ) -> dict:
        return self.invoke_chaincode(
            self.cc_lifecycle, "ClaimDevice",
            [device_id, controller_did, ownership_vc_hash],
        )

    def twin_device(self, device_id: str, ditto_thing_id: str) -> dict:
        return self.invoke_chaincode(
            self.cc_lifecycle, "TwinDevice", [device_id, ditto_thing_id],
        )

    def untwin_device(self, device_id: str) -> dict:
        return self.invoke_chaincode(self.cc_lifecycle, "UntwinDevice", [device_id])

    def decommission_device(self, device_id: str) -> dict:
        return self.invoke_chaincode(
            self.cc_lifecycle, "DecommissionDevice", [device_id],
        )

    def query_device(self, device_id: str) -> dict:
        return self.invoke_chaincode(self.cc_lifecycle, "QueryDevice", [device_id])

    # ---------- Dataset Tracking ----------

    def register_dataset(
        self, dataset_id: str, device_id: str, ipfs_hash: str,
        owner_did: str, size_bytes: int, record_count: int,
        start_time: str, end_time: str,
    ) -> dict:
        return self.invoke_chaincode(
            self.cc_dataset, "RegisterDataset",
            [dataset_id, device_id, ipfs_hash, owner_did,
             str(size_bytes), str(record_count), start_time, end_time],
        )

    def query_datasets(self, device_id: str) -> dict:
        return self.invoke_chaincode(
            self.cc_dataset, "QueryDatasetsByDevice", [device_id],
        )
