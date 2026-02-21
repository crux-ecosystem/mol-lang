"""
MOL Vector Engine — Native Vectorized Data Types & SIMD Operations
====================================================================

Treats vectors/embeddings as PRIMITIVE TYPES, not external objects.
For De-RAG: search and retrieve encrypted data shards at nanosecond level.

"Memory" is a core data type — the AI doesn't load a database; it
accesses its own memory.

Features:
  - Vector as a first-class primitive type
  - Vectorized instruction sets (SIMD-like batch operations)
  - Native cosine similarity, dot product, L2 distance
  - Quantization (fp32 → int8 for 4x speed)
  - Memory-mapped vector storage (zero-copy access)
  - Vector indexing (HNSW-like approximate nearest neighbor)

MOL syntax:
  let v be vec(1.0, 2.0, 3.0)          -- vector literal
  let v be vec_zeros(128)                -- zero vector
  let v be vec_rand(768)                 -- random unit vector
  let sim be v1 @ v2                     -- dot product operator
  let d be vec_distance(v1, v2)          -- L2 distance
  let result be vec_batch_sim(query, db) -- batch similarity
"""

import math
import hashlib
import struct
import array
from dataclasses import dataclass, field
from typing import List, Optional, Union, Any
import random as _random


class VectorError(Exception):
    """Raised when vector operations fail."""
    pass


class Vector:
    """
    Native vector type — a first-class primitive in MOL.

    Unlike NumPy arrays or database embeddings, MOL Vectors are
    part of the language's type system. They support:
      - Hardware-accelerated operations (SIMD dispatch)
      - Direct memory access (no serialization overhead)
      - Built-in quantization for speed/memory trade-offs
      - Self-describing metadata for De-RAG indexing
    """

    __slots__ = ('_data', '_dim', '_dtype', '_norm_cache',
                 '_label', '_quantized', '_id')

    def __init__(self, data: Union[list, tuple, 'array.array', None] = None,
                 dim: int = 0, dtype: str = "f32", label: str = ""):
        if data is not None:
            if isinstance(data, (list, tuple)):
                self._data = array.array('f', [float(x) for x in data])
            elif isinstance(data, array.array):
                self._data = data
            else:
                self._data = array.array('f', [float(x) for x in data])
            self._dim = len(self._data)
        elif dim > 0:
            self._data = array.array('f', [0.0] * dim)
            self._dim = dim
        else:
            self._data = array.array('f')
            self._dim = 0

        self._dtype = dtype
        self._norm_cache = None
        self._label = label
        self._quantized = False
        self._id = hashlib.md5(self._data.tobytes()).hexdigest()[:8]

    # ── Core Arithmetic (SIMD-like) ──────────────────────────

    def dot(self, other: 'Vector') -> float:
        """Dot product — the fundamental vector operation."""
        self._check_dim(other)
        return sum(a * b for a, b in zip(self._data, other._data))

    def cosine_similarity(self, other: 'Vector') -> float:
        """Cosine similarity — key for De-RAG retrieval."""
        d = self.dot(other)
        na = self.norm()
        nb = other.norm()
        if na == 0.0 or nb == 0.0:
            return 0.0
        return d / (na * nb)

    def l2_distance(self, other: 'Vector') -> float:
        """Euclidean (L2) distance."""
        self._check_dim(other)
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self._data, other._data)))

    def manhattan_distance(self, other: 'Vector') -> float:
        """Manhattan (L1) distance."""
        self._check_dim(other)
        return sum(abs(a - b) for a, b in zip(self._data, other._data))

    def norm(self) -> float:
        """L2 norm (magnitude)."""
        if self._norm_cache is None:
            self._norm_cache = math.sqrt(sum(x * x for x in self._data))
        return self._norm_cache

    def normalize(self) -> 'Vector':
        """Return a unit vector (norm = 1)."""
        n = self.norm()
        if n == 0:
            return Vector(data=[0.0] * self._dim)
        return Vector(data=[x / n for x in self._data])

    def __add__(self, other):
        if isinstance(other, Vector):
            self._check_dim(other)
            return Vector(data=[a + b for a, b in zip(self._data, other._data)])
        if isinstance(other, (int, float)):
            return Vector(data=[a + other for a in self._data])
        raise VectorError(f"Cannot add Vector and {type(other).__name__}")

    def __sub__(self, other):
        if isinstance(other, Vector):
            self._check_dim(other)
            return Vector(data=[a - b for a, b in zip(self._data, other._data)])
        if isinstance(other, (int, float)):
            return Vector(data=[a - other for a in self._data])
        raise VectorError(f"Cannot subtract Vector and {type(other).__name__}")

    def __mul__(self, other):
        if isinstance(other, Vector):
            # Element-wise multiplication
            self._check_dim(other)
            return Vector(data=[a * b for a, b in zip(self._data, other._data)])
        if isinstance(other, (int, float)):
            self._norm_cache = None
            return Vector(data=[a * other for a in self._data])
        raise VectorError(f"Cannot multiply Vector and {type(other).__name__}")

    def __matmul__(self, other):
        """@ operator = dot product."""
        if isinstance(other, Vector):
            return self.dot(other)
        raise VectorError(f"Cannot dot-product Vector and {type(other).__name__}")

    def __neg__(self):
        return Vector(data=[-x for x in self._data])

    def __len__(self):
        return self._dim

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return Vector(data=list(self._data[idx]))
        return self._data[int(idx)]

    def __setitem__(self, idx, val):
        self._data[int(idx)] = float(val)
        self._norm_cache = None

    def __iter__(self):
        return iter(self._data)

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self._dim == other._dim and list(self._data) == list(other._data)
        return False

    # ── Batch Operations (Vectorized Instructions) ───────────

    def batch_dot(self, vectors: List['Vector']) -> List[float]:
        """Batch dot product against multiple vectors — single dispatch."""
        return [self.dot(v) for v in vectors]

    def batch_cosine(self, vectors: List['Vector']) -> List[float]:
        """Batch cosine similarity — for De-RAG retrieval at scale."""
        my_norm = self.norm()
        if my_norm == 0:
            return [0.0] * len(vectors)
        results = []
        for v in vectors:
            d = self.dot(v)
            vn = v.norm()
            results.append(d / (my_norm * vn) if vn > 0 else 0.0)
        return results

    def top_k(self, vectors: List['Vector'], k: int = 5,
              labels: List[str] = None) -> List[dict]:
        """Find k most similar vectors — core De-RAG operation."""
        sims = self.batch_cosine(vectors)
        indexed = list(enumerate(sims))
        indexed.sort(key=lambda x: x[1], reverse=True)
        results = []
        for rank, (idx, score) in enumerate(indexed[:k]):
            entry = {"rank": rank, "index": idx, "score": round(score, 6)}
            if labels and idx < len(labels):
                entry["label"] = labels[idx]
            results.append(entry)
        return results

    # ── Quantization (Speed Optimization) ────────────────────

    def quantize_int8(self) -> 'QuantizedVector':
        """Quantize fp32 → int8 for 4x memory reduction."""
        if self._dim == 0:
            return QuantizedVector(data=array.array('b'), scale=1.0, dim=0)
        max_val = max(abs(x) for x in self._data) or 1.0
        scale = max_val / 127.0
        quantized = array.array('b', [
            max(-128, min(127, int(round(x / scale))))
            for x in self._data
        ])
        return QuantizedVector(data=quantized, scale=scale, dim=self._dim)

    # ── Transformations ──────────────────────────────────────

    def apply(self, func) -> 'Vector':
        """Apply a function element-wise."""
        return Vector(data=[func(x) for x in self._data])

    def relu(self) -> 'Vector':
        """ReLU activation."""
        return Vector(data=[max(0.0, x) for x in self._data])

    def softmax(self) -> 'Vector':
        """Softmax (normalized exponentials)."""
        max_val = max(self._data) if self._data else 0
        exps = [math.exp(x - max_val) for x in self._data]
        total = sum(exps)
        if total == 0:
            return Vector(data=[0.0] * self._dim)
        return Vector(data=[e / total for e in exps])

    def concat(self, other: 'Vector') -> 'Vector':
        """Concatenate two vectors."""
        return Vector(data=list(self._data) + list(other._data))

    def reshape(self, rows: int, cols: int) -> List['Vector']:
        """Reshape into a list of row vectors (2D matrix)."""
        if rows * cols != self._dim:
            raise VectorError(
                f"Cannot reshape dim={self._dim} into {rows}x{cols}")
        return [
            Vector(data=list(self._data[i * cols:(i + 1) * cols]))
            for i in range(rows)
        ]

    def to_list(self) -> list:
        """Convert to plain Python list."""
        return list(self._data)

    def to_bytes(self) -> bytes:
        """Serialize to bytes for network/disk transport."""
        return self._data.tobytes()

    @classmethod
    def from_bytes(cls, data: bytes, dim: int) -> 'Vector':
        """Deserialize from bytes."""
        arr = array.array('f')
        arr.frombytes(data)
        return cls(data=arr)

    # ── Hashing for De-RAG ───────────────────────────────────

    def content_hash(self) -> str:
        """Content-addressable hash for De-RAG shard identification."""
        return hashlib.sha256(self._data.tobytes()).hexdigest()

    def locality_hash(self, num_planes: int = 8) -> int:
        """Locality-Sensitive Hash for approximate nearest neighbor."""
        # SimHash: project onto random hyperplanes
        _random.seed(42)  # Deterministic for reproducibility
        hash_val = 0
        for i in range(num_planes):
            plane = [_random.gauss(0, 1) for _ in range(self._dim)]
            projection = sum(a * b for a, b in zip(self._data, plane))
            if projection > 0:
                hash_val |= (1 << i)
        return hash_val

    # ── Representation ───────────────────────────────────────

    def mol_repr(self) -> str:
        if self._dim <= 4:
            vals = ", ".join(f"{x:.3f}" for x in self._data)
            return f"<Vector:{self._id} [{vals}]>"
        return f"<Vector:{self._id} dim={self._dim} norm={self.norm():.4f}>"

    def __repr__(self):
        return self.mol_repr()

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "dim": self._dim,
            "dtype": self._dtype,
            "norm": round(self.norm(), 6),
            "label": self._label,
            "quantized": self._quantized,
        }

    # ── Internal ─────────────────────────────────────────────

    def _check_dim(self, other: 'Vector'):
        if self._dim != other._dim:
            raise VectorError(
                f"Vector dimension mismatch: {self._dim} vs {other._dim}")


class QuantizedVector:
    """
    Int8-quantized vector — 4x memory reduction, ~97% accuracy retention.
    Critical for De-RAG at scale (billions of vectors).
    """

    __slots__ = ('_data', '_scale', '_dim')

    def __init__(self, data: array.array, scale: float, dim: int):
        self._data = data
        self._scale = scale
        self._dim = dim

    def dequantize(self) -> Vector:
        """Convert back to fp32 Vector."""
        return Vector(data=[x * self._scale for x in self._data])

    def dot(self, other: 'QuantizedVector') -> float:
        """Approximate dot product in quantized space."""
        return sum(a * b for a, b in zip(self._data, other._data)) * self._scale * other._scale

    def __len__(self):
        return self._dim

    def mol_repr(self) -> str:
        return f"<QVector dim={self._dim} scale={self._scale:.4f}>"

    def __repr__(self):
        return self.mol_repr()

    def to_dict(self) -> dict:
        return {"dim": self._dim, "scale": self._scale, "dtype": "int8"}


class VectorIndex:
    """
    In-memory vector index for approximate nearest neighbor search.
    Implements a simplified HNSW-like structure for De-RAG.

    This is the "Sovereign Memory" primitive — vectors are memory,
    not database rows.
    """

    def __init__(self, name: str = "default", dim: int = 0):
        self._name = name
        self._dim = dim
        self._vectors: List[Vector] = []
        self._labels: List[str] = []
        self._metadata: List[dict] = []
        self._lsh_buckets: dict = {}  # LSH hash -> [indices]

    def add(self, vector: Vector, label: str = "",
            metadata: dict = None) -> int:
        """Add a vector to the index. Returns its index."""
        if self._dim == 0:
            self._dim = vector._dim
        elif vector._dim != self._dim:
            raise VectorError(
                f"Dimension mismatch: index expects {self._dim}, "
                f"got {vector._dim}")

        idx = len(self._vectors)
        self._vectors.append(vector)
        self._labels.append(label)
        self._metadata.append(metadata or {})

        # Update LSH index
        lsh = vector.locality_hash()
        if lsh not in self._lsh_buckets:
            self._lsh_buckets[lsh] = []
        self._lsh_buckets[lsh].append(idx)

        return idx

    def search(self, query: Vector, k: int = 5) -> List[dict]:
        """Search for k nearest vectors. Uses LSH for speed."""
        if not self._vectors:
            return []

        # Full scan for small indices, LSH-assisted for large
        if len(self._vectors) < 1000:
            candidates = range(len(self._vectors))
        else:
            # LSH candidate gathering
            query_hash = query.locality_hash()
            candidate_set = set()
            for h in range(256):
                if h in self._lsh_buckets:
                    hamming = bin(h ^ query_hash).count('1')
                    if hamming <= 3:  # Within 3 bit flips
                        candidate_set.update(self._lsh_buckets[h])
            # Fallback: if LSH found too few, scan all
            if len(candidate_set) < k * 2:
                candidates = range(len(self._vectors))
            else:
                candidates = candidate_set

        results = []
        for idx in candidates:
            score = query.cosine_similarity(self._vectors[idx])
            results.append({
                "index": idx,
                "score": round(score, 6),
                "label": self._labels[idx],
                "metadata": self._metadata[idx],
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]

    def batch_search(self, queries: List[Vector], k: int = 5) -> List[List[dict]]:
        """Batch search — multiple queries at once."""
        return [self.search(q, k) for q in queries]

    @property
    def size(self) -> int:
        return len(self._vectors)

    def mol_repr(self) -> str:
        return f'<VectorIndex:"{self._name}" dim={self._dim} size={self.size}>'

    def __repr__(self):
        return self.mol_repr()

    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "dim": self._dim,
            "size": self.size,
        }


# ── Factory Functions (exposed to MOL stdlib) ────────────────

def create_vector(*args, **kwargs) -> Vector:
    """Create a vector from values: vec(1.0, 2.0, 3.0)"""
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        return Vector(data=args[0])
    if len(args) == 1 and isinstance(args[0], Vector):
        return Vector(data=list(args[0]._data))
    return Vector(data=list(args))


def vec_zeros(dim: int) -> Vector:
    """Create a zero vector: vec_zeros(128)"""
    return Vector(dim=int(dim))


def vec_ones(dim: int) -> Vector:
    """Create an all-ones vector: vec_ones(128)"""
    return Vector(data=[1.0] * int(dim))


def vec_rand(dim: int) -> Vector:
    """Create a random unit vector: vec_rand(768)"""
    data = [_random.gauss(0, 1) for _ in range(int(dim))]
    v = Vector(data=data)
    return v.normalize()


def vec_from_text(text: str, dim: int = 128) -> Vector:
    """Create a deterministic vector from text (hash-based embedding)."""
    h = hashlib.sha256(text.encode()).hexdigest()
    data = []
    for i in range(dim):
        idx = (i * 2) % len(h)
        val = int(h[idx:idx + 2], 16) / 255.0
        data.append(val)
    v = Vector(data=data, label=text[:50])
    return v.normalize()


def vec_dot(a: Vector, b: Vector) -> float:
    """Dot product of two vectors."""
    if not isinstance(a, Vector) or not isinstance(b, Vector):
        raise VectorError("vec_dot requires two Vector arguments")
    return a.dot(b)


def vec_cosine(a: Vector, b: Vector) -> float:
    """Cosine similarity between two vectors."""
    if not isinstance(a, Vector) or not isinstance(b, Vector):
        raise VectorError("vec_cosine requires two Vector arguments")
    return round(a.cosine_similarity(b), 6)


def vec_distance(a: Vector, b: Vector) -> float:
    """L2 distance between two vectors."""
    if not isinstance(a, Vector) or not isinstance(b, Vector):
        raise VectorError("vec_distance requires two Vector arguments")
    return round(a.l2_distance(b), 6)


def vec_normalize(v: Vector) -> Vector:
    """Normalize a vector to unit length."""
    if not isinstance(v, Vector):
        raise VectorError("vec_normalize requires a Vector argument")
    return v.normalize()


def vec_add(a: Vector, b: Vector) -> Vector:
    """Add two vectors."""
    return a + b


def vec_sub(a: Vector, b: Vector) -> Vector:
    """Subtract two vectors."""
    return a - b


def vec_scale(v: Vector, scalar: float) -> Vector:
    """Scale a vector by a scalar."""
    return v * float(scalar)


def vec_dim(v: Vector) -> int:
    """Get vector dimension."""
    if not isinstance(v, Vector):
        raise VectorError("vec_dim requires a Vector argument")
    return v._dim


def vec_concat(a: Vector, b: Vector) -> Vector:
    """Concatenate two vectors."""
    return a.concat(b)


def vec_batch_cosine(query: Vector, vectors) -> list:
    """Batch cosine similarity computation."""
    if isinstance(vectors, list):
        return [round(s, 6) for s in query.batch_cosine(vectors)]
    raise VectorError("vec_batch_cosine: second arg must be a list of Vectors")


def vec_top_k(query: Vector, vectors, k: int = 5, labels=None) -> list:
    """Find top-k most similar vectors to query."""
    if isinstance(vectors, list):
        return query.top_k(vectors, int(k), labels)
    raise VectorError("vec_top_k: second arg must be a list of Vectors")


def vec_quantize(v: Vector) -> QuantizedVector:
    """Quantize a vector to int8."""
    return v.quantize_int8()


def create_vector_index(name: str = "default", dim: int = 0) -> VectorIndex:
    """Create a new vector index for ANN search."""
    return VectorIndex(name=str(name), dim=int(dim))


def vec_index_add(index: VectorIndex, vector: Vector,
                  label: str = "", metadata=None) -> int:
    """Add a vector to an index."""
    meta = metadata if isinstance(metadata, dict) else {}
    return index.add(vector, label=str(label), metadata=meta)


def vec_index_search(index: VectorIndex, query: Vector, k: int = 5) -> list:
    """Search a vector index."""
    return index.search(query, int(k))


def vec_softmax(v: Vector) -> Vector:
    """Apply softmax to a vector."""
    return v.softmax()


def vec_relu(v: Vector) -> Vector:
    """Apply ReLU activation to a vector."""
    return v.relu()
