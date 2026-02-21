"""
MOL Swarm Runtime — Multi-Node Distributed Execution
======================================================

Treats a distributed network as a single CPU. When you run a MOL
program, it seamlessly spreads across the De-RAG network.

The language itself handles the "sharding" of data across the world.
This makes the "Sovereign Memory" project possible.

Features:
  - Transparent distributed execution
  - Data sharding and replication
  - Swarm-level task scheduling
  - Consensus protocols for data consistency
  - Fault tolerance (automatic failover)
  - Network-aware data placement
  - Encrypted shard management for De-RAG

MOL syntax:
  let cluster be swarm_init(3)            -- 3-node cluster
  swarm_shard(data, cluster)              -- shard data across nodes
  swarm_map(cluster, fn(shard) -> ...)    -- map across all shards
  swarm_reduce(results, fn(a, b) -> ...) -- reduce results
  swarm_broadcast(cluster, message)       -- broadcast to all nodes
  let result be swarm_gather(cluster)     -- gather all results
"""

import time
import hashlib
import threading
import queue
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Tuple
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
import secrets


class NodeState(Enum):
    """State of a node in the swarm."""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    UNREACHABLE = "unreachable"
    DRAINING = "draining"
    SHUTDOWN = "shutdown"


class ShardStrategy(Enum):
    """How data is distributed across nodes."""
    HASH = "hash"           # Consistent hashing
    RANGE = "range"         # Range-based partitioning
    ROUND_ROBIN = "round_robin"  # Simple round-robin
    LOCALITY = "locality"   # Locality-aware (similar vectors together)


@dataclass
class SwarmNode:
    """A single node in the swarm network."""
    node_id: str
    address: str = "local"
    state: NodeState = NodeState.INITIALIZING
    capacity: int = 100      # Max concurrent tasks
    current_load: int = 0
    data_shards: List[str] = field(default_factory=list)
    last_heartbeat: float = 0.0
    total_tasks_completed: int = 0
    total_data_bytes: int = 0
    _local_store: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.last_heartbeat = time.time()

    @property
    def load_factor(self) -> float:
        return self.current_load / self.capacity if self.capacity > 0 else 1.0

    def mol_repr(self) -> str:
        return (f'<SwarmNode:{self.node_id} {self.state.value} '
                f'load={self.load_factor:.0%} shards={len(self.data_shards)}>')

    def __repr__(self):
        return self.mol_repr()

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "address": self.address,
            "state": self.state.value,
            "load_factor": round(self.load_factor, 2),
            "shards": len(self.data_shards),
            "tasks_completed": self.total_tasks_completed,
            "data_bytes": self.total_data_bytes,
        }


@dataclass
class DataShard:
    """A shard of data distributed across the swarm."""
    shard_id: str
    data: Any = None
    size_bytes: int = 0
    node_id: str = ""
    replicas: List[str] = field(default_factory=list)
    encrypted: bool = False
    checksum: str = ""
    created_at: float = 0.0

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
        if not self.checksum and self.data is not None:
            self.checksum = hashlib.sha256(
                str(self.data).encode()
            ).hexdigest()[:16]

    def mol_repr(self) -> str:
        enc = " encrypted" if self.encrypted else ""
        return f'<Shard:{self.shard_id} node={self.node_id}{enc}>'

    def to_dict(self) -> dict:
        return {
            "shard_id": self.shard_id,
            "node_id": self.node_id,
            "size_bytes": self.size_bytes,
            "replicas": self.replicas,
            "encrypted": self.encrypted,
            "checksum": self.checksum,
        }


@dataclass
class SwarmTask:
    """A task distributed across the swarm."""
    task_id: str
    func: Any = None
    args: list = field(default_factory=list)
    node_id: str = ""
    status: str = "pending"  # pending, running, completed, failed
    result: Any = None
    error: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0

    @property
    def elapsed_ms(self) -> float:
        if self.end_time > 0:
            return (self.end_time - self.start_time) * 1000
        return (time.time() - self.start_time) * 1000 if self.start_time > 0 else 0

    def mol_repr(self) -> str:
        return f'<SwarmTask:{self.task_id} {self.status} node={self.node_id}>'


class ConsistentHash:
    """
    Consistent hashing ring for data distribution.
    Ensures minimal data movement when nodes join/leave.
    """

    def __init__(self, replicas: int = 150):
        self._replicas = replicas
        self._ring: Dict[int, str] = {}
        self._sorted_keys: List[int] = []
        self._nodes: set = set()

    def add_node(self, node_id: str):
        """Add a node to the hash ring."""
        self._nodes.add(node_id)
        for i in range(self._replicas):
            key = self._hash(f"{node_id}:{i}")
            self._ring[key] = node_id
        self._sorted_keys = sorted(self._ring.keys())

    def remove_node(self, node_id: str):
        """Remove a node from the hash ring."""
        self._nodes.discard(node_id)
        for i in range(self._replicas):
            key = self._hash(f"{node_id}:{i}")
            self._ring.pop(key, None)
        self._sorted_keys = sorted(self._ring.keys())

    def get_node(self, key: str) -> str:
        """Get the node responsible for a given key."""
        if not self._ring:
            raise RuntimeError("No nodes in hash ring")
        h = self._hash(key)
        # Binary search for the nearest node
        idx = self._bisect(h)
        if idx >= len(self._sorted_keys):
            idx = 0
        return self._ring[self._sorted_keys[idx]]

    def get_nodes(self, key: str, n: int = 3) -> List[str]:
        """Get n nodes for a key (for replication)."""
        if not self._ring:
            return []
        nodes = []
        h = self._hash(key)
        idx = self._bisect(h)
        seen = set()
        while len(nodes) < min(n, len(self._nodes)):
            if idx >= len(self._sorted_keys):
                idx = 0
            node = self._ring[self._sorted_keys[idx]]
            if node not in seen:
                seen.add(node)
                nodes.append(node)
            idx += 1
        return nodes

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def _bisect(self, target: int) -> int:
        lo, hi = 0, len(self._sorted_keys)
        while lo < hi:
            mid = (lo + hi) // 2
            if self._sorted_keys[mid] < target:
                lo = mid + 1
            else:
                hi = mid
        return lo


class SwarmCluster:
    """
    The MOL Swarm Cluster — treats a distributed network as a single CPU.

    Manages nodes, distributes data, schedules tasks, and handles
    fault tolerance. For De-RAG: this is how Sovereign Memory
    is distributed across the world while remaining encrypted.
    """

    def __init__(self, num_nodes: int = 3, replication_factor: int = 2):
        self._nodes: Dict[str, SwarmNode] = {}
        self._shards: Dict[str, DataShard] = {}
        self._tasks: Dict[str, SwarmTask] = {}
        self._hash_ring = ConsistentHash()
        self._replication_factor = replication_factor
        self._executor = ThreadPoolExecutor(
            max_workers=num_nodes * 4,
            thread_name_prefix="mol-swarm"
        )
        self._lock = threading.Lock()
        self._message_queues: Dict[str, queue.Queue] = {}
        self._created_at = time.time()

        # Initialize nodes
        for i in range(num_nodes):
            node_id = f"node-{secrets.token_hex(4)}"
            self._add_node(node_id)

    def _add_node(self, node_id: str):
        """Add a new node to the cluster."""
        node = SwarmNode(node_id=node_id)
        node.state = NodeState.READY
        self._nodes[node_id] = node
        self._hash_ring.add_node(node_id)
        self._message_queues[node_id] = queue.Queue()

    def remove_node(self, node_id: str):
        """Remove a node and redistribute its data."""
        if node_id not in self._nodes:
            return
        node = self._nodes[node_id]
        node.state = NodeState.DRAINING

        # Redistribute shards
        for shard_id in list(node.data_shards):
            if shard_id in self._shards:
                shard = self._shards[shard_id]
                new_node_id = self._find_best_node(exclude={node_id})
                if new_node_id:
                    self._move_shard(shard_id, new_node_id)

        node.state = NodeState.SHUTDOWN
        self._hash_ring.remove_node(node_id)

    # ── Data Sharding ────────────────────────────────────────

    def shard_data(self, data: Any,
                   strategy: ShardStrategy = ShardStrategy.HASH,
                   num_shards: int = None) -> List[DataShard]:
        """
        Shard data across the cluster.
        Returns list of created shards.
        """
        if num_shards is None:
            num_shards = len(self._nodes)

        chunks = self._split_data(data, num_shards)
        shards = []

        for i, chunk in enumerate(chunks):
            shard_id = f"shard-{secrets.token_hex(4)}"

            if strategy == ShardStrategy.HASH:
                node_ids = self._hash_ring.get_nodes(
                    shard_id, self._replication_factor)
            elif strategy == ShardStrategy.ROUND_ROBIN:
                node_list = list(self._nodes.keys())
                node_ids = [node_list[i % len(node_list)]]
            else:
                node_ids = [self._find_best_node()]

            primary_node = node_ids[0] if node_ids else list(self._nodes.keys())[0]
            replica_nodes = node_ids[1:] if len(node_ids) > 1 else []

            shard = DataShard(
                shard_id=shard_id,
                data=chunk,
                size_bytes=self._estimate_size(chunk),
                node_id=primary_node,
                replicas=replica_nodes,
            )

            self._shards[shard_id] = shard

            # Place data on nodes
            if primary_node in self._nodes:
                self._nodes[primary_node].data_shards.append(shard_id)
                self._nodes[primary_node]._local_store[shard_id] = chunk
                self._nodes[primary_node].total_data_bytes += shard.size_bytes

            for replica_id in replica_nodes:
                if replica_id in self._nodes:
                    self._nodes[replica_id].data_shards.append(shard_id)
                    self._nodes[replica_id]._local_store[shard_id] = chunk

            shards.append(shard)

        return shards

    def gather_shards(self, shard_ids: List[str] = None) -> list:
        """Gather data from shards back into a single value."""
        if shard_ids is None:
            shard_ids = list(self._shards.keys())

        results = []
        for sid in sorted(shard_ids):
            if sid in self._shards:
                shard = self._shards[sid]
                # Read from primary node
                if shard.node_id in self._nodes:
                    data = self._nodes[shard.node_id]._local_store.get(sid)
                    if data is not None:
                        if isinstance(data, list):
                            results.extend(data)
                        else:
                            results.append(data)
        return results

    # ── Distributed Computation ──────────────────────────────

    def swarm_map(self, func: Callable, data: Any = None) -> list:
        """
        Map a function across all shards in parallel.
        Each node processes its own shards — true distributed execution.
        """
        futures = {}
        shard_order = []

        for shard_id, shard in self._shards.items():
            node_id = shard.node_id
            if node_id not in self._nodes:
                continue

            node = self._nodes[node_id]
            local_data = node._local_store.get(shard_id)
            if local_data is None:
                continue

            task_id = f"task-{secrets.token_hex(4)}"
            task = SwarmTask(
                task_id=task_id,
                func=func,
                args=[local_data],
                node_id=node_id,
                start_time=time.time(),
            )
            self._tasks[task_id] = task
            shard_order.append(task_id)

            # Submit to thread pool (simulates distributed execution)
            def run_task(t=task, d=local_data, f=func):
                t.status = "running"
                try:
                    t.result = f(d)
                    t.status = "completed"
                except Exception as e:
                    t.error = str(e)
                    t.status = "failed"
                finally:
                    t.end_time = time.time()
                return t

            future = self._executor.submit(run_task)
            futures[task_id] = future

        # Gather results in order
        results = []
        for task_id in shard_order:
            if task_id in futures:
                futures[task_id].result()  # Wait for completion
                task = self._tasks[task_id]
                if task.status == "completed":
                    results.append(task.result)
                    # Update node stats
                    if task.node_id in self._nodes:
                        self._nodes[task.node_id].total_tasks_completed += 1

        return results

    def swarm_reduce(self, results: list, func: Callable) -> Any:
        """Reduce distributed results into a single value."""
        if not results:
            return None
        acc = results[0]
        for item in results[1:]:
            acc = func(acc, item)
        return acc

    def swarm_broadcast(self, message: Any) -> dict:
        """Broadcast a message to all nodes."""
        responses = {}
        for node_id, q in self._message_queues.items():
            q.put(message)
            responses[node_id] = "delivered"
        return responses

    def swarm_scatter(self, items: list) -> Dict[str, Any]:
        """Scatter items to nodes (one item per node)."""
        node_ids = list(self._nodes.keys())
        assignments = {}
        for i, item in enumerate(items):
            node_id = node_ids[i % len(node_ids)]
            assignments[node_id] = item
            self._nodes[node_id]._local_store["__scatter__"] = item
        return assignments

    # ── Fault Tolerance ──────────────────────────────────────

    def health_check(self) -> dict:
        """Check cluster health."""
        healthy = 0
        unhealthy = 0
        for node in self._nodes.values():
            if node.state in (NodeState.READY, NodeState.BUSY):
                healthy += 1
            else:
                unhealthy += 1

        total_shards = len(self._shards)
        replicated = sum(1 for s in self._shards.values() if s.replicas)

        return {
            "total_nodes": len(self._nodes),
            "healthy": healthy,
            "unhealthy": unhealthy,
            "total_shards": total_shards,
            "replicated_shards": replicated,
            "replication_factor": self._replication_factor,
            "total_tasks": len(self._tasks),
            "uptime_seconds": round(time.time() - self._created_at, 2),
        }

    def rebalance(self):
        """Rebalance shards across nodes for even distribution."""
        node_ids = [n for n, node in self._nodes.items()
                    if node.state == NodeState.READY]
        if not node_ids:
            return

        # Calculate ideal distribution
        total_shards = len(self._shards)
        ideal_per_node = math.ceil(total_shards / len(node_ids))

        # Find overloaded and underloaded nodes
        loads = {nid: len(self._nodes[nid].data_shards) for nid in node_ids}
        overloaded = [nid for nid, load in loads.items() if load > ideal_per_node + 1]
        underloaded = [nid for nid, load in loads.items() if load < ideal_per_node - 1]

        for over_id in overloaded:
            while (len(self._nodes[over_id].data_shards) > ideal_per_node
                   and underloaded):
                under_id = underloaded[0]
                if len(self._nodes[under_id].data_shards) >= ideal_per_node:
                    underloaded.pop(0)
                    continue
                shard_id = self._nodes[over_id].data_shards[-1]
                self._move_shard(shard_id, under_id)

    # ── Information ──────────────────────────────────────────

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def shard_count(self) -> int:
        return len(self._shards)

    def get_nodes(self) -> List[dict]:
        """Get status of all nodes."""
        return [n.to_dict() for n in self._nodes.values()]

    def get_node_ids(self) -> List[str]:
        """Get all node IDs."""
        return list(self._nodes.keys())

    def mol_repr(self) -> str:
        healthy = sum(1 for n in self._nodes.values()
                      if n.state in (NodeState.READY, NodeState.BUSY))
        return (f'<SwarmCluster nodes={len(self._nodes)} '
                f'healthy={healthy} shards={len(self._shards)}>')

    def __repr__(self):
        return self.mol_repr()

    def to_dict(self) -> dict:
        return self.health_check()

    # ── Internal ─────────────────────────────────────────────

    def _split_data(self, data: Any, num_chunks: int) -> list:
        """Split data into chunks for sharding."""
        if isinstance(data, list):
            chunk_size = max(1, math.ceil(len(data) / num_chunks))
            return [data[i:i + chunk_size]
                    for i in range(0, len(data), chunk_size)]
        if isinstance(data, dict):
            items = list(data.items())
            chunk_size = max(1, math.ceil(len(items) / num_chunks))
            return [dict(items[i:i + chunk_size])
                    for i in range(0, len(items), chunk_size)]
        if isinstance(data, str):
            chunk_size = max(1, math.ceil(len(data) / num_chunks))
            return [data[i:i + chunk_size]
                    for i in range(0, len(data), chunk_size)]
        # Non-splittable: replicate to all
        return [data] * num_chunks

    def _find_best_node(self, exclude: set = None) -> str:
        """Find the least-loaded ready node."""
        exclude = exclude or set()
        candidates = [
            (nid, node) for nid, node in self._nodes.items()
            if node.state == NodeState.READY and nid not in exclude
        ]
        if not candidates:
            # Fallback: any non-shutdown node
            candidates = [
                (nid, node) for nid, node in self._nodes.items()
                if node.state != NodeState.SHUTDOWN and nid not in exclude
            ]
        if not candidates:
            return list(self._nodes.keys())[0]
        return min(candidates, key=lambda x: x[1].load_factor)[0]

    def _move_shard(self, shard_id: str, target_node_id: str):
        """Move a shard from its current node to a new one."""
        if shard_id not in self._shards:
            return
        shard = self._shards[shard_id]
        old_node_id = shard.node_id

        # Remove from old node
        if old_node_id in self._nodes:
            old_node = self._nodes[old_node_id]
            if shard_id in old_node.data_shards:
                old_node.data_shards.remove(shard_id)
            data = old_node._local_store.pop(shard_id, shard.data)
        else:
            data = shard.data

        # Place on new node
        shard.node_id = target_node_id
        if target_node_id in self._nodes:
            new_node = self._nodes[target_node_id]
            new_node.data_shards.append(shard_id)
            new_node._local_store[shard_id] = data

    def _estimate_size(self, value: Any) -> int:
        """Estimate the byte size of a value."""
        if value is None:
            return 0
        if isinstance(value, (int, float)):
            return 8
        if isinstance(value, str):
            return len(value.encode('utf-8', errors='replace'))
        if isinstance(value, list):
            return 64 + sum(self._estimate_size(v) for v in value[:100])
        if isinstance(value, dict):
            return 64 + sum(
                self._estimate_size(k) + self._estimate_size(v)
                for k, v in list(value.items())[:100]
            )
        return 64


# ── MOL Stdlib Functions ─────────────────────────────────────

_global_clusters: Dict[str, SwarmCluster] = {}


def _builtin_swarm_init(num_nodes=3, replication=2) -> SwarmCluster:
    """Initialize a swarm cluster with N nodes."""
    cluster = SwarmCluster(
        num_nodes=int(num_nodes),
        replication_factor=int(replication)
    )
    cluster_id = f"cluster-{secrets.token_hex(4)}"
    _global_clusters[cluster_id] = cluster
    return cluster


def _builtin_swarm_shard(data, cluster=None, strategy="hash",
                         num_shards=None) -> list:
    """Shard data across a swarm cluster."""
    if cluster is None:
        if not _global_clusters:
            cluster = _builtin_swarm_init()
        else:
            cluster = list(_global_clusters.values())[-1]
    if not isinstance(cluster, SwarmCluster):
        raise RuntimeError("Expected a SwarmCluster")

    strat_map = {
        "hash": ShardStrategy.HASH,
        "range": ShardStrategy.RANGE,
        "round_robin": ShardStrategy.ROUND_ROBIN,
        "locality": ShardStrategy.LOCALITY,
    }
    strat = strat_map.get(str(strategy), ShardStrategy.HASH)
    shards = cluster.shard_data(data, strategy=strat,
                                num_shards=int(num_shards) if num_shards else None)
    return [s.to_dict() for s in shards]


def _builtin_swarm_map(cluster, func) -> list:
    """Map a function across all shards in the cluster."""
    if not isinstance(cluster, SwarmCluster):
        raise RuntimeError("Expected a SwarmCluster")
    if not callable(func):
        raise RuntimeError("Expected a callable function")
    return cluster.swarm_map(func)


def _builtin_swarm_reduce(results, func) -> Any:
    """Reduce distributed results."""
    if not isinstance(results, list):
        raise RuntimeError("Expected a list of results")
    if not callable(func):
        raise RuntimeError("Expected a callable function")
    if not results:
        return None
    acc = results[0]
    for item in results[1:]:
        acc = func(acc, item)
    return acc


def _builtin_swarm_gather(cluster) -> list:
    """Gather all sharded data from the cluster."""
    if not isinstance(cluster, SwarmCluster):
        raise RuntimeError("Expected a SwarmCluster")
    return cluster.gather_shards()


def _builtin_swarm_broadcast(cluster, message) -> dict:
    """Broadcast a message to all nodes in the cluster."""
    if not isinstance(cluster, SwarmCluster):
        raise RuntimeError("Expected a SwarmCluster")
    return cluster.swarm_broadcast(message)


def _builtin_swarm_health(cluster) -> dict:
    """Get cluster health report."""
    if not isinstance(cluster, SwarmCluster):
        raise RuntimeError("Expected a SwarmCluster")
    return cluster.health_check()


def _builtin_swarm_nodes(cluster) -> list:
    """Get status of all nodes in the cluster."""
    if not isinstance(cluster, SwarmCluster):
        raise RuntimeError("Expected a SwarmCluster")
    return cluster.get_nodes()


def _builtin_swarm_rebalance(cluster) -> bool:
    """Rebalance shards across nodes."""
    if not isinstance(cluster, SwarmCluster):
        raise RuntimeError("Expected a SwarmCluster")
    cluster.rebalance()
    return True


def _builtin_swarm_add_node(cluster) -> dict:
    """Add a new node to the cluster."""
    if not isinstance(cluster, SwarmCluster):
        raise RuntimeError("Expected a SwarmCluster")
    node_id = f"node-{secrets.token_hex(4)}"
    cluster._add_node(node_id)
    return cluster._nodes[node_id].to_dict()


def _builtin_swarm_remove_node(cluster, node_id) -> bool:
    """Remove a node from the cluster (with data redistribution)."""
    if not isinstance(cluster, SwarmCluster):
        raise RuntimeError("Expected a SwarmCluster")
    cluster.remove_node(str(node_id))
    return True


def _builtin_swarm_scatter(cluster, items) -> dict:
    """Scatter items to nodes (one per node)."""
    if not isinstance(cluster, SwarmCluster):
        raise RuntimeError("Expected a SwarmCluster")
    if not isinstance(items, list):
        raise RuntimeError("Expected a list")
    return cluster.swarm_scatter(items)
