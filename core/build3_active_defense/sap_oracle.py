"""
sap_oracle.py – LUMINARK Cryptographic Yield Oracle
Axiom Yield Broker / Smart Contract Integration Layer

Signs Trap Score outputs with HMAC-SHA256 so they can be consumed by
automated ledgers (smart contracts, escrow systems, insurance APIs) as
a cryptographically verifiable commitment.

The oracle does NOT deploy to a blockchain — it produces signed JSON that
any EVM-compatible contract or off-chain verifier can validate using the
shared secret or public key.

DESIGN:
  - Sign the full output dict (system_id + stage + trap_score + timestamp)
  - Produce a hex digest: HMAC-SHA256(secret_key, canonical_json)
  - Also produce an ABI-encoded payload matching Solidity bytes32 convention
  - Include a Solidity interface stub for contract integration

AXIOM YIELD BROKER USE CASES:
  - Freight insurance: carrier's Trap Score signed every N minutes
  - Escrow release: Stage ≤ 4 with Trap < 25 → auto-release
  - Risk reallocation: Stage 7+ → automatic hold + premium spike
  - Route volatility: Tension spike → renegotiate carrier rate in real time

SECURITY NOTE:
  The secret_key should be rotated per-carrier per-session and stored in
  a hardware security module (HSM) or KMS in production. Do not hardcode.
"""

import hashlib
import hmac
import json
import time
import struct
from typing import Dict, Optional, Any


# ── Canonical serialization ───────────────────────────────────────────────────

def _canonical_json(data: Dict[str, Any]) -> bytes:
    """
    Produce deterministic JSON bytes for signing.
    Keys sorted, no whitespace, UTF-8 encoded.
    """
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")


# ── Oracle ────────────────────────────────────────────────────────────────────

class SAPOracle:
    """
    Cryptographic signing oracle for LUMINARK Trap Score outputs.

    Parameters
    ----------
    secret_key : bytes — shared secret for HMAC-SHA256
                         In production: load from KMS/HSM, never hardcode
    oracle_id  : str  — identifies this oracle instance (e.g. "AYB-ORACLE-01")
    """

    def __init__(self, secret_key: bytes, oracle_id: str = "LUMINARK-ORACLE"):
        if len(secret_key) < 16:
            raise ValueError("secret_key must be at least 16 bytes")
        self._key = secret_key
        self.oracle_id = oracle_id

    def sign(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign an engine output dict. Returns the original payload plus
        oracle metadata and HMAC signature.

        Parameters
        ----------
        payload : dict — must contain at minimum:
                    system_id, stage, trap_normalized, timestamp

        Returns
        -------
        dict with added keys:
            oracle_id    : str
            oracle_ts    : float (unix timestamp of signing)
            signature    : str  (hex HMAC-SHA256)
            abi_encoded  : str  (hex, bytes32-compatible for Solidity)
            contract_hint: dict (how a smart contract should consume this)
        """
        oracle_ts = time.time()
        signing_payload = {
            "oracle_id":       self.oracle_id,
            "oracle_ts":       oracle_ts,
            "system_id":       payload.get("system_id", ""),
            "stage":           payload.get("stage", -1),
            "trap_normalized": payload.get("trap_normalized", 0.0),
            "risk_level":      payload.get("risk_level", "UNKNOWN"),
            "timestamp":       payload.get("timestamp", ""),
        }

        canonical = _canonical_json(signing_payload)
        sig = hmac.new(self._key, canonical, hashlib.sha256).hexdigest()

        # ABI-encode trap_normalized as uint16 scaled ×100 (matches Solidity uint16)
        # and stage as uint8 — fits in 3 bytes, padded to bytes32
        trap_int = min(9999, int(payload.get("trap_normalized", 0.0) * 100))
        stage_int = int(payload.get("stage", 0)) & 0xFF
        # Pack: [stage_u8][trap_u16_big_endian][zeros×29]
        raw = struct.pack(">BH", stage_int, trap_int) + b"\x00" * 29
        abi_encoded = raw.hex()

        # Determine contract action hint
        trap = payload.get("trap_normalized", 0.0)
        stage = payload.get("stage", 0)
        if stage <= 4 and trap < 25.0:
            contract_action = "RELEASE_ESCROW"
            fee_multiplier  = 1.0
        elif stage >= 7 or trap >= 75.0:
            contract_action = "HOLD_AND_REALLOCATE"
            fee_multiplier  = 3.5
        elif stage >= 5 or trap >= 50.0:
            contract_action = "INCREASE_PREMIUM"
            fee_multiplier  = 1.8
        else:
            contract_action = "STANDARD_TERMS"
            fee_multiplier  = 1.2

        return {
            **payload,
            "oracle_id":      self.oracle_id,
            "oracle_ts":      oracle_ts,
            "signature":      sig,
            "abi_encoded":    abi_encoded,
            "contract_hint": {
                "action":         contract_action,
                "fee_multiplier": fee_multiplier,
                "stage":          stage_int,
                "trap_scaled":    trap_int,
            },
        }

    def verify(self, signed_payload: Dict[str, Any]) -> bool:
        """
        Verify a previously signed payload. Returns True if signature is valid.

        Parameters
        ----------
        signed_payload : dict — output of sign(), including "signature" key

        Returns
        -------
        bool — True if HMAC matches, False otherwise
        """
        provided_sig = signed_payload.get("signature", "")
        reconstructed = {
            "oracle_id":       signed_payload.get("oracle_id", ""),
            "oracle_ts":       signed_payload.get("oracle_ts", 0.0),
            "system_id":       signed_payload.get("system_id", ""),
            "stage":           signed_payload.get("stage", -1),
            "trap_normalized": signed_payload.get("trap_normalized", 0.0),
            "risk_level":      signed_payload.get("risk_level", "UNKNOWN"),
            "timestamp":       signed_payload.get("timestamp", ""),
        }
        canonical = _canonical_json(reconstructed)
        expected_sig = hmac.new(self._key, canonical, hashlib.sha256).hexdigest()
        return hmac.compare_digest(provided_sig, expected_sig)


# ── Solidity interface stub ───────────────────────────────────────────────────

SOLIDITY_INTERFACE = '''
// SPDX-License-Identifier: MIT
// ILuminarkOracle.sol – Interface for consuming LUMINARK signed oracle data
// Deploy an oracle adapter that calls verifyAndAct() with the signed payload.

pragma solidity ^0.8.20;

interface ILuminarkOracle {
    /// @notice Emitted when a LUMINARK oracle report is processed
    event OracleReport(
        bytes32 indexed systemId,
        uint8   stage,
        uint16  trapScaled,      // trap_normalized * 100, range [0, 10000]
        bytes32 signature,       // first 32 bytes of HMAC-SHA256 (off-chain verified)
        uint8   contractAction   // 0=STANDARD, 1=RELEASE_ESCROW, 2=INCREASE_PREMIUM, 3=HOLD
    );

    /// @notice Process a LUMINARK oracle report
    /// @param abiEncoded  The bytes32 from oracle.sign()["abi_encoded"]
    /// @param systemId    The carrier/system identifier
    function processOracleReport(
        bytes32 abiEncoded,
        bytes32 systemId
    ) external;

    /// @notice Get current fee multiplier for a system (scaled x100)
    function getFeeMultiplier(bytes32 systemId) external view returns (uint16);

    /// @notice Check if escrow is releasable for a system
    function isEscrowReleasable(bytes32 systemId) external view returns (bool);
}

/*
 * IMPLEMENTATION NOTES:
 *
 * 1. Deploy an oracle relayer (off-chain) that:
 *    a. Receives signed payloads from SAPOracle.sign()
 *    b. Verifies HMAC using SAPOracle.verify()
 *    c. Calls processOracleReport() on-chain with the ABI-encoded bytes32
 *
 * 2. The bytes32 abiEncoded layout:
 *    byte 0   : stage (uint8, 0-9)
 *    bytes 1-2: trapScaled (uint16 big-endian, trap_normalized * 100)
 *    bytes 3-31: zeros (reserved for future fields)
 *
 * 3. Decode in Solidity:
 *    uint8  stage      = uint8(abiEncoded[0]);
 *    uint16 trapScaled = (uint16(uint8(abiEncoded[1])) << 8)
 *                      | uint16(uint8(abiEncoded[2]));
 *
 * 4. Contract actions by stage/trap:
 *    stage <= 4 AND trap < 2500  → RELEASE_ESCROW
 *    stage >= 7 OR  trap >= 7500 → HOLD_AND_REALLOCATE
 *    stage >= 5 OR  trap >= 5000 → INCREASE_PREMIUM
 *    else                        → STANDARD_TERMS
 */
'''


def write_solidity_interface(path: str = "ILuminarkOracle.sol") -> None:
    """Write the Solidity interface to a file."""
    with open(path, "w") as f:
        f.write(SOLIDITY_INTERFACE)
    print(f"Solidity interface written to {path}")


# ── Self-test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    key = os.urandom(32)
    oracle = SAPOracle(key, oracle_id="AYB-TEST-ORACLE")

    payload = {
        "system_id":       "carrier-TX-441",
        "stage":           4,
        "trap_normalized": 18.5,
        "risk_level":      "LOW",
        "timestamp":       "2026-04-14T12:00:00",
    }

    signed = oracle.sign(payload)
    verified = oracle.verify(signed)

    print("Oracle self-test")
    print(f"  Signature    : {signed['signature'][:32]}...")
    print(f"  ABI encoded  : 0x{signed['abi_encoded'][:12]}...")
    print(f"  Contract hint: {signed['contract_hint']['action']}")
    print(f"  Fee multiplier: {signed['contract_hint']['fee_multiplier']}x")
    print(f"  Verified     : {'✅' if verified else '❌'}")

    # Tamper test
    tampered = dict(signed)
    tampered["trap_normalized"] = 99.0
    print(f"  Tamper check : {'✅ rejected' if not oracle.verify(tampered) else '❌ accepted (bug!)'}")
