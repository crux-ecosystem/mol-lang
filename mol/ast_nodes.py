"""
MOL AST (Abstract Syntax Tree) Node Definitions
=================================================

Every construct in MOL is represented as a node in the AST.
The interpreter walks this tree using the Visitor pattern.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


# ── Base ─────────────────────────────────────────────────────
@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    line: int = 0
    column: int = 0


# ── Program ──────────────────────────────────────────────────
@dataclass
class Program(ASTNode):
    statements: list = field(default_factory=list)


# ── Literals ─────────────────────────────────────────────────
@dataclass
class NumberLiteral(ASTNode):
    value: float = 0.0


@dataclass
class StringLiteral(ASTNode):
    value: str = ""


@dataclass
class BoolLiteral(ASTNode):
    value: bool = False


@dataclass
class NullLiteral(ASTNode):
    pass


@dataclass
class ListLiteral(ASTNode):
    elements: list = field(default_factory=list)


@dataclass
class MapLiteral(ASTNode):
    pairs: list = field(default_factory=list)  # list of (key, value)


# ── Variables ────────────────────────────────────────────────
@dataclass
class VarRef(ASTNode):
    name: str = ""


@dataclass
class DeclareVar(ASTNode):
    name: str = ""
    type_name: Optional[str] = None
    value: Any = None


@dataclass
class AssignVar(ASTNode):
    name: str = ""
    value: Any = None


# ── Expressions ──────────────────────────────────────────────
@dataclass
class BinaryOp(ASTNode):
    op: str = ""
    left: Any = None
    right: Any = None


@dataclass
class UnaryOp(ASTNode):
    op: str = ""
    operand: Any = None


@dataclass
class Comparison(ASTNode):
    op: str = ""
    left: Any = None
    right: Any = None


@dataclass
class LogicalOp(ASTNode):
    op: str = ""    # "and", "or"
    left: Any = None
    right: Any = None


@dataclass
class NotOp(ASTNode):
    operand: Any = None


@dataclass
class Group(ASTNode):
    expr: Any = None


# ── Access ───────────────────────────────────────────────────
@dataclass
class FieldAccess(ASTNode):
    obj: Any = None
    field_name: str = ""


@dataclass
class IndexAccess(ASTNode):
    obj: Any = None
    index: Any = None


@dataclass
class MethodCall(ASTNode):
    obj: Any = None
    method: str = ""
    args: list = field(default_factory=list)


# ── Functions ────────────────────────────────────────────────
@dataclass
class FuncDef(ASTNode):
    name: str = ""
    params: list = field(default_factory=list)   # list of (name, type_or_None)
    body: list = field(default_factory=list)


@dataclass
class FuncCall(ASTNode):
    name: str = ""
    args: list = field(default_factory=list)


@dataclass
class ReturnStmt(ASTNode):
    value: Any = None


# ── Control Flow ─────────────────────────────────────────────
@dataclass
class IfStmt(ASTNode):
    condition: Any = None
    body: list = field(default_factory=list)
    elif_clauses: list = field(default_factory=list)   # list of (condition, body)
    else_body: Optional[list] = None


@dataclass
class WhileStmt(ASTNode):
    condition: Any = None
    body: list = field(default_factory=list)


@dataclass
class ForStmt(ASTNode):
    var_name: str = ""
    iterable: Any = None
    body: list = field(default_factory=list)


# ── Show (print) ────────────────────────────────────────────
@dataclass
class ShowStmt(ASTNode):
    value: Any = None


# ── Domain Specific ─────────────────────────────────────────
@dataclass
class TriggerStmt(ASTNode):
    event: Any = None


@dataclass
class LinkStmt(ASTNode):
    source: Any = None
    target: Any = None


@dataclass
class ProcessStmt(ASTNode):
    target: Any = None
    with_expr: Any = None


@dataclass
class AccessStmt(ASTNode):
    resource: Any = None


@dataclass
class SyncStmt(ASTNode):
    stream: Any = None


@dataclass
class EvolveStmt(ASTNode):
    node: Any = None


@dataclass
class EmitStmt(ASTNode):
    data: Any = None


@dataclass
class ListenStmt(ASTNode):
    event: Any = None
    body: list = field(default_factory=list)


@dataclass
class BlockStmt(ASTNode):
    body: list = field(default_factory=list)


@dataclass
class ExprStmt(ASTNode):
    expr: Any = None


# ── Pipeline & Guard (v0.2.0) ───────────────────────────────
@dataclass
class PipeChain(ASTNode):
    """A chain of pipe operations: a |> b |> c"""
    stages: list = field(default_factory=list)


@dataclass
class GuardStmt(ASTNode):
    """Guard assertion: guard expr or guard expr : "msg" """
    condition: Any = None
    message: Optional[str] = None


@dataclass
class PipelineDef(ASTNode):
    """Named pipeline definition with auto-tracing."""
    name: str = ""
    params: list = field(default_factory=list)
    body: list = field(default_factory=list)


# ── Module System (v0.5.0) ──────────────────────────────────
@dataclass
class UseStmt(ASTNode):
    """Import a package or file.

    Forms:
      use "math"                → import all from built-in math package
      use "math" : sin, cos     → import specific symbols
      use "./utils.mol"         → import local .mol file
      use "pkg" as P            → import with alias (namespace)
    """
    module: str = ""
    symbols: list = field(default_factory=list)   # empty = import all
    alias: Optional[str] = None                    # 'as' alias


# ── v0.6.0 Power Features ───────────────────────────────────

# ── Pattern Matching ─────────────────────────────────────────
@dataclass
class MatchExpr(ASTNode):
    """Pattern matching: match expr with | pattern -> body end"""
    subject: Any = None
    arms: list = field(default_factory=list)  # list of MatchArm

@dataclass
class MatchArm(ASTNode):
    """A single arm:  | pattern -> body"""
    pattern: Any = None    # MatchPattern node
    guard: Any = None      # optional 'when' guard expression
    body: list = field(default_factory=list)

@dataclass
class MatchPattern(ASTNode):
    """Pattern node — literal, binding, wildcard, list, map, or type."""
    kind: str = ""         # "literal", "binding", "wildcard", "list", "map", "type", "or"
    value: Any = None      # literal value, binding name, type name, etc.
    children: list = field(default_factory=list)  # sub-patterns for list/map/or


# ── Error Handling ───────────────────────────────────────────
@dataclass
class TryRescue(ASTNode):
    """try ... rescue [name] ... ensure ... end"""
    body: list = field(default_factory=list)
    rescue_name: Optional[str] = None      # variable name for error
    rescue_body: list = field(default_factory=list)
    ensure_body: list = field(default_factory=list)


# ── Lambda Expression ────────────────────────────────────────
@dataclass
class LambdaExpr(ASTNode):
    """fn(x, y) -> expr   (anonymous function)"""
    params: list = field(default_factory=list)  # list of param names (strings)
    body: Any = None  # single expression


# ── String Interpolation ────────────────────────────────────
@dataclass
class InterpolatedString(ASTNode):
    """f"Hello {name}, you have {count} items" """
    parts: list = field(default_factory=list)  # list of str | ASTNode


# ── Destructuring Assignment ────────────────────────────────
@dataclass
class DestructureList(ASTNode):
    """let [a, b, c] be expr"""
    names: list = field(default_factory=list)  # list of str (or "_" for skip)
    rest: Optional[str] = None                  # ...rest capture
    value: Any = None

@dataclass
class DestructureMap(ASTNode):
    """let {x, y, z} be expr"""
    keys: list = field(default_factory=list)    # list of str
    value: Any = None


# ── Null Coalescing Operator ────────────────────────────────
@dataclass
class NullCoalesce(ASTNode):
    """expr ?? default — returns default if expr is null"""
    left: Any = None
    right: Any = None


# ── Built-in Test Block ─────────────────────────────────────
@dataclass
class TestBlock(ASTNode):
    """test "description" do ... end"""
    description: str = ""
    body: list = field(default_factory=list)


# ── Chained Comparison (v0.6.0) ─────────────────────────────
@dataclass
class ChainedComparison(ASTNode):
    """0 < x < 100 — chained comparison without repeating x"""
    operands: list = field(default_factory=list)  # [expr, expr, expr, ...]
    ops: list = field(default_factory=list)        # ["<", "<", ...]


# ── Default Parameters (v0.6.0) ─────────────────────────────
# Handled through param tuple expansion: (name, type, default)


# ── Concurrency (v0.7.0) ────────────────────────────────────
@dataclass
class SpawnExpr(ASTNode):
    """spawn do ... end — run a block in a background task"""
    body: list = field(default_factory=list)


@dataclass
class AwaitExpr(ASTNode):
    """await expr — wait for a spawned task to complete"""
    expr: object = None

