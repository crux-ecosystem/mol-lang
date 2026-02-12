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

