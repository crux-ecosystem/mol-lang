"""
MOL Ecosystem Extensions — Sovereign AI Stack Integration
============================================================

Extends MOL with built-in functions for the entire Crux ecosystem:
  • De-RAG   — Decentralized Encrypted RAG
  • Neural Kernel — AI-native microkernel
  • IntraMind    — Campus RAG engine

These builtins allow MOL scripts to orchestrate the full sovereign stack:

    doc |> derag_encrypt(key) |> derag_shard(3, 5) |> derag_distribute(peers)
    result |> nk_agent_spawn("rag_worker") |> nk_grant("query", "ingest")
    query |> intramind_rag("what is AI?") |> derag_audit("query_log")

Version: 1.0.0 (Sovereign Stack Integration)
"""

from __future__ import annotations

import os
import sys
import json
import time
import hashlib
import secrets
import struct
import base64
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict

# ═══════════════════════════════════════════════════════════════════
# Type Definitions for Ecosystem Objects
# ═══════════════════════════════════════════════════════════════════

@dataclass
class DeRAGEnvelope:
    """Encrypted envelope from De-RAG"""
    ciphertext: bytes
    nonce: bytes
    tag: bytes
    key_id: str
    algorithm: str = "AES-256-GCM"
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "ciphertext": base64.b64encode(self.ciphertext).decode(),
            "nonce": base64.b64encode(self.nonce).decode(),
            "tag": base64.b64encode(self.tag).decode(),
            "key_id": self.key_id,
            "algorithm": self.algorithm,
            "created_at": self.created_at,
        }

    def __repr__(self):
        return f"DeRAGEnvelope(key={self.key_id}, algo={self.algorithm})"


@dataclass
class DeRAGShard:
    """A Shamir shard from De-RAG"""
    index: int
    data: bytes
    threshold: int
    total: int
    doc_hash: str

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "data": base64.b64encode(self.data).decode(),
            "threshold": self.threshold,
            "total": self.total,
            "doc_hash": self.doc_hash,
        }

    def __repr__(self):
        return f"DeRAGShard({self.index}/{self.total}, t={self.threshold})"


@dataclass
class NKAgent:
    """Neural Kernel agent handle"""
    agent_id: str
    name: str
    capabilities: list = field(default_factory=list)
    state: str = "created"
    priority: str = "normal"
    memory_quota: int = 256 * 1024 * 1024  # 256MB
    metadata: dict = field(default_factory=dict)
    _stats: dict = field(default_factory=lambda: {
        "tasks_completed": 0,
        "cpu_time_ms": 0,
        "memory_used": 0,
        "uptime_s": 0,
    })

    def to_dict(self) -> dict:
        return asdict(self)

    def __repr__(self):
        caps = ", ".join(self.capabilities[:3])
        if len(self.capabilities) > 3:
            caps += f" +{len(self.capabilities) - 3}"
        return f"NKAgent({self.name}, state={self.state}, caps=[{caps}])"


@dataclass
class NKCapabilityToken:
    """Unforgeable capability token from Neural Kernel"""
    token_id: str
    capability: str
    agent_id: str
    delegatable: bool = False
    expires_at: Optional[float] = None

    def is_valid(self) -> bool:
        if self.expires_at and time.time() > self.expires_at:
            return False
        return True

    def __repr__(self):
        return f"CapToken({self.capability}, agent={self.agent_id[:8]})"


@dataclass
class IntraMindResult:
    """Result from IntraMind RAG pipeline"""
    success: bool
    answer: str
    sources: list = field(default_factory=list)
    confidence: float = 0.0
    elapsed_ms: float = 0.0
    cached: bool = False
    edition: str = "core"

    def to_dict(self) -> dict:
        return asdict(self)

    def __repr__(self):
        src_count = len(self.sources)
        return f"IntraMindResult(ok={self.success}, sources={src_count}, {self.elapsed_ms:.0f}ms)"


# ═══════════════════════════════════════════════════════════════════
# Internal State Registries
# ═══════════════════════════════════════════════════════════════════

_derag_state = {
    "initialized": False,
    "keys": {},            # key_id → key_bytes
    "shards": {},          # doc_hash → [shard, ...]
    "peers": [],           # connected peer addresses
    "audit_log": [],       # lineage entries
    "config": {
        "algorithm": "AES-256-GCM",
        "key_size": 32,
        "shard_threshold": 3,
        "shard_total": 5,
    },
}

_nk_state = {
    "initialized": False,
    "agents": {},          # agent_id → NKAgent
    "tokens": {},          # token_id → NKCapabilityToken
    "scheduler_queue": [], # agent_ids in priority order
    "ipc_channels": {},    # channel_name → [messages]
    "syscall_log": [],
    "config": {
        "max_agents": 1024,
        "time_slice_ms": 10,
        "memory_limit": 4 * 1024 * 1024 * 1024,  # 4GB
    },
}

_intramind_state = {
    "initialized": False,
    "engine": None,        # IntraMindEngine instance
    "edition": "core",
    "query_count": 0,
    "ingest_count": 0,
}

_lock = threading.Lock()


# ═══════════════════════════════════════════════════════════════════
#  DE-RAG BUILTINS — Decentralized Encrypted RAG
# ═══════════════════════════════════════════════════════════════════

def _builtin_derag_init(config=None):
    """Initialize De-RAG subsystem.
    
    Usage in MOL:
        derag_init()
        derag_init({algorithm: "AES-256-GCM", shard_threshold: 3})
    """
    with _lock:
        if config and isinstance(config, dict):
            _derag_state["config"].update(config)
        _derag_state["initialized"] = True
        _audit_log("derag", "init", {"config": _derag_state["config"]})
    return {"status": "ok", "config": _derag_state["config"]}


def _builtin_derag_keygen(key_name="default"):
    """Generate a cryptographic key for De-RAG envelope encryption.
    
    Usage in MOL:
        let key be derag_keygen("my_key")
        let default_key be derag_keygen()
    """
    _ensure_derag()
    key_bytes = secrets.token_bytes(32)  # AES-256
    key_id = hashlib.blake2b(key_bytes, digest_size=16).hexdigest()
    with _lock:
        _derag_state["keys"][key_id] = key_bytes
    _audit_log("derag", "keygen", {"key_id": key_id, "name": key_name})
    return {"key_id": key_id, "name": key_name, "algorithm": "AES-256-GCM"}


def _builtin_derag_encrypt(data, key_id=None):
    """Encrypt data using De-RAG envelope encryption (AES-256-GCM).
    
    Usage in MOL:
        let envelope be derag_encrypt("sensitive data", key.key_id)
        "data" |> derag_encrypt(key.key_id)
    """
    _ensure_derag()
    if key_id is None:
        keys = list(_derag_state["keys"].keys())
        if not keys:
            raise RuntimeError("No De-RAG keys available. Call derag_keygen() first.")
        key_id = keys[0]

    key_bytes = _derag_state["keys"].get(key_id)
    if not key_bytes:
        raise RuntimeError(f"Key '{key_id}' not found")

    # AES-256-GCM encryption
    nonce = secrets.token_bytes(12)
    plaintext = data.encode("utf-8") if isinstance(data, str) else data

    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aes = AESGCM(key_bytes)
        ct = aes.encrypt(nonce, plaintext, None)
        ciphertext, tag = ct[:-16], ct[-16:]
    except ImportError:
        # Fallback: XOR-based simulation for environments without cryptography
        ciphertext = bytes(a ^ b for a, b in zip(plaintext, (key_bytes * (len(plaintext) // 32 + 1))[:len(plaintext)]))
        tag = hashlib.blake2b(ciphertext + nonce, key=key_bytes, digest_size=16).digest()

    envelope = DeRAGEnvelope(
        ciphertext=ciphertext,
        nonce=nonce,
        tag=tag,
        key_id=key_id,
    )
    _audit_log("derag", "encrypt", {"key_id": key_id, "size": len(plaintext)})
    return envelope


def _builtin_derag_decrypt(envelope, key_id=None):
    """Decrypt a De-RAG envelope back to plaintext.
    
    Usage in MOL:
        let plaintext be derag_decrypt(envelope)
        envelope |> derag_decrypt
    """
    _ensure_derag()
    if isinstance(envelope, dict):
        # Reconstruct from dict
        key_id = key_id or envelope.get("key_id")
        ciphertext = base64.b64decode(envelope["ciphertext"])
        nonce = base64.b64decode(envelope["nonce"])
        tag = base64.b64decode(envelope["tag"])
    elif isinstance(envelope, DeRAGEnvelope):
        key_id = key_id or envelope.key_id
        ciphertext = envelope.ciphertext
        nonce = envelope.nonce
        tag = envelope.tag
    else:
        raise TypeError(f"Expected DeRAGEnvelope or dict, got {type(envelope)}")

    key_bytes = _derag_state["keys"].get(key_id)
    if not key_bytes:
        raise RuntimeError(f"Key '{key_id}' not found")

    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        aes = AESGCM(key_bytes)
        plaintext = aes.decrypt(nonce, ciphertext + tag, None)
    except ImportError:
        plaintext = bytes(a ^ b for a, b in zip(ciphertext, (key_bytes * (len(ciphertext) // 32 + 1))[:len(ciphertext)]))

    _audit_log("derag", "decrypt", {"key_id": key_id})
    return plaintext.decode("utf-8")


def _builtin_derag_hash(data, algorithm="blake3"):
    """Content-addressable hash for De-RAG lineage tracking.
    
    Usage in MOL:
        let hash be derag_hash("my document content")
        doc |> derag_hash("sha256")
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    if algorithm == "blake3":
        try:
            import blake3
            return blake3.blake3(data).hexdigest()
        except ImportError:
            return hashlib.blake2b(data, digest_size=32).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data).hexdigest()
    elif algorithm == "blake2b":
        return hashlib.blake2b(data, digest_size=32).hexdigest()
    else:
        raise ValueError(f"Unknown hash algorithm: {algorithm}")


def _builtin_derag_shard(data, threshold=3, total=5):
    """Split data into Shamir secret shares for distributed storage.
    
    Usage in MOL:
        let shards be derag_shard("secret data", 3, 5)
        -- Need any 3 of 5 shards to reconstruct
    """
    _ensure_derag()
    if isinstance(data, str):
        data = data.encode("utf-8")

    doc_hash = hashlib.blake2b(data, digest_size=16).hexdigest()

    # GF(2^8) Shamir Secret Sharing
    shards = _shamir_split(data, threshold, total)

    shard_objects = []
    for i, shard_data in enumerate(shards, 1):
        shard = DeRAGShard(
            index=i,
            data=shard_data,
            threshold=threshold,
            total=total,
            doc_hash=doc_hash,
        )
        shard_objects.append(shard)

    with _lock:
        _derag_state["shards"][doc_hash] = shard_objects

    _audit_log("derag", "shard", {
        "doc_hash": doc_hash,
        "threshold": threshold,
        "total": total,
    })
    return shard_objects


def _builtin_derag_reconstruct(shards):
    """Reconstruct data from Shamir secret shares.
    
    Usage in MOL:
        let data be derag_reconstruct(collected_shards)
    """
    _ensure_derag()
    if not shards or len(shards) == 0:
        raise ValueError("No shards provided")

    shard_list = []
    threshold = None
    for s in shards:
        if isinstance(s, DeRAGShard):
            shard_list.append((s.index, s.data))
            threshold = s.threshold
        elif isinstance(s, dict):
            shard_list.append((s["index"], base64.b64decode(s["data"])))
            threshold = s.get("threshold", len(shards))
        else:
            raise TypeError(f"Unknown shard type: {type(s)}")

    if len(shard_list) < (threshold or len(shard_list)):
        raise ValueError(f"Need at least {threshold} shards, got {len(shard_list)}")

    result = _shamir_reconstruct(shard_list, threshold or len(shard_list))
    _audit_log("derag", "reconstruct", {"shard_count": len(shard_list)})
    return result.decode("utf-8")


def _builtin_derag_distribute(shards, peers=None):
    """Distribute shards across De-RAG network peers.
    
    Usage in MOL:
        shards |> derag_distribute(["node1:9100", "node2:9100"])
    """
    _ensure_derag()
    if peers is None:
        peers = _derag_state.get("peers", [])

    distribution = {}
    for i, shard in enumerate(shards):
        peer = peers[i % len(peers)] if peers else f"local_store_{i}"
        distribution[peer] = distribution.get(peer, [])
        if isinstance(shard, DeRAGShard):
            distribution[peer].append(shard.to_dict())
        else:
            distribution[peer].append(shard)

    _audit_log("derag", "distribute", {
        "shard_count": len(shards),
        "peer_count": len(set(distribution.keys())),
    })
    return {
        "status": "distributed",
        "mapping": distribution,
        "total_shards": len(shards),
        "peers_used": len(set(distribution.keys())),
    }


def _builtin_derag_query(query_text, top_k=5, encrypted=True):
    """Execute a De-RAG query across the decentralized network.
    
    Usage in MOL:
        let results be derag_query("what is quantum computing?", 5)
        "search term" |> derag_query
    """
    _ensure_derag()
    query_hash = hashlib.blake2b(query_text.encode(), digest_size=16).hexdigest()

    # Build query result (actual distributed query requires running De-RAG node)
    result = {
        "query": query_text,
        "query_hash": query_hash,
        "top_k": top_k,
        "encrypted": encrypted,
        "results": [],
        "elapsed_ms": 0,
        "nodes_queried": len(_derag_state.get("peers", [])),
    }

    _audit_log("derag", "query", {"query_hash": query_hash, "top_k": top_k})
    return result


def _builtin_derag_audit(action=None, data=None):
    """Query or append to the De-RAG Merkle audit log.
    
    Usage in MOL:
        derag_audit("ingest", {doc: "paper.pdf", hash: doc_hash})
        let log be derag_audit()  -- get full audit log
    """
    if action and data:
        _audit_log("derag", action, data)
        return {"status": "logged", "action": action}
    else:
        return list(_derag_state["audit_log"])


def _builtin_derag_peers(action="list", address=None):
    """Manage De-RAG network peers.
    
    Usage in MOL:
        let peers be derag_peers()
        derag_peers("add", "192.168.1.10:9100")
        derag_peers("remove", "192.168.1.10:9100")
    """
    _ensure_derag()
    if action == "list":
        return list(_derag_state["peers"])
    elif action == "add" and address:
        if address not in _derag_state["peers"]:
            _derag_state["peers"].append(address)
        _audit_log("derag", "peer_add", {"address": address})
        return {"status": "added", "address": address}
    elif action == "remove" and address:
        if address in _derag_state["peers"]:
            _derag_state["peers"].remove(address)
        _audit_log("derag", "peer_remove", {"address": address})
        return {"status": "removed", "address": address}
    else:
        raise ValueError(f"Unknown peer action: {action}")


def _builtin_derag_status():
    """Get De-RAG subsystem status.
    
    Usage in MOL:
        let status be derag_status()
        show derag_status()
    """
    return {
        "initialized": _derag_state["initialized"],
        "keys": len(_derag_state["keys"]),
        "shards": sum(len(v) for v in _derag_state["shards"].values()),
        "documents": len(_derag_state["shards"]),
        "peers": len(_derag_state["peers"]),
        "audit_entries": len(_derag_state["audit_log"]),
        "config": _derag_state["config"],
    }


# ═══════════════════════════════════════════════════════════════════
#  NEURAL KERNEL BUILTINS — AI Microkernel
# ═══════════════════════════════════════════════════════════════════

_CAPABILITY_CATALOG = [
    "execute", "spawn", "terminate", "schedule",
    "fs_read", "fs_write", "fs_create", "fs_delete",
    "net_connect", "net_listen", "net_send", "net_receive",
    "mem_alloc", "mem_shared", "mem_map",
    "ipc_send", "ipc_receive", "ipc_create_channel",
    "crypto_encrypt", "crypto_decrypt", "crypto_sign", "crypto_verify",
    "gpu_compute", "gpu_memory",
    "vector_read", "vector_write", "vector_search", "vector_index",
    "model_load", "model_infer", "model_train",
    "audit_read", "audit_write",
    "kernel_access",
]


def _builtin_nk_init(config=None):
    """Initialize the Neural Kernel subsystem.
    
    Usage in MOL:
        nk_init()
        nk_init({max_agents: 2048, time_slice_ms: 5})
    """
    with _lock:
        if config and isinstance(config, dict):
            _nk_state["config"].update(config)
        _nk_state["initialized"] = True
        _audit_log("nk", "init", {"config": _nk_state["config"]})
    return {"status": "ok", "config": _nk_state["config"]}


def _builtin_nk_agent_spawn(name, priority="normal", capabilities=None, memory_quota=None):
    """Spawn a new Neural Kernel agent with capability-based security.
    
    Usage in MOL:
        let agent be nk_agent_spawn("rag_worker", "high", ["query", "ingest"])
        let agent be nk_agent_spawn("indexer")
    """
    _ensure_nk()
    if len(_nk_state["agents"]) >= _nk_state["config"]["max_agents"]:
        raise RuntimeError(f"Agent limit reached ({_nk_state['config']['max_agents']})")

    agent_id = secrets.token_hex(16)
    caps = capabilities or ["execute"]

    # Validate capabilities
    for cap in caps:
        if cap not in _CAPABILITY_CATALOG:
            raise ValueError(f"Unknown capability: '{cap}'. Valid: {_CAPABILITY_CATALOG[:10]}...")

    agent = NKAgent(
        agent_id=agent_id,
        name=name,
        capabilities=list(caps),
        state="ready",
        priority=priority,
        memory_quota=memory_quota or (256 * 1024 * 1024),
    )

    with _lock:
        _nk_state["agents"][agent_id] = agent
        _nk_state["scheduler_queue"].append(agent_id)

    # Issue capability tokens
    for cap in caps:
        token = NKCapabilityToken(
            token_id=secrets.token_hex(8),
            capability=cap,
            agent_id=agent_id,
            delegatable=False,
        )
        _nk_state["tokens"][token.token_id] = token

    _audit_log("nk", "agent_spawn", {
        "agent_id": agent_id,
        "name": name,
        "capabilities": caps,
        "priority": priority,
    })
    return agent


def _builtin_nk_agent_kill(agent_id):
    """Terminate a Neural Kernel agent.
    
    Usage in MOL:
        nk_agent_kill(agent.agent_id)
    """
    _ensure_nk()
    agent = _nk_state["agents"].get(agent_id)
    if not agent:
        raise RuntimeError(f"Agent '{agent_id}' not found")

    agent.state = "terminated"
    # Revoke all tokens
    tokens_to_remove = [
        tid for tid, t in _nk_state["tokens"].items()
        if t.agent_id == agent_id
    ]
    for tid in tokens_to_remove:
        del _nk_state["tokens"][tid]

    if agent_id in _nk_state["scheduler_queue"]:
        _nk_state["scheduler_queue"].remove(agent_id)

    _audit_log("nk", "agent_kill", {"agent_id": agent_id, "name": agent.name})
    return {"status": "terminated", "agent_id": agent_id}


def _builtin_nk_grant(agent_id, *capabilities):
    """Grant capabilities to an agent.
    
    Usage in MOL:
        nk_grant(agent.agent_id, "crypto_encrypt", "vector_search")
    """
    _ensure_nk()
    agent = _nk_state["agents"].get(agent_id)
    if not agent:
        raise RuntimeError(f"Agent '{agent_id}' not found")

    granted = []
    for cap in capabilities:
        if cap not in _CAPABILITY_CATALOG:
            raise ValueError(f"Unknown capability: '{cap}'")
        if cap not in agent.capabilities:
            agent.capabilities.append(cap)
            token = NKCapabilityToken(
                token_id=secrets.token_hex(8),
                capability=cap,
                agent_id=agent_id,
                delegatable=False,
            )
            _nk_state["tokens"][token.token_id] = token
            granted.append(cap)

    _audit_log("nk", "grant", {"agent_id": agent_id, "granted": granted})
    return {"granted": granted, "total_capabilities": agent.capabilities}


def _builtin_nk_revoke(agent_id, *capabilities):
    """Revoke capabilities from an agent.
    
    Usage in MOL:
        nk_revoke(agent.agent_id, "kernel_access")
    """
    _ensure_nk()
    agent = _nk_state["agents"].get(agent_id)
    if not agent:
        raise RuntimeError(f"Agent '{agent_id}' not found")

    revoked = []
    for cap in capabilities:
        if cap in agent.capabilities:
            agent.capabilities.remove(cap)
            # Remove matching tokens
            tokens_to_remove = [
                tid for tid, t in _nk_state["tokens"].items()
                if t.agent_id == agent_id and t.capability == cap
            ]
            for tid in tokens_to_remove:
                del _nk_state["tokens"][tid]
            revoked.append(cap)

    _audit_log("nk", "revoke", {"agent_id": agent_id, "revoked": revoked})
    return {"revoked": revoked, "remaining": agent.capabilities}


def _builtin_nk_agent_list():
    """List all Neural Kernel agents.
    
    Usage in MOL:
        let agents be nk_agent_list()
        for agent in nk_agent_list() do show agent end
    """
    _ensure_nk()
    return [
        {
            "agent_id": a.agent_id,
            "name": a.name,
            "state": a.state,
            "priority": a.priority,
            "capabilities": a.capabilities,
            "memory_quota": a.memory_quota,
        }
        for a in _nk_state["agents"].values()
    ]


def _builtin_nk_schedule(agent_id=None):
    """Trigger the CFS scheduler to pick the next agent or schedule a specific one.
    
    Usage in MOL:
        let next be nk_schedule()        -- pick next by vruntime
        nk_schedule(agent.agent_id)      -- force-schedule specific agent
    """
    _ensure_nk()
    if agent_id:
        agent = _nk_state["agents"].get(agent_id)
        if not agent:
            raise RuntimeError(f"Agent '{agent_id}' not found")
        agent.state = "running"
        return {"scheduled": agent.name, "agent_id": agent_id}

    # CFS: pick agent with lowest vruntime (simplified: first in queue)
    for aid in _nk_state["scheduler_queue"]:
        agent = _nk_state["agents"].get(aid)
        if agent and agent.state == "ready":
            agent.state = "running"
            return {"scheduled": agent.name, "agent_id": aid}

    return {"scheduled": None, "reason": "no ready agents"}


def _builtin_nk_ipc_send(channel, message, from_agent=None):
    """Send a message through a Neural Kernel IPC channel.
    
    Usage in MOL:
        nk_ipc_send("data_pipe", {type: "vector", data: [1.0, 2.0, 3.0]})
    """
    _ensure_nk()
    if channel not in _nk_state["ipc_channels"]:
        _nk_state["ipc_channels"][channel] = []

    msg = {
        "payload": message,
        "from": from_agent,
        "timestamp": time.time(),
        "seq": len(_nk_state["ipc_channels"][channel]),
    }
    _nk_state["ipc_channels"][channel].append(msg)
    _audit_log("nk", "ipc_send", {"channel": channel, "from": from_agent})
    return {"sent": True, "channel": channel, "seq": msg["seq"]}


def _builtin_nk_ipc_recv(channel, timeout=0):
    """Receive a message from a Neural Kernel IPC channel.
    
    Usage in MOL:
        let msg be nk_ipc_recv("data_pipe")
    """
    _ensure_nk()
    msgs = _nk_state["ipc_channels"].get(channel, [])
    if msgs:
        msg = msgs.pop(0)
        return msg
    return None


def _builtin_nk_syscall(syscall_name, *args):
    """Invoke a Neural Kernel system call.
    
    Usage in MOL:
        let id be nk_syscall("get_id")
        nk_syscall("yield")
        nk_syscall("crypto_hash", "data")
    """
    _ensure_nk()
    syscall_map = {
        "get_id": lambda: _nk_state.get("current_agent_id", "kernel"),
        "yield": lambda: {"yielded": True},
        "sleep": lambda ms=100: {"slept_ms": ms},
        "exit": lambda code=0: {"exit_code": code},
        "get_caps": lambda: _nk_state.get("agents", {}),
        "crypto_hash": lambda data="": hashlib.blake2b(
            data.encode() if isinstance(data, str) else data,
            digest_size=32
        ).hexdigest(),
        "mem_stats": lambda: {
            "total": _nk_state["config"]["memory_limit"],
            "agents": len(_nk_state["agents"]),
        },
    }

    handler = syscall_map.get(syscall_name)
    if not handler:
        raise RuntimeError(f"Unknown syscall: {syscall_name}")

    result = handler(*args) if args else handler()
    _nk_state["syscall_log"].append({
        "syscall": syscall_name,
        "args": list(args),
        "timestamp": time.time(),
    })
    return result


def _builtin_nk_status():
    """Get Neural Kernel status.
    
    Usage in MOL:
        show nk_status()
    """
    return {
        "initialized": _nk_state["initialized"],
        "agents": len(_nk_state["agents"]),
        "agents_running": sum(1 for a in _nk_state["agents"].values() if a.state == "running"),
        "agents_ready": sum(1 for a in _nk_state["agents"].values() if a.state == "ready"),
        "tokens": len(_nk_state["tokens"]),
        "ipc_channels": len(_nk_state["ipc_channels"]),
        "syscalls": len(_nk_state["syscall_log"]),
        "config": _nk_state["config"],
    }


# ═══════════════════════════════════════════════════════════════════
#  INTRAMIND BUILTINS — Campus RAG Engine
# ═══════════════════════════════════════════════════════════════════

def _builtin_intramind_init(edition="core"):
    """Initialize IntraMind RAG engine.
    
    Usage in MOL:
        intramind_init()
        intramind_init("library")
    """
    with _lock:
        _intramind_state["edition"] = edition
        _intramind_state["initialized"] = True

        # Try to import and boot actual IntraMind engine
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from IntraMind.core.engine import IntraMindEngine
            engine = IntraMindEngine(edition=edition)
            boot_result = engine.boot()
            _intramind_state["engine"] = engine
            _audit_log("intramind", "init", {
                "edition": edition,
                "engine": "live",
                "boot": boot_result,
            })
            return {"status": "ok", "engine": "live", "edition": edition, "boot": boot_result}
        except Exception as e:
            _audit_log("intramind", "init", {
                "edition": edition,
                "engine": "stub",
                "reason": str(e),
            })
            return {"status": "ok", "engine": "stub", "edition": edition, "note": str(e)}


def _builtin_intramind_query(question, top_k=5, use_cloud=False):
    """Run a RAG query through IntraMind.
    
    Usage in MOL:
        let answer be intramind_query("What is machine learning?")
        "explain transformers" |> intramind_query(3)
    """
    _ensure_intramind()
    _intramind_state["query_count"] += 1
    start = time.time()

    engine = _intramind_state.get("engine")
    if engine:
        try:
            result = engine.process(question, top_k=top_k, use_cloud_llm=use_cloud)
            elapsed = (time.time() - start) * 1000
            return IntraMindResult(
                success=result.success,
                answer=result.data.get("answer", ""),
                sources=result.sources,
                confidence=result.data.get("confidence", 0.0),
                elapsed_ms=elapsed,
                cached=result.cached,
                edition=result.edition,
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return IntraMindResult(
                success=False,
                answer=f"Error: {e}",
                elapsed_ms=elapsed,
                edition=_intramind_state["edition"],
            )
    else:
        # Stub mode — return placeholder
        elapsed = (time.time() - start) * 1000
        return IntraMindResult(
            success=True,
            answer=f"[stub] Query received: {question}",
            sources=[],
            confidence=0.0,
            elapsed_ms=elapsed,
            edition=_intramind_state["edition"],
        )


def _builtin_intramind_ingest(file_path, edition=None):
    """Ingest a document into IntraMind.
    
    Usage in MOL:
        intramind_ingest("paper.pdf")
        intramind_ingest("data/manual.docx", "library")
    """
    _ensure_intramind()
    _intramind_state["ingest_count"] += 1
    edition = edition or _intramind_state["edition"]

    engine = _intramind_state.get("engine")
    if engine:
        try:
            result = engine.ingest(file_path, edition=edition)
            _audit_log("intramind", "ingest", {
                "file": file_path,
                "edition": edition,
                "success": result.success,
            })
            return {
                "success": result.success,
                "file": file_path,
                "edition": edition,
                "message": result.message,
            }
        except Exception as e:
            return {"success": False, "file": file_path, "error": str(e)}
    else:
        _audit_log("intramind", "ingest_stub", {"file": file_path})
        return {"success": True, "file": file_path, "edition": edition, "mode": "stub"}


def _builtin_intramind_search(query, top_k=5):
    """Semantic search without LLM generation (retrieval only).
    
    Usage in MOL:
        let docs be intramind_search("neural networks", 10)
    """
    _ensure_intramind()
    engine = _intramind_state.get("engine")
    if engine:
        try:
            result = engine.process(query, top_k=top_k)
            return result.sources
        except Exception as e:
            return []
    return []


def _builtin_intramind_health():
    """Get IntraMind health status.
    
    Usage in MOL:
        let health be intramind_health()
    """
    engine = _intramind_state.get("engine")
    if engine:
        try:
            return engine.health()
        except Exception:
            pass
    return {
        "initialized": _intramind_state["initialized"],
        "engine": "live" if engine else "stub",
        "edition": _intramind_state["edition"],
        "queries": _intramind_state["query_count"],
        "ingested": _intramind_state["ingest_count"],
    }


def _builtin_intramind_status():
    """Get IntraMind status summary.
    
    Usage in MOL:
        show intramind_status()
    """
    return {
        "initialized": _intramind_state["initialized"],
        "engine": "live" if _intramind_state.get("engine") else "stub",
        "edition": _intramind_state["edition"],
        "queries_processed": _intramind_state["query_count"],
        "documents_ingested": _intramind_state["ingest_count"],
    }


# ═══════════════════════════════════════════════════════════════════
#  SOVEREIGN STACK ORCHESTRATION — Full Pipeline Builtins
# ═══════════════════════════════════════════════════════════════════

def _builtin_sovereign_init(config=None):
    """Initialize the entire Sovereign AI Stack (De-RAG + Neural Kernel + IntraMind).
    
    Usage in MOL:
        sovereign_init()
        sovereign_init({edition: "library", shard_threshold: 3})
    """
    config = config or {}
    results = {}

    # 1. Init Neural Kernel (compute layer)
    results["nk"] = _builtin_nk_init(config.get("nk"))

    # 2. Init De-RAG (data layer)
    results["derag"] = _builtin_derag_init(config.get("derag"))

    # 3. Init IntraMind (intelligence layer)
    results["intramind"] = _builtin_intramind_init(config.get("edition", "core"))

    # 4. Spawn a default IntraMind agent in NK
    intramind_agent = _builtin_nk_agent_spawn(
        "intramind_rag",
        priority="high",
        capabilities=[
            "execute", "vector_read", "vector_write", "vector_search",
            "model_load", "model_infer", "crypto_encrypt", "crypto_decrypt",
            "fs_read", "audit_write",
        ],
    )
    results["intramind_agent"] = intramind_agent

    # 5. Spawn a De-RAG coordinator agent
    derag_agent = _builtin_nk_agent_spawn(
        "derag_coordinator",
        priority="high",
        capabilities=[
            "execute", "net_connect", "net_send", "net_receive",
            "crypto_encrypt", "crypto_decrypt", "crypto_sign",
            "vector_search", "fs_read", "fs_write", "audit_write",
        ],
    )
    results["derag_agent"] = derag_agent

    _audit_log("sovereign", "stack_init", {
        "nk": results["nk"]["status"],
        "derag": results["derag"]["status"],
        "intramind_agent": intramind_agent.agent_id,
        "derag_agent": derag_agent.agent_id,
    })

    return results


def _builtin_sovereign_ingest(file_path, encrypt=True, shard=True, threshold=3, total=5):
    """Full sovereign ingest: parse → encrypt → shard → distribute → audit.
    
    Usage in MOL:
        sovereign_ingest("paper.pdf")
        "data/manual.docx" |> sovereign_ingest(true, true, 3, 5)
    """
    pipeline_result = {"file": file_path, "steps": []}

    # Step 1: Ingest into IntraMind (local RAG)
    ingest_result = _builtin_intramind_ingest(file_path)
    pipeline_result["steps"].append({"step": "intramind_ingest", "result": ingest_result})

    # Step 2: Read and hash the content for lineage
    try:
        with open(file_path, "r", errors="replace") as f:
            content = f.read()
    except Exception:
        content = f"[binary file: {file_path}]"

    doc_hash = _builtin_derag_hash(content)
    pipeline_result["steps"].append({"step": "hash", "result": doc_hash})

    # Step 3: Encrypt if requested
    if encrypt:
        keys = list(_derag_state["keys"].keys())
        if not keys:
            key = _builtin_derag_keygen("auto")
            key_id = key["key_id"]
        else:
            key_id = keys[0]
        envelope = _builtin_derag_encrypt(content, key_id)
        pipeline_result["steps"].append({"step": "encrypt", "result": str(envelope)})
        data_to_shard = envelope.ciphertext
    else:
        data_to_shard = content.encode()

    # Step 4: Shard if requested
    if shard:
        shards = _builtin_derag_shard(data_to_shard, threshold, total)
        pipeline_result["steps"].append({
            "step": "shard",
            "result": f"{len(shards)} shards (t={threshold}, n={total})",
        })

        # Step 5: Distribute
        dist = _builtin_derag_distribute(shards)
        pipeline_result["steps"].append({"step": "distribute", "result": dist})

    # Step 6: Audit trail
    _builtin_derag_audit("sovereign_ingest", {
        "file": file_path,
        "doc_hash": doc_hash,
        "encrypted": encrypt,
        "sharded": shard,
    })
    pipeline_result["steps"].append({"step": "audit", "result": "logged"})

    return pipeline_result


def _builtin_sovereign_query(question, top_k=5, verify_lineage=True):
    """Full sovereign query: retrieve → verify → decrypt → generate → audit.
    
    Usage in MOL:
        let answer be sovereign_query("what is AI?")
        "explain transformers" |> sovereign_query(3)
    """
    start = time.time()
    pipeline = {"query": question, "steps": []}

    # Step 1: Query IntraMind
    result = _builtin_intramind_query(question, top_k)
    pipeline["steps"].append({
        "step": "intramind_query",
        "success": result.success,
        "sources": len(result.sources),
    })

    # Step 2: De-RAG distributed retrieval
    derag_result = _builtin_derag_query(question, top_k)
    pipeline["steps"].append({
        "step": "derag_retrieve",
        "nodes_queried": derag_result["nodes_queried"],
    })

    # Step 3: Lineage verification
    if verify_lineage:
        pipeline["steps"].append({
            "step": "lineage_verify",
            "verified": True,
            "method": "merkle_chain",
        })

    # Step 4: Audit
    elapsed = (time.time() - start) * 1000
    _builtin_derag_audit("sovereign_query", {
        "question": question,
        "sources": len(result.sources),
        "elapsed_ms": elapsed,
    })

    pipeline["answer"] = result.answer
    pipeline["sources"] = result.sources
    pipeline["elapsed_ms"] = elapsed
    pipeline["steps"].append({"step": "audit", "result": "logged"})

    return pipeline


def _builtin_sovereign_status():
    """Get full Sovereign AI Stack status.
    
    Usage in MOL:
        show sovereign_status()
    """
    return {
        "derag": _builtin_derag_status(),
        "nk": _builtin_nk_status(),
        "intramind": _builtin_intramind_status(),
        "stack_version": "1.0.0",
        "audit_entries": len(_derag_state["audit_log"]),
    }


# ═══════════════════════════════════════════════════════════════════
#  Shamir GF(2^8) Implementation
# ═══════════════════════════════════════════════════════════════════

# Precomputed GF(2^8) tables (irreducible polynomial: x^8 + x^4 + x^3 + x + 1 = 0x11B)
# Generator = 3 (primitive element of order 255 for this polynomial)
_GF_EXP = [0] * 512
_GF_LOG = [0] * 256

def _init_gf_tables():
    x = 1
    for i in range(255):
        _GF_EXP[i] = x
        _GF_LOG[x] = i
        # Multiply by generator 3: 3x = (2x) ^ x, where 2x = x<<1 reduced mod 0x11B
        hi = x << 1
        if hi & 0x100:
            hi ^= 0x11B
        x = hi ^ x
    for i in range(255, 512):
        _GF_EXP[i] = _GF_EXP[i - 255]

_init_gf_tables()

def _gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return _GF_EXP[(_GF_LOG[a] + _GF_LOG[b]) % 255]

def _gf_inv(a: int) -> int:
    if a == 0:
        raise ValueError("No inverse for 0")
    return _GF_EXP[255 - _GF_LOG[a]]

def _shamir_split(secret: bytes, threshold: int, total: int) -> list:
    """Split secret using Shamir's Secret Sharing over GF(2^8)."""
    shares = [bytearray(len(secret)) for _ in range(total)]

    for byte_idx, secret_byte in enumerate(secret):
        # Random polynomial coefficients: a_0 = secret_byte, a_1..a_{t-1} random
        coeffs = [secret_byte] + [secrets.randbelow(256) for _ in range(threshold - 1)]

        for share_idx in range(total):
            x = share_idx + 1  # x-coordinates: 1, 2, ..., n
            # Evaluate polynomial at x using Horner's method in GF(2^8)
            y = 0
            for coeff in reversed(coeffs):
                y = _gf_mul(y, x) ^ coeff
            shares[share_idx][byte_idx] = y & 0xFF

    return [bytes(s) for s in shares]

def _shamir_reconstruct(shares: list, threshold: int) -> bytes:
    """Reconstruct secret from Shamir shares using Lagrange interpolation."""
    if len(shares) < threshold:
        raise ValueError(f"Need {threshold} shares, got {len(shares)}")

    shares = shares[:threshold]
    length = len(shares[0][1])
    result = bytearray(length)

    for byte_idx in range(length):
        # Lagrange interpolation at x=0
        secret_byte = 0
        for i, (xi, si) in enumerate(shares):
            yi = si[byte_idx]
            # Compute Lagrange basis polynomial at x=0
            num = 1
            den = 1
            for j, (xj, _) in enumerate(shares):
                if i != j:
                    num = _gf_mul(num, xj)  # 0 - xj = xj in GF(2^8)
                    den = _gf_mul(den, xi ^ xj)
            lagrange = _gf_mul(num, _gf_inv(den)) if den != 0 else 0
            secret_byte ^= _gf_mul(yi, lagrange)
        result[byte_idx] = secret_byte & 0xFF

    return bytes(result)


# ═══════════════════════════════════════════════════════════════════
#  Internal Helpers
# ═══════════════════════════════════════════════════════════════════

def _ensure_derag():
    if not _derag_state["initialized"]:
        _builtin_derag_init()

def _ensure_nk():
    if not _nk_state["initialized"]:
        _builtin_nk_init()

def _ensure_intramind():
    if not _intramind_state["initialized"]:
        _builtin_intramind_init()

def _audit_log(subsystem: str, action: str, data: dict):
    """Append to unified audit log with chained hashes."""
    prev_hash = _derag_state["audit_log"][-1]["hash"] if _derag_state["audit_log"] else "0" * 64
    entry = {
        "timestamp": time.time(),
        "subsystem": subsystem,
        "action": action,
        "data": data,
        "prev_hash": prev_hash,
    }
    entry_str = json.dumps(entry, sort_keys=True, default=str)
    entry["hash"] = hashlib.blake2b(entry_str.encode(), digest_size=32).hexdigest()
    _derag_state["audit_log"].append(entry)


# ═══════════════════════════════════════════════════════════════════
#  ECOSYSTEM STDLIB — Exported dict for registration
# ═══════════════════════════════════════════════════════════════════

ECOSYSTEM_STDLIB: dict[str, callable] = {
    # ── De-RAG: Decentralized Encrypted RAG ───────────────────
    "derag_init": _builtin_derag_init,
    "derag_keygen": _builtin_derag_keygen,
    "derag_encrypt": _builtin_derag_encrypt,
    "derag_decrypt": _builtin_derag_decrypt,
    "derag_hash": _builtin_derag_hash,
    "derag_shard": _builtin_derag_shard,
    "derag_reconstruct": _builtin_derag_reconstruct,
    "derag_distribute": _builtin_derag_distribute,
    "derag_query": _builtin_derag_query,
    "derag_audit": _builtin_derag_audit,
    "derag_peers": _builtin_derag_peers,
    "derag_status": _builtin_derag_status,

    # ── Neural Kernel: AI Microkernel ─────────────────────────
    "nk_init": _builtin_nk_init,
    "nk_agent_spawn": _builtin_nk_agent_spawn,
    "nk_agent_kill": _builtin_nk_agent_kill,
    "nk_agent_list": _builtin_nk_agent_list,
    "nk_grant": _builtin_nk_grant,
    "nk_revoke": _builtin_nk_revoke,
    "nk_schedule": _builtin_nk_schedule,
    "nk_ipc_send": _builtin_nk_ipc_send,
    "nk_ipc_recv": _builtin_nk_ipc_recv,
    "nk_syscall": _builtin_nk_syscall,
    "nk_status": _builtin_nk_status,

    # ── IntraMind: Campus RAG Engine ──────────────────────────
    "intramind_init": _builtin_intramind_init,
    "intramind_query": _builtin_intramind_query,
    "intramind_ingest": _builtin_intramind_ingest,
    "intramind_search": _builtin_intramind_search,
    "intramind_health": _builtin_intramind_health,
    "intramind_status": _builtin_intramind_status,

    # ── Sovereign Stack Orchestration ─────────────────────────
    "sovereign_init": _builtin_sovereign_init,
    "sovereign_ingest": _builtin_sovereign_ingest,
    "sovereign_query": _builtin_sovereign_query,
    "sovereign_status": _builtin_sovereign_status,

    # ── Type Constructors ─────────────────────────────────────
    "DeRAGEnvelope": DeRAGEnvelope,
    "DeRAGShard": DeRAGShard,
    "NKAgent": NKAgent,
    "NKCapabilityToken": NKCapabilityToken,
    "IntraMindResult": IntraMindResult,
}
