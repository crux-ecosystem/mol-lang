"""
MOL Domain Types
=================

Built-in types specific to IntraMind: Thought, Memory, Node, Stream.
These are first-class citizens in MOL — not just strings and integers.

v2.0.0 additions: Vector, Encrypted, SwarmCluster as primitive types.
"""

import time
import uuid

# Re-export new v2.0.0 primitive types so they're accessible from mol.types
from mol.vector_engine import (
    Vector, QuantizedVector, VectorIndex, VectorError,
)
from mol.encryption import (
    EncryptedValue, EncryptedVector, EncryptedMemory,
    CryptoKeyPair, CryptoError, EncryptionError,
)
from mol.swarm_runtime import SwarmCluster


class MolObject:
    """Base class for all MOL domain objects."""

    def __init__(self):
        self._id = str(uuid.uuid4())[:8]
        self._created_at = time.time()
        self._access_level = "public"

    def mol_repr(self) -> str:
        return f"<{self.__class__.__name__}:{self._id}>"

    def __repr__(self):
        return self.mol_repr()


class Thought(MolObject):
    """
    Represents a cognitive unit — an idea, observation, or inference.
    Can carry a payload of data and a confidence score.
    """

    def __init__(self, content="", confidence=1.0):
        super().__init__()
        self.content = content
        self.confidence = min(max(confidence, 0.0), 1.0)
        self.tags: list[str] = []
        self.linked_thoughts: list["Thought"] = []

    def tag(self, *tags):
        self.tags.extend(tags)
        return self

    def link(self, other: "Thought"):
        self.linked_thoughts.append(other)
        return self

    def mol_repr(self):
        return f'<Thought:{self._id} "{self.content}" conf={self.confidence}>'

    def to_dict(self):
        return {
            "id": self._id,
            "content": self.content,
            "confidence": self.confidence,
            "tags": self.tags,
        }


class Memory(MolObject):
    """
    Persistent storage unit within IntraMind. Memories can be
    stored, recalled, and can decay over time.
    """

    def __init__(self, key="", value=None):
        super().__init__()
        self.key = key
        self.value = value
        self.strength = 1.0       # decays over time
        self.recall_count = 0
        self._access_level = "protected"

    def recall(self):
        self.recall_count += 1
        self.strength = min(self.strength + 0.1, 1.0)
        return self.value

    def decay(self, amount=0.05):
        self.strength = max(self.strength - amount, 0.0)
        return self

    def mol_repr(self):
        return f'<Memory:{self._id} key="{self.key}" strength={self.strength:.2f}>'

    def to_dict(self):
        return {
            "id": self._id,
            "key": self.key,
            "value": self.value,
            "strength": self.strength,
        }


class Node(MolObject):
    """
    A computational node in IntraMind's neural graph.
    Nodes can connect, activate, and evolve.
    """

    def __init__(self, label="", weight=0.0):
        super().__init__()
        self.label = label
        self.weight = weight
        self.connections: list["Node"] = []
        self.active = False
        self.generation = 0

    def connect(self, other: "Node"):
        self.connections.append(other)
        return self

    def activate(self):
        self.active = True
        return self

    def deactivate(self):
        self.active = False
        return self

    def evolve(self, factor=1.1):
        self.weight *= factor
        self.generation += 1
        return self

    def mol_repr(self):
        state = "active" if self.active else "idle"
        return f'<Node:{self._id} "{self.label}" w={self.weight:.2f} {state} gen={self.generation}>'

    def to_dict(self):
        return {
            "id": self._id,
            "label": self.label,
            "weight": self.weight,
            "active": self.active,
            "generation": self.generation,
        }


class Stream(MolObject):
    """
    A data stream for real-time data flow within IntraMind.
    Supports buffering, emitting, and subscribing.
    """

    def __init__(self, name=""):
        super().__init__()
        self.name = name
        self.buffer: list = []
        self.subscribers: list = []
        self._synced = False

    def emit(self, data):
        self.buffer.append(data)
        for cb in self.subscribers:
            cb(data)
        return self

    def subscribe(self, callback):
        self.subscribers.append(callback)
        return self

    def sync(self):
        self._synced = True
        return self

    def consume(self):
        data = list(self.buffer)
        self.buffer.clear()
        return data

    def mol_repr(self):
        synced = "synced" if self._synced else "unsynced"
        return f'<Stream:{self._id} "{self.name}" buf={len(self.buffer)} {synced}>'

    def to_dict(self):
        return {
            "id": self._id,
            "name": self.name,
            "buffer_size": len(self.buffer),
            "synced": self._synced,
        }


# ── RAG Pipeline Types (v0.2.0) ─────────────────────────────

class Document(MolObject):
    """
    A text document — the starting point of any RAG pipeline.
    Can be loaded from files and chunked for processing.
    """

    def __init__(self, source="", content=""):
        super().__init__()
        self.source = source
        self.content = content
        self.metadata: dict = {}

    def mol_repr(self):
        size = len(self.content)
        if size > 1024:
            size_str = f"{size / 1024:.1f}KB"
        else:
            size_str = f"{size}B"
        return f'<Document:{self._id} "{self.source}" {size_str}>'

    def to_dict(self):
        return {
            "id": self._id,
            "source": self.source,
            "content_length": len(self.content),
            "metadata": self.metadata,
        }


class Chunk(MolObject):
    """
    A chunk of text from a document. Produced by the chunk() pipeline stage.
    """

    def __init__(self, content="", index=0, source=""):
        super().__init__()
        self.content = content
        self.index = index
        self.source = source

    def mol_repr(self):
        preview = self.content[:30] + "..." if len(self.content) > 30 else self.content
        preview = preview.replace("\n", " ")
        return f'<Chunk:{self._id} #{self.index} "{preview}">'

    def to_dict(self):
        return {
            "id": self._id,
            "content": self.content,
            "index": self.index,
            "source": self.source,
        }


class Embedding(MolObject):
    """
    A vector embedding of text. Uses deterministic hash-based simulation
    (plug in real models via IntraMind in v0.3+).
    """

    def __init__(self, text="", model="mol-sim-v1"):
        super().__init__()
        self.text = text[:80]
        self.model = model
        self.dimensions = 64
        self.vector = self._hash_embed(text)

    def _hash_embed(self, text):
        """Deterministic pseudo-embedding from text hash — same text = same vector."""
        import hashlib
        h = hashlib.sha256(text.encode()).hexdigest()
        vec = []
        for i in range(self.dimensions):
            idx = (i * 2) % len(h)
            val = int(h[idx:idx + 2], 16) / 255.0
            vec.append(val)
        norm = sum(v * v for v in vec) ** 0.5
        return [v / norm for v in vec] if norm > 0 else vec

    def mol_repr(self):
        return f'<Embedding:{self._id} dim={self.dimensions} model="{self.model}">'

    def to_dict(self):
        return {
            "id": self._id,
            "text": self.text,
            "model": self.model,
            "dimensions": self.dimensions,
        }


class VectorStore(MolObject):
    """
    In-memory vector store for embeddings. Supports add + similarity search.
    (Plugs into FAISS/Milvus in v0.4+.)
    """

    def __init__(self, name="default"):
        super().__init__()
        self.name = name
        self.entries: list[dict] = []

    def add(self, embedding, chunk=None, text=""):
        self.entries.append({
            "embedding": embedding,
            "chunk": chunk,
            "text": text,
        })

    def search(self, query_emb, top_k=3):
        results = []
        for entry in self.entries:
            sim = self._cosine_sim(query_emb.vector, entry["embedding"].vector)
            results.append({
                "chunk": entry.get("chunk"),
                "text": entry.get("text", ""),
                "score": round(sim, 4),
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @staticmethod
    def _cosine_sim(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def mol_repr(self):
        return f'<VectorStore:{self._id} "{self.name}" {len(self.entries)} vectors>'

    def to_dict(self):
        return {
            "id": self._id,
            "name": self.name,
            "count": len(self.entries),
        }
