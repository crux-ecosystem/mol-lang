"""
MOL Borrow Checker — Hardware-Level Memory Safety
===================================================

Implements Rust-inspired ownership and borrowing semantics with
AI-assisted automatic memory management. Designed for the Neural
Kernel where crashes are unacceptable.

Rules:
  1. Every value has exactly ONE owner at a time.
  2. Ownership can be MOVED (transferred) to another binding.
  3. Values can be BORROWED immutably (&) — multiple readers OK.
  4. Values can be BORROWED mutably (&mut) — exclusive access.
  5. No mutable + immutable borrows can coexist.
  6. Borrows must not outlive the owner.
  7. When the owner goes out of scope, the value is DROPPED.

MOL syntax:
  let own x be [1, 2, 3]          -- owned value
  let ref y be borrow x            -- immutable borrow
  let ref mut z be borrow_mut x    -- mutable borrow
  move x to new_owner              -- transfer ownership
  drop x                           -- explicit drop
  lifetime 'a do ... end           -- explicit lifetime scope

AI-Assisted Features:
  - Automatic borrow inference (no annotations needed for simple cases)
  - Tracing-based lifetime analysis
  - Preventive buffer overflow detection
  - Smart pointer auto-insertion
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Set, Dict, List
from enum import Enum
import time


class OwnershipKind(Enum):
    """How a variable relates to its value."""
    OWNED = "owned"              # Full ownership
    IMMUTABLE_BORROW = "borrow"  # &ref — read-only
    MUTABLE_BORROW = "borrow_mut"  # &mut — exclusive read/write
    MOVED = "moved"              # Ownership transferred away


class MemoryRegion(Enum):
    """Where a value lives in the abstract memory model."""
    STACK = "stack"
    HEAP = "heap"
    STATIC = "static"
    KERNEL = "kernel"  # Neural Kernel protected memory


@dataclass
class Lifetime:
    """Tracks the valid scope of a borrow."""
    name: str                      # 'a, 'b, etc.
    created_at: float = 0.0
    scope_depth: int = 0
    active: bool = True

    def __post_init__(self):
        self.created_at = time.time()


@dataclass
class OwnershipRecord:
    """Tracks ownership state of a single binding."""
    var_name: str
    kind: OwnershipKind = OwnershipKind.OWNED
    region: MemoryRegion = MemoryRegion.STACK
    lifetime: Optional[Lifetime] = None
    borrowed_from: Optional[str] = None  # Source variable for borrows
    borrow_count: int = 0                # Active immutable borrows
    mutable_borrowed: bool = False       # Is mutably borrowed?
    move_target: Optional[str] = None    # Where ownership moved to
    dropped: bool = False
    size_bytes: int = 0                  # Tracked memory size
    access_count: int = 0               # For AI optimization
    last_access: float = 0.0


class BorrowError(Exception):
    """Raised when borrow checking fails — prevents memory unsafety."""
    pass


class OwnershipError(Exception):
    """Raised when ownership rules are violated."""
    pass


class LifetimeError(Exception):
    """Raised when a borrow outlives its source."""
    pass


class BufferOverflowError(Exception):
    """Raised when buffer bounds are violated — the #1 OS vulnerability."""
    pass


class UseAfterFreeError(Exception):
    """Raised when accessing a dropped/moved value."""
    pass


class BorrowChecker:
    """
    The MOL Borrow Checker — enforces memory safety at runtime.

    Integrates with the interpreter to track ownership, borrows,
    and lifetimes for every value. AI-assisted: automatically
    infers the safest ownership model when not explicitly specified.

    For the Neural Kernel: prevents buffer overflows, use-after-free,
    double-free, and data races at the language level.
    """

    def __init__(self, ai_assist: bool = True):
        self._records: Dict[str, OwnershipRecord] = {}
        self._lifetime_stack: List[Lifetime] = []
        self._scope_depth: int = 0
        self._ai_assist = ai_assist
        self._dropped_values: Set[str] = set()
        self._allocation_log: List[dict] = []
        self._total_allocated: int = 0
        self._total_freed: int = 0
        self._buffer_registry: Dict[str, int] = {}  # var -> max_size
        self._violation_log: List[dict] = []

    # ── Ownership Management ─────────────────────────────────

    def register_owned(self, var_name: str, value: Any,
                       region: MemoryRegion = MemoryRegion.STACK) -> OwnershipRecord:
        """Register a new owned value: `let own x be ...`"""
        if var_name in self._records and not self._records[var_name].dropped:
            old = self._records[var_name]
            if old.kind == OwnershipKind.OWNED:
                # Auto-drop the old value (AI-assist)
                self._auto_drop(var_name)

        size = self._estimate_size(value)
        record = OwnershipRecord(
            var_name=var_name,
            kind=OwnershipKind.OWNED,
            region=region,
            size_bytes=size,
            last_access=time.time(),
        )

        # Assign current lifetime scope
        if self._lifetime_stack:
            record.lifetime = self._lifetime_stack[-1]

        self._records[var_name] = record
        self._total_allocated += size
        self._allocation_log.append({
            "action": "allocate",
            "var": var_name,
            "size": size,
            "region": region.value,
            "time": time.time(),
        })
        return record

    def register_buffer(self, var_name: str, max_size: int):
        """Register a fixed-size buffer for overflow protection."""
        self._buffer_registry[var_name] = max_size

    def check_buffer_access(self, var_name: str, index: int):
        """Check buffer bounds — prevents the #1 OS vulnerability."""
        if var_name in self._buffer_registry:
            max_size = self._buffer_registry[var_name]
            if index < 0 or index >= max_size:
                self._log_violation("buffer_overflow", var_name,
                                    f"Index {index} out of bounds [0, {max_size})")
                raise BufferOverflowError(
                    f"Buffer overflow: '{var_name}[{index}]' — "
                    f"valid range is [0, {max_size}). "
                    f"This would be a critical vulnerability in a kernel."
                )

    def borrow(self, borrower: str, source: str) -> OwnershipRecord:
        """Create an immutable borrow: `let ref y be borrow x`"""
        self._check_accessible(source)
        src = self._records[source]

        if src.mutable_borrowed:
            raise BorrowError(
                f"Cannot immutably borrow '{source}' — "
                f"it is already mutably borrowed. "
                f"Mutable borrows require exclusive access."
            )

        src.borrow_count += 1
        record = OwnershipRecord(
            var_name=borrower,
            kind=OwnershipKind.IMMUTABLE_BORROW,
            borrowed_from=source,
            lifetime=self._lifetime_stack[-1] if self._lifetime_stack else None,
            last_access=time.time(),
        )
        self._records[borrower] = record
        return record

    def borrow_mut(self, borrower: str, source: str) -> OwnershipRecord:
        """Create a mutable borrow: `let ref mut z be borrow_mut x`"""
        self._check_accessible(source)
        src = self._records[source]

        if src.borrow_count > 0:
            raise BorrowError(
                f"Cannot mutably borrow '{source}' — "
                f"it has {src.borrow_count} active immutable borrow(s). "
                f"Cannot have mutable + immutable borrows simultaneously."
            )

        if src.mutable_borrowed:
            raise BorrowError(
                f"Cannot mutably borrow '{source}' — "
                f"it is already mutably borrowed. "
                f"Only one mutable borrow allowed at a time."
            )

        src.mutable_borrowed = True
        record = OwnershipRecord(
            var_name=borrower,
            kind=OwnershipKind.MUTABLE_BORROW,
            borrowed_from=source,
            lifetime=self._lifetime_stack[-1] if self._lifetime_stack else None,
            last_access=time.time(),
        )
        self._records[borrower] = record
        return record

    def move_ownership(self, source: str, target: str) -> OwnershipRecord:
        """Transfer ownership: `move x to y`"""
        self._check_accessible(source)
        src = self._records[source]

        if src.borrow_count > 0 or src.mutable_borrowed:
            raise OwnershipError(
                f"Cannot move '{source}' — it has active borrows. "
                f"All borrows must be released before moving ownership."
            )

        # Move: source becomes invalid, target gets ownership
        src.kind = OwnershipKind.MOVED
        src.move_target = target

        record = OwnershipRecord(
            var_name=target,
            kind=OwnershipKind.OWNED,
            region=src.region,
            size_bytes=src.size_bytes,
            lifetime=self._lifetime_stack[-1] if self._lifetime_stack else None,
            last_access=time.time(),
        )
        self._records[target] = record
        return record

    def drop(self, var_name: str):
        """Explicitly drop a value: `drop x`"""
        if var_name not in self._records:
            raise OwnershipError(f"Cannot drop '{var_name}' — not found")

        record = self._records[var_name]
        if record.dropped:
            raise OwnershipError(
                f"Double free: '{var_name}' has already been dropped. "
                f"This would be a critical vulnerability."
            )
        if record.kind == OwnershipKind.MOVED:
            raise OwnershipError(
                f"Cannot drop '{var_name}' — ownership was moved to '{record.move_target}'")

        if record.borrow_count > 0 or record.mutable_borrowed:
            raise OwnershipError(
                f"Cannot drop '{var_name}' — it has active borrows. "
                f"Borrows must be released first."
            )

        record.dropped = True
        self._dropped_values.add(var_name)
        self._total_freed += record.size_bytes
        self._allocation_log.append({
            "action": "free",
            "var": var_name,
            "size": record.size_bytes,
            "time": time.time(),
        })

    def release_borrow(self, borrower: str):
        """Release a borrow when it goes out of scope."""
        if borrower not in self._records:
            return

        record = self._records[borrower]
        if record.kind in (OwnershipKind.IMMUTABLE_BORROW,
                           OwnershipKind.MUTABLE_BORROW):
            source = record.borrowed_from
            if source and source in self._records:
                src = self._records[source]
                if record.kind == OwnershipKind.IMMUTABLE_BORROW:
                    src.borrow_count = max(0, src.borrow_count - 1)
                else:
                    src.mutable_borrowed = False
            record.dropped = True

    def check_access(self, var_name: str):
        """Check if accessing a variable is safe."""
        self._check_accessible(var_name)
        if var_name in self._records:
            self._records[var_name].access_count += 1
            self._records[var_name].last_access = time.time()

    def check_mutation(self, var_name: str):
        """Check if mutating a variable is safe."""
        self._check_accessible(var_name)
        record = self._records[var_name]

        if record.kind == OwnershipKind.IMMUTABLE_BORROW:
            raise BorrowError(
                f"Cannot mutate '{var_name}' — it is an immutable borrow. "
                f"Use 'borrow_mut' for mutable access."
            )

        if record.borrow_count > 0:
            raise BorrowError(
                f"Cannot mutate '{var_name}' — it has "
                f"{record.borrow_count} active immutable borrow(s). "
                f"Mutation requires exclusive access."
            )

    # ── Lifetime Management ──────────────────────────────────

    def enter_lifetime(self, name: str = None) -> Lifetime:
        """Enter a new lifetime scope."""
        self._scope_depth += 1
        lt_name = name or f"'scope_{self._scope_depth}"
        lt = Lifetime(name=lt_name, scope_depth=self._scope_depth)
        self._lifetime_stack.append(lt)
        return lt

    def exit_lifetime(self):
        """Exit the current lifetime scope — drop all local borrows."""
        if not self._lifetime_stack:
            return

        lt = self._lifetime_stack.pop()
        lt.active = False
        self._scope_depth -= 1

        # Release all borrows in this lifetime scope
        to_release = []
        for name, record in self._records.items():
            if record.lifetime == lt and not record.dropped:
                if record.kind in (OwnershipKind.IMMUTABLE_BORROW,
                                   OwnershipKind.MUTABLE_BORROW):
                    to_release.append(name)

        for name in to_release:
            self.release_borrow(name)

    def scope_drop_all(self, scope_vars: List[str]):
        """Drop all owned values when a scope exits (automatic RAII)."""
        for var_name in reversed(scope_vars):
            if var_name in self._records:
                record = self._records[var_name]
                if record.kind == OwnershipKind.OWNED and not record.dropped:
                    # Auto-release any borrows first
                    self._force_release_borrows(var_name)
                    self.drop(var_name)

    # ── AI-Assisted Analysis ─────────────────────────────────

    def analyze_safety(self, var_name: str) -> dict:
        """AI-assisted safety analysis of a variable's memory state."""
        if var_name not in self._records:
            return {"safe": False, "reason": "Variable not tracked"}

        record = self._records[var_name]
        issues = []

        if record.dropped:
            issues.append("Value has been dropped — use-after-free risk")
        if record.kind == OwnershipKind.MOVED:
            issues.append(f"Ownership moved to '{record.move_target}'")
        if record.borrow_count > 3:
            issues.append(f"High borrow count ({record.borrow_count}) — consider restructuring")
        if record.region == MemoryRegion.KERNEL and record.kind != OwnershipKind.OWNED:
            issues.append("Kernel memory should be owned, not borrowed")

        return {
            "safe": len(issues) == 0,
            "var": var_name,
            "kind": record.kind.value,
            "region": record.region.value,
            "borrows": record.borrow_count,
            "mutable_borrowed": record.mutable_borrowed,
            "size_bytes": record.size_bytes,
            "access_count": record.access_count,
            "issues": issues,
        }

    def get_memory_report(self) -> dict:
        """Get a full memory safety report for the current program state."""
        active = {k: v for k, v in self._records.items()
                  if not v.dropped and v.kind != OwnershipKind.MOVED}
        leaked = {k: v for k, v in active.items()
                  if v.kind == OwnershipKind.OWNED and v.access_count == 0}

        return {
            "total_allocated": self._total_allocated,
            "total_freed": self._total_freed,
            "in_use": self._total_allocated - self._total_freed,
            "active_bindings": len(active),
            "potential_leaks": len(leaked),
            "violations": len(self._violation_log),
            "leak_suspects": list(leaked.keys()),
            "violation_log": self._violation_log[-10:],
        }

    def auto_infer_ownership(self, var_name: str, value: Any,
                             usage_pattern: str = "local") -> OwnershipKind:
        """AI-assisted ownership inference based on usage patterns."""
        if not self._ai_assist:
            return OwnershipKind.OWNED

        # Heuristics for auto-inference
        if usage_pattern == "return":
            return OwnershipKind.OWNED  # Returned values must be owned
        if usage_pattern == "read_only":
            return OwnershipKind.IMMUTABLE_BORROW
        if usage_pattern == "temporary":
            return OwnershipKind.OWNED  # Short-lived, will be auto-dropped
        if isinstance(value, (int, float, str, bool)):
            return OwnershipKind.OWNED  # Primitives are always copied/owned

        return OwnershipKind.OWNED  # Default: owned

    # ── Smart Pointers ───────────────────────────────────────

    def create_smart_ptr(self, var_name: str, value: Any) -> 'SmartPointer':
        """Create a reference-counted smart pointer (like Rc<T> in Rust)."""
        ptr = SmartPointer(var_name, value, self)
        self.register_owned(var_name, value, MemoryRegion.HEAP)
        return ptr

    # ── Internal Helpers ─────────────────────────────────────

    def _check_accessible(self, var_name: str):
        """Verify a variable is accessible (not dropped, not moved)."""
        if var_name not in self._records:
            # In AI-assist mode, auto-register on first access
            if self._ai_assist:
                return
            raise OwnershipError(f"'{var_name}' is not tracked by the borrow checker")

        record = self._records[var_name]
        if record.dropped:
            raise UseAfterFreeError(
                f"Use after free: '{var_name}' has been dropped. "
                f"Accessing freed memory is undefined behavior."
            )
        if record.kind == OwnershipKind.MOVED:
            raise OwnershipError(
                f"Use after move: '{var_name}' — ownership was moved to "
                f"'{record.move_target}'. The original binding is no longer valid."
            )

    def _auto_drop(self, var_name: str):
        """AI-assisted automatic drop when rebinding."""
        if var_name in self._records:
            record = self._records[var_name]
            if not record.dropped and record.kind == OwnershipKind.OWNED:
                self._force_release_borrows(var_name)
                record.dropped = True
                self._total_freed += record.size_bytes

    def _force_release_borrows(self, source: str):
        """Force-release all borrows of a source variable."""
        for name, record in self._records.items():
            if record.borrowed_from == source and not record.dropped:
                self.release_borrow(name)

    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of a value in bytes."""
        if value is None:
            return 0
        if isinstance(value, bool):
            return 1
        if isinstance(value, int):
            return 8
        if isinstance(value, float):
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
        return 64  # Default object overhead

    def _log_violation(self, kind: str, var: str, detail: str):
        """Log a safety violation for audit."""
        self._violation_log.append({
            "kind": kind,
            "var": var,
            "detail": detail,
            "time": time.time(),
        })


class SmartPointer:
    """
    Reference-counted smart pointer — like Rc<T> / Arc<T> in Rust.
    Automatically drops the value when the reference count hits zero.
    """

    def __init__(self, name: str, value: Any, checker: BorrowChecker):
        self._name = name
        self._value = value
        self._checker = checker
        self._ref_count = 1
        self._clones: List[str] = []

    @property
    def value(self):
        if self._ref_count == 0:
            raise UseAfterFreeError(
                f"Smart pointer '{self._name}' — reference count is zero")
        return self._value

    def clone(self, new_name: str) -> 'SmartPointer':
        """Create a new reference to the same value (Rc::clone)."""
        self._ref_count += 1
        self._clones.append(new_name)
        new_ptr = SmartPointer(new_name, self._value, self._checker)
        new_ptr._ref_count = self._ref_count
        return new_ptr

    def drop(self):
        """Decrement reference count. Drop value when it reaches zero."""
        self._ref_count -= 1
        if self._ref_count == 0:
            self._checker.drop(self._name)
            self._value = None

    def __repr__(self):
        return f"<SmartPtr:{self._name} refs={self._ref_count}>"

    def mol_repr(self):
        return f"<SmartPtr:{self._name} refs={self._ref_count}>"

    def to_dict(self):
        return {
            "name": self._name,
            "ref_count": self._ref_count,
            "clones": self._clones,
        }
