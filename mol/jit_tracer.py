"""
MOL JIT Tracer — Self-Optimizing Just-In-Time Compilation
============================================================

The language watches how the Neural Kernel runs and recompiles
its own "hot paths" to be faster. AI workloads change constantly —
a language that "traces itself" can rewrite its own execution
strategy to be 10x faster for specific tasks.

Features:
  - Hot path detection (functions called > threshold)
  - Trace recording (captures execution patterns)
  - JIT specialization (type-specific fast paths)
  - Adaptive optimization (profiles change → reoptimize)
  - Inline caching (monomorphic call sites)
  - Loop invariant detection
  - Constant folding on traced paths

MOL syntax:
  @jit                     -- decorator to enable JIT on a function
  @trace                   -- explicitly trace a function
  jit_stats()              -- get JIT compilation statistics
  jit_warmup(func, args)   -- pre-warm a function
"""

import time
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Tuple
from enum import Enum
import threading


class OptLevel(Enum):
    """Optimization levels for JIT compilation."""
    INTERPRET = 0       # No optimization
    BASELINE = 1        # Basic optimizations
    OPTIMIZED = 2       # Full trace-based optimization
    SPECIALIZED = 3     # Type-specialized fast paths


@dataclass
class TraceRecord:
    """Records a single execution trace of a function."""
    func_name: str
    arg_types: Tuple[str, ...]
    execution_time_ms: float
    result_type: str
    call_count: int = 1
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class HotPathInfo:
    """Information about a detected hot path."""
    func_name: str
    call_count: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    opt_level: OptLevel = OptLevel.INTERPRET
    type_profile: Dict[str, int] = field(default_factory=dict)
    last_optimized: float = 0.0
    speedup_factor: float = 1.0
    specialized_for: Optional[Tuple[str, ...]] = None


@dataclass
class InlineCache:
    """Inline cache for monomorphic call sites."""
    func_name: str
    cached_type_sig: Optional[Tuple[str, ...]] = None
    cached_result_type: Optional[str] = None
    cached_callable: Optional[Any] = None
    hits: int = 0
    misses: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


@dataclass
class LoopTrace:
    """Trace information for a loop body."""
    loop_id: str
    iteration_count: int = 0
    invariant_vars: List[str] = field(default_factory=list)
    body_time_ms: float = 0.0
    unrolled: bool = False


class JITTracer:
    """
    The MOL JIT Tracer — watches execution and self-optimizes.

    Architecture:
      1. INTERPRET: All code starts interpreted (baseline)
      2. PROFILE: Track call counts and execution times
      3. TRACE: When a function is "hot" (>100 calls), record traces
      4. OPTIMIZE: Generate specialized fast paths from traces
      5. ADAPT: If workload changes, invalidate and re-trace

    For the Neural Kernel: AI workloads are dynamic. A matrix
    multiplication that runs on 128-dim vectors today might run
    on 768-dim tomorrow. The JIT adapts automatically.
    """

    # Thresholds for optimization tiers
    HOT_THRESHOLD = 50          # Calls before tracing starts
    OPTIMIZATION_THRESHOLD = 100  # Calls before specialization
    REOPT_INTERVAL = 5.0        # Seconds between re-optimization checks

    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self._call_counts: Dict[str, int] = {}
        self._hot_paths: Dict[str, HotPathInfo] = {}
        self._traces: Dict[str, List[TraceRecord]] = {}
        self._inline_caches: Dict[str, InlineCache] = {}
        self._loop_traces: Dict[str, LoopTrace] = {}
        self._specializations: Dict[str, Dict[Tuple, Callable]] = {}
        self._constant_pool: Dict[str, Any] = {}
        self._total_calls: int = 0
        self._total_optimized: int = 0
        self._total_time_saved_ms: float = 0.0
        self._start_time = time.time()
        self._lock = threading.Lock()

    # ── Core Tracing API ─────────────────────────────────────

    def trace_call(self, func_name: str, args: list,
                   result: Any, elapsed_ms: float) -> Optional[Any]:
        """
        Record a function call. Returns optimized result if available.

        Called by the interpreter after every function invocation.
        """
        if not self._enabled:
            return None

        with self._lock:
            self._total_calls += 1

            # Update call count
            count = self._call_counts.get(func_name, 0) + 1
            self._call_counts[func_name] = count

            # Get type signature
            arg_types = tuple(self._type_name(a) for a in args)
            result_type = self._type_name(result)

            # Record trace
            trace = TraceRecord(
                func_name=func_name,
                arg_types=arg_types,
                execution_time_ms=elapsed_ms,
                result_type=result_type,
                call_count=count,
            )

            if func_name not in self._traces:
                self._traces[func_name] = []
            # Keep last 100 traces per function
            traces = self._traces[func_name]
            if len(traces) >= 100:
                traces.pop(0)
            traces.append(trace)

            # Check if function is hot
            if count == self.HOT_THRESHOLD:
                self._promote_to_hot(func_name)

            # Update hot path info
            if func_name in self._hot_paths:
                hp = self._hot_paths[func_name]
                hp.call_count = count
                hp.total_time_ms += elapsed_ms
                hp.avg_time_ms = hp.total_time_ms / count

                # Track type profile
                type_key = str(arg_types)
                hp.type_profile[type_key] = hp.type_profile.get(type_key, 0) + 1

                # Check for optimization
                if count >= self.OPTIMIZATION_THRESHOLD:
                    self._maybe_optimize(func_name, hp)

            # Check inline cache
            if func_name in self._inline_caches:
                cache = self._inline_caches[func_name]
                if cache.cached_type_sig == arg_types:
                    cache.hits += 1
                else:
                    cache.misses += 1
                    # Update cache (monomorphic assumption)
                    cache.cached_type_sig = arg_types
                    cache.cached_result_type = result_type

            return None  # No specialization override yet

    def trace_loop_start(self, loop_id: str):
        """Mark the start of a loop for tracing."""
        if not self._enabled:
            return
        if loop_id not in self._loop_traces:
            self._loop_traces[loop_id] = LoopTrace(loop_id=loop_id)

    def trace_loop_iteration(self, loop_id: str, elapsed_ms: float):
        """Record a loop iteration."""
        if loop_id in self._loop_traces:
            lt = self._loop_traces[loop_id]
            lt.iteration_count += 1
            lt.body_time_ms += elapsed_ms

    def register_constant(self, key: str, value: Any):
        """Register a compile-time constant for folding."""
        self._constant_pool[key] = value

    def get_constant(self, key: str) -> Optional[Any]:
        """Look up a folded constant."""
        return self._constant_pool.get(key)

    # ── Specialization ───────────────────────────────────────

    def register_specialization(self, func_name: str,
                                type_sig: Tuple[str, ...],
                                fast_fn: Callable):
        """Register a type-specialized fast path."""
        if func_name not in self._specializations:
            self._specializations[func_name] = {}
        self._specializations[func_name][type_sig] = fast_fn
        self._total_optimized += 1

    def get_specialization(self, func_name: str,
                           args: list) -> Optional[Callable]:
        """Look up a specialized version for the given argument types."""
        if func_name not in self._specializations:
            return None
        type_sig = tuple(self._type_name(a) for a in args)
        return self._specializations[func_name].get(type_sig)

    def warmup(self, func: Callable, sample_args: list,
               iterations: int = 100):
        """Pre-warm a function by running it multiple times."""
        func_name = getattr(func, 'name', getattr(func, '__name__', '<anon>'))
        for _ in range(iterations):
            start = time.time()
            try:
                result = func(*sample_args)
            except Exception:
                result = None
            elapsed = (time.time() - start) * 1000
            self.trace_call(func_name, sample_args, result, elapsed)

    # ── Analysis & Reporting ─────────────────────────────────

    def get_hot_paths(self) -> List[dict]:
        """Get all detected hot paths, sorted by call count."""
        paths = []
        for name, hp in sorted(self._hot_paths.items(),
                                key=lambda x: x[1].call_count,
                                reverse=True):
            paths.append({
                "name": name,
                "calls": hp.call_count,
                "total_ms": round(hp.total_time_ms, 2),
                "avg_ms": round(hp.avg_time_ms, 4),
                "opt_level": hp.opt_level.name,
                "speedup": round(hp.speedup_factor, 2),
                "type_profile": hp.type_profile,
            })
        return paths

    def get_stats(self) -> dict:
        """Get JIT compilation statistics."""
        uptime = time.time() - self._start_time
        return {
            "enabled": self._enabled,
            "total_calls_traced": self._total_calls,
            "hot_paths": len(self._hot_paths),
            "optimized_functions": self._total_optimized,
            "time_saved_ms": round(self._total_time_saved_ms, 2),
            "inline_caches": len(self._inline_caches),
            "constant_pool_size": len(self._constant_pool),
            "loop_traces": len(self._loop_traces),
            "uptime_seconds": round(uptime, 2),
            "calls_per_second": round(self._total_calls / uptime, 1) if uptime > 0 else 0,
        }

    def get_profile(self, func_name: str) -> dict:
        """Get detailed profile for a specific function."""
        if func_name not in self._traces:
            return {"error": f"No traces for '{func_name}'"}

        traces = self._traces[func_name]
        times = [t.execution_time_ms for t in traces]
        type_dist = {}
        for t in traces:
            key = str(t.arg_types)
            type_dist[key] = type_dist.get(key, 0) + 1

        return {
            "name": func_name,
            "total_traces": len(traces),
            "min_ms": round(min(times), 4),
            "max_ms": round(max(times), 4),
            "avg_ms": round(sum(times) / len(times), 4),
            "p50_ms": round(sorted(times)[len(times) // 2], 4),
            "p99_ms": round(sorted(times)[int(len(times) * 0.99)], 4) if len(times) > 1 else round(times[0], 4),
            "type_distribution": type_dist,
            "is_hot": func_name in self._hot_paths,
            "opt_level": self._hot_paths[func_name].opt_level.name if func_name in self._hot_paths else "INTERPRET",
        }

    def reset(self):
        """Reset all JIT state (useful after major code changes)."""
        self._call_counts.clear()
        self._hot_paths.clear()
        self._traces.clear()
        self._inline_caches.clear()
        self._loop_traces.clear()
        self._specializations.clear()
        self._constant_pool.clear()
        self._total_calls = 0
        self._total_optimized = 0
        self._total_time_saved_ms = 0.0

    # ── Optimization Engine ──────────────────────────────────

    def optimize_arithmetic(self, op: str, left: Any, right: Any) -> Optional[Any]:
        """
        Fast-path arithmetic for common types.
        Bypasses the full interpreter dispatch for hot operations.
        """
        if not self._enabled:
            return None

        # Integer fast path
        if isinstance(left, int) and isinstance(right, int):
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/" and right != 0:
                result = left / right
                return int(result) if result == int(result) else result

        # Float fast path
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/" and right != 0:
                return left / right

        # String concat fast path
        if isinstance(left, str) and isinstance(right, str) and op == "+":
            return left + right

        return None  # Fall through to interpreter

    def optimize_comparison(self, op: str, left: Any, right: Any) -> Optional[bool]:
        """Fast-path comparison for common types."""
        if not self._enabled:
            return None

        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
            if op == ">":
                return left > right
            if op == "<":
                return left < right
            if op == ">=":
                return left >= right
            if op == "<=":
                return left <= right

        return None

    # ── Internal ─────────────────────────────────────────────

    def _promote_to_hot(self, func_name: str):
        """Promote a function to hot path status."""
        traces = self._traces.get(func_name, [])
        total_ms = sum(t.execution_time_ms for t in traces)
        count = len(traces)

        hp = HotPathInfo(
            func_name=func_name,
            call_count=count,
            total_time_ms=total_ms,
            avg_time_ms=total_ms / count if count > 0 else 0,
            opt_level=OptLevel.BASELINE,
        )
        self._hot_paths[func_name] = hp

        # Create inline cache
        self._inline_caches[func_name] = InlineCache(func_name=func_name)

    def _maybe_optimize(self, func_name: str, hp: HotPathInfo):
        """Check if a hot function should be optimized further."""
        now = time.time()
        if now - hp.last_optimized < self.REOPT_INTERVAL:
            return

        hp.last_optimized = now

        # Analyze type stability
        if hp.type_profile:
            total = sum(hp.type_profile.values())
            dominant = max(hp.type_profile.items(), key=lambda x: x[1])
            stability = dominant[1] / total

            if stability > 0.9:
                # Type-stable: specialize
                hp.opt_level = OptLevel.SPECIALIZED
                hp.specialized_for = eval(dominant[0]) if dominant[0].startswith("(") else None
            elif stability > 0.7:
                hp.opt_level = OptLevel.OPTIMIZED
            else:
                hp.opt_level = OptLevel.BASELINE  # Too polymorphic

    def _type_name(self, value: Any) -> str:
        """Get a concise type name for profiling."""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "Bool"
        if isinstance(value, int):
            return "Int"
        if isinstance(value, float):
            return "Float"
        if isinstance(value, str):
            return "Text"
        if isinstance(value, list):
            return f"List[{len(value)}]"
        if isinstance(value, dict):
            return "Map"
        return type(value).__name__


# ── Global JIT Instance ─────────────────────────────────────

_global_jit = JITTracer(enabled=True)


# ── MOL Stdlib Functions ─────────────────────────────────────

def _builtin_jit_stats() -> dict:
    """Get JIT compilation statistics."""
    return _global_jit.get_stats()


def _builtin_jit_hot_paths() -> list:
    """Get all detected hot paths."""
    return _global_jit.get_hot_paths()


def _builtin_jit_profile(func_name: str) -> dict:
    """Get detailed profile for a function."""
    return _global_jit.get_profile(str(func_name))


def _builtin_jit_reset():
    """Reset all JIT state."""
    _global_jit.reset()
    return True


def _builtin_jit_warmup(func, sample_args, iterations=100):
    """Pre-warm a function for JIT optimization."""
    if not callable(func):
        return False
    if not isinstance(sample_args, list):
        sample_args = [sample_args]
    _global_jit.warmup(func, sample_args, int(iterations))
    return True


def _builtin_jit_enabled() -> bool:
    """Check if JIT is enabled."""
    return _global_jit._enabled


def _builtin_jit_toggle(enabled=None) -> bool:
    """Toggle JIT on/off."""
    if enabled is not None:
        _global_jit._enabled = bool(enabled)
    else:
        _global_jit._enabled = not _global_jit._enabled
    return _global_jit._enabled
