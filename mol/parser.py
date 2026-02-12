"""
MOL Parser — Lark-based Lexer/Parser + AST Transformer
========================================================

Reads MOL source code, tokenizes it via Lark, and transforms
the parse tree into a clean AST using the nodes from ast_nodes.py.
"""

import os
from lark import Lark, Transformer, v_args, Token
from mol.ast_nodes import *

_GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "grammar.lark")


def _get_parser() -> Lark:
    """Create and return the Lark parser for MOL."""
    with open(_GRAMMAR_PATH, "r") as f:
        grammar = f.read()
    return Lark(
        grammar,
        parser="lalr",
        propagate_positions=True,
        maybe_placeholders=True,
    )


_parser = _get_parser()


# ── Transformer: parse-tree → AST ───────────────────────────
@v_args(inline=True)
class MOLTransformer(Transformer):
    """Transforms the Lark parse tree into our AST node objects."""

    def __default_token__(self, tok):
        return tok

    def _apply_meta(self, tree, result):
        """After transforming a tree, apply its meta (line/col) to the result AST node."""
        if isinstance(result, ASTNode) and hasattr(tree, 'meta'):
            meta = tree.meta
            if hasattr(meta, 'line') and meta.line is not None:
                result.line = meta.line
                result.column = getattr(meta, 'column', 0) or 0
        return result

    def _call_userfunc_token(self, token):
        return token

    def __default__(self, data, children, meta):
        """Fallback for rules without explicit handlers."""
        return children

    def _transform_tree(self, tree):
        """Override to inject line/col from Lark meta into AST nodes."""
        result = super()._transform_tree(tree)
        return self._apply_meta(tree, result)

    # ── Program ──────────────────────────────────────────────
    def start(self, *stmts):
        return Program(statements=[s for s in stmts if s is not None])

    # ── Literals ─────────────────────────────────────────────
    def number(self, tok):
        v = float(tok)
        if v == int(v):
            v = int(v)
        return NumberLiteral(value=v)

    def string(self, tok):
        return StringLiteral(value=str(tok)[1:-1])  # strip quotes

    def true_lit(self):
        return BoolLiteral(value=True)

    def false_lit(self):
        return BoolLiteral(value=False)

    def null_lit(self):
        return NullLiteral()

    def list_lit(self, items=None):
        if items is None:
            return ListLiteral(elements=[])
        return ListLiteral(elements=items)

    def expr_list(self, *items):
        return list(items)

    def map_lit(self, pairs=None):
        if pairs is None:
            return MapLiteral(pairs=[])
        return MapLiteral(pairs=pairs)

    def pair_list(self, *pairs):
        return list(pairs)

    def pair(self, key, value):
        if isinstance(key, Token):
            k = str(key)
            if k.startswith('"') or k.startswith("'"):
                k = k[1:-1]
        else:
            k = str(key)
        return (k, value)

    # ── Variables ────────────────────────────────────────────
    def var_ref(self, name):
        return VarRef(name=str(name))

    def declare_infer(self, name, value):
        return DeclareVar(name=str(name), value=value)

    def declare_typed(self, name, type_n, value):
        return DeclareVar(name=str(name), type_name=type_n, value=value)

    def assign_stmt(self, name, value):
        return AssignVar(name=str(name), value=value)

    def assign_field_stmt(self, obj_name, field_name, value):
        from mol.ast_nodes import VarRef
        return AssignField(obj=VarRef(name=str(obj_name)), field_name=str(field_name), value=value)

    def assign_index_stmt(self, obj_name, index, value):
        from mol.ast_nodes import VarRef
        return AssignIndex(obj=VarRef(name=str(obj_name)), index=index, value=value)

    def assign_field_index_stmt(self, obj_name, field_name, index, value):
        from mol.ast_nodes import VarRef, FieldAccess
        obj = FieldAccess(obj=VarRef(name=str(obj_name)), field_name=str(field_name))
        return AssignIndex(obj=obj, index=index, value=value)

    def assign_index_index_stmt(self, obj_name, first_index, second_index, value):
        from mol.ast_nodes import VarRef, IndexAccess
        obj = IndexAccess(obj=VarRef(name=str(obj_name)), index=first_index)
        return AssignIndex(obj=obj, index=second_index, value=value)

    # ── Types ────────────────────────────────────────────────
    def type_thought(self):  return "Thought"
    def type_memory(self):   return "Memory"
    def type_node(self):     return "Node"
    def type_stream(self):   return "Stream"
    def type_number(self):   return "Number"
    def type_text(self):     return "Text"
    def type_bool(self):     return "Bool"
    def type_list(self):     return "List"
    def type_custom(self, n): return str(n)

    # ── Expressions ──────────────────────────────────────────
    def or_expr(self, *args):
        args = list(args)
        if len(args) == 1:
            return args[0]
        result = args[0]
        for i in range(1, len(args)):
            result = LogicalOp(op="or", left=result, right=args[i])
        return result

    def and_expr(self, *args):
        args = list(args)
        if len(args) == 1:
            return args[0]
        result = args[0]
        for i in range(1, len(args)):
            result = LogicalOp(op="and", left=result, right=args[i])
        return result

    def not_expr(self, operand):
        return NotOp(operand=operand)

    def comparison(self, *args):
        args = list(args)
        if len(args) == 1:
            return args[0]
        # args: [left, op, right, op, right, ...]
        result = args[0]
        i = 1
        while i < len(args):
            op = args[i]
            right = args[i + 1]
            result = Comparison(op=op, left=result, right=right)
            i += 2
        return result

    def comp_eq(self):    return "=="
    def comp_neq(self):   return "!="
    def comp_gt(self):    return ">"
    def comp_lt(self):    return "<"
    def comp_gte(self):   return ">="
    def comp_lte(self):   return "<="

    def addition(self, *args):
        args = list(args)
        if len(args) == 1:
            return args[0]
        result = args[0]
        i = 1
        while i < len(args):
            op = args[i]
            right = args[i + 1]
            result = BinaryOp(op=op, left=result, right=right)
            i += 2
        return result

    def op_add(self):  return "+"
    def op_sub(self):  return "-"

    def multiplication(self, *args):
        args = list(args)
        if len(args) == 1:
            return args[0]
        result = args[0]
        i = 1
        while i < len(args):
            op = args[i]
            right = args[i + 1]
            result = BinaryOp(op=op, left=result, right=right)
            i += 2
        return result

    def op_mul(self):  return "*"
    def op_div(self):  return "/"
    def op_mod(self):  return "%"

    def neg(self, operand):
        return UnaryOp(op="-", operand=operand)

    def group(self, expr):
        return Group(expr=expr)

    # ── Access / Calls ───────────────────────────────────────
    def field_access(self, obj, name):
        return FieldAccess(obj=obj, field_name=str(name))

    def index_access(self, obj, idx):
        return IndexAccess(obj=obj, index=idx)

    def method_call(self, obj, name, args=None):
        return MethodCall(obj=obj, method=str(name), args=args or [])

    def func_call(self, name, args=None):
        return FuncCall(name=str(name), args=args or [])

    def arg_list(self, *args):
        return list(args)

    # ── Functions ────────────────────────────────────────────
    def func_def(self, name, *args):
        # When param_list is absent, Lark passes (name, body)
        # When present, it passes (name, params, body)
        if len(args) == 1:
            params = []
            body = args[0]
        else:
            params = args[0]
            body = args[1]
        return FuncDef(
            name=str(name),
            params=params if params else [],
            body=body if body else [],
        )

    def param_list(self, *params):
        return list(params)

    def param(self, name, type_n=None):
        return (str(name), type_n)

    def return_stmt(self, value=None):
        return ReturnStmt(value=value)

    # ── Control Flow ─────────────────────────────────────────
    def if_stmt(self, cond, body, *rest):
        elifs = []
        else_body = None
        for item in rest:
            if item is None:
                continue
            if isinstance(item, tuple) and item[0] == "__elif__":
                elifs.append((item[1], item[2]))
            elif isinstance(item, tuple) and item[0] == "__else__":
                else_body = item[1]
        return IfStmt(
            condition=cond,
            body=body,
            elif_clauses=elifs,
            else_body=else_body,
        )

    def elif_clause(self, cond, body):
        return ("__elif__", cond, body)

    def else_clause(self, body):
        return ("__else__", body)

    def while_stmt(self, cond, body):
        return WhileStmt(condition=cond, body=body)

    def for_stmt(self, name, iterable, body):
        return ForStmt(var_name=str(name), iterable=iterable, body=body)

    # ── Block ────────────────────────────────────────────────
    def block(self, *stmts):
        return [s for s in stmts if s is not None]

    def block_stmt(self, body):
        return BlockStmt(body=body)

    # ── Show ─────────────────────────────────────────────────
    def show_stmt(self, value):
        return ShowStmt(value=value)

    # ── Domain-Specific ──────────────────────────────────────
    def trigger_stmt(self, event):
        return TriggerStmt(event=event)

    def link_stmt(self, source, target):
        return LinkStmt(source=source, target=target)

    def process_stmt(self, target, with_expr=None):
        return ProcessStmt(target=target, with_expr=with_expr)

    def access_stmt(self, resource):
        return AccessStmt(resource=resource)

    def sync_stmt(self, stream):
        return SyncStmt(stream=stream)

    def evolve_stmt(self, node):
        return EvolveStmt(node=node)

    def emit_stmt(self, data):
        return EmitStmt(data=data)

    def listen_stmt(self, event, body):
        return ListenStmt(event=event, body=body)

    # ── Expression Statement ─────────────────────────────────
    def expr_stmt(self, expr):
        return ExprStmt(expr=expr)

    # ── Pipe Chain ───────────────────────────────────────────
    def pipe_chain(self, *args):
        # Filter out any Token objects (anonymous terminals like "|>")
        stages = [a for a in args if not isinstance(a, Token)]
        if len(stages) == 1:
            return stages[0]
        return PipeChain(stages=stages)

    # ── Guard ────────────────────────────────────────────────
    def guard_stmt(self, cond):
        return GuardStmt(condition=cond)

    def guard_msg(self, cond, msg):
        return GuardStmt(condition=cond, message=str(msg)[1:-1])

    # ── Pipeline Definition ──────────────────────────────────
    def pipeline_def(self, name, params, body):
        return PipelineDef(
            name=str(name),
            params=params if params else [],
            body=body if body else [],
        )

    # ── Use (import) Statement ───────────────────────────────
    def use_all(self, module):
        return UseStmt(module=str(module)[1:-1])

    def use_named(self, module, *names):
        return UseStmt(module=str(module)[1:-1], symbols=[str(n) for n in names])

    def use_alias(self, module, alias):
        return UseStmt(module=str(module)[1:-1], alias=str(alias))

    # ── v0.6.0 — Destructuring ──────────────────────────────
    def name_list(self, *names):
        return [str(n) for n in names]

    def destruct_names(self, *args):
        """Parse destructure names, optionally with ...rest at end."""
        names = []
        rest = None
        skip_next = False
        for i, a in enumerate(args):
            s = str(a)
            if s == '...':
                skip_next = True
                continue
            if skip_next:
                rest = s
                skip_next = False
                continue
            names.append(s)
        return (names, rest)

    def destructure_list(self, names_info, value):
        names, rest = names_info
        return DestructureList(names=names, rest=rest, value=value)

    def destructure_map(self, names, value):
        return DestructureMap(keys=names, value=value)

    # ── v0.6.0 — Default Parameters ─────────────────────────
    def param_default(self, name, default):
        return (str(name), None, default)     # (name, type, default_expr)

    # ── v0.6.0 — Null Coalescing ────────────────────────────
    def null_coalesce(self, *args):
        args = list(args)
        if len(args) == 1:
            return args[0]
        result = args[0]
        for i in range(1, len(args)):
            result = NullCoalesce(left=result, right=args[i])
        return result

    # ── v0.6.0 — Try/Rescue/Ensure ──────────────────────────
    def try_rescue(self, body, rescue, ensure=None):
        r_name, r_body = rescue
        e_body = ensure if ensure else []
        return TryRescue(body=body, rescue_name=r_name, rescue_body=r_body, ensure_body=e_body)

    def rescue_clause(self, *args):
        if len(args) == 2:
            return (str(args[0]), args[1])   # (name, body)
        return (None, args[0])               # (None, body)

    def ensure_clause(self, body):
        return body

    # ── v0.6.0 — Test Block ─────────────────────────────────
    def test_block(self, desc, body):
        return TestBlock(description=str(desc)[1:-1], body=body)

    # ── v0.6.0 — Lambda Expression ──────────────────────────
    def lambda_expr(self, *args):
        if len(args) == 1:
            # No parameters: fn() -> body
            return LambdaExpr(params=[], body=args[0])
        names, body = args
        params = names if names else []
        return LambdaExpr(params=params, body=body)

    # ── v0.7.0 — Spawn / Await (Concurrency) ────────────────
    def spawn_expr(self, body):
        return SpawnExpr(body=body)

    def await_expr(self, expr):
        return AwaitExpr(expr=expr)

    # ── v0.8.0 — Structs ────────────────────────────────────
    def struct_field(self, *args):
        name = str(args[0])
        type_name = str(args[1]) if len(args) > 1 else None
        return (name, type_name)

    def struct_fields(self, *fields):
        return list(fields)

    def struct_def(self, name, fields):
        return StructDef(name=str(name), fields=fields)

    def impl_methods(self, *methods):
        return list(methods)

    def impl_block(self, name, methods):
        return ImplBlock(struct_name=str(name), methods=methods)

    def struct_literal(self, name, *pairs):
        # pairs may be: a single pair_list (list of tuples) or individual tuples
        fields = []
        for p in pairs:
            if isinstance(p, list):
                fields.extend(p)
            else:
                fields.append(p)
        return StructLiteral(struct_name=str(name), fields=fields)

    # ── v0.8.0 — Yield ──────────────────────────────────────
    def yield_stmt(self, value):
        return YieldStmt(value=value)

    # ── v0.8.0 — Export ─────────────────────────────────────
    def export_stmt(self, *names):
        return ExportStmt(names=[str(n) for n in names])

    # ── v0.6.0 — Match Expression ───────────────────────────
    def match_expr(self, subject, *arms):
        return MatchExpr(subject=subject, arms=list(arms))

    def match_arm(self, pattern, body):
        # body may be an inline expr (single node) or a block (list of stmts)
        if not isinstance(body, list):
            body = [body]
        return MatchArm(pattern=pattern, body=body)

    def match_arm_guard(self, pattern, guard_expr, body):
        if not isinstance(body, list):
            body = [body]
        return MatchArm(pattern=pattern, guard=guard_expr, body=body)

    def pattern_wildcard(self):
        return MatchPattern(kind="wildcard")

    def pattern_number(self, tok):
        v = float(tok)
        if v == int(v):
            v = int(v)
        return MatchPattern(kind="literal", value=v)

    def pattern_string(self, tok):
        return MatchPattern(kind="literal", value=str(tok)[1:-1])

    def pattern_true(self):
        return MatchPattern(kind="literal", value=True)

    def pattern_false(self):
        return MatchPattern(kind="literal", value=False)

    def pattern_null(self):
        return MatchPattern(kind="literal", value=None)

    def pattern_binding(self, name):
        return MatchPattern(kind="binding", value=str(name))

    def pattern_list(self, items=None):
        return MatchPattern(kind="list", children=items if items else [])

    def pattern_list_rest(self, items, rest):
        return MatchPattern(kind="list_rest", value=str(rest), children=items if items else [])

    def match_pattern_list(self, *items):
        return list(items)

    # ── v0.6.0 — String Interpolation ───────────────────────
    def interp_string(self, tok):
        raw = str(tok)           # f"Hello {name}, {age}"
        inner = raw[2:-1]        # strip f" and "
        parts = []
        i = 0
        while i < len(inner):
            if inner[i] == '{':
                end = inner.index('}', i)
                expr_src = inner[i+1:end]
                # Parse the expression
                from mol.parser import parse as _parse_mol
                mini_ast = _parse_mol(f"show {expr_src}")
                parts.append(mini_ast.statements[0].value)
                i = end + 1
            else:
                # Collect literal text
                j = i
                while j < len(inner) and inner[j] != '{':
                    j += 1
                parts.append(inner[i:j])
                i = j
        return InterpolatedString(parts=parts)


# ── Public API ───────────────────────────────────────────────
def parse(source: str) -> Program:
    """Parse MOL source code and return the AST."""
    tree = _parser.parse(source + "\n")
    transformer = MOLTransformer()
    return transformer.transform(tree)
