"""
MOL Transpiler — Generate Python or JavaScript from MOL AST
=============================================================

Enables MOL programs to be "compiled" to host languages
for portability across web, server, and mobile.
"""

from mol.ast_nodes import *
import json


class PythonTranspiler:
    """Transpile MOL AST → Python source code."""

    def __init__(self):
        self._indent = 0
        self._lines: list[str] = []

    def transpile(self, program: Program) -> str:
        self._lines = [
            "# Auto-generated from MOL",
            "# ─────────────────────────",
            "",
            "from mol.types import Thought, Memory, Node, Stream",
            "",
        ]
        for stmt in program.statements:
            self._emit_stmt(stmt)
        return "\n".join(self._lines)

    def _line(self, text: str):
        self._lines.append("    " * self._indent + text)

    def _emit_stmt(self, node):
        method = f"_emit_{type(node).__name__}"
        handler = getattr(self, method, None)
        if handler:
            handler(node)
        else:
            self._line(f"# Unsupported: {type(node).__name__}")

    def _emit_expr(self, node) -> str:
        method = f"_expr_{type(node).__name__}"
        handler = getattr(self, method, None)
        if handler:
            return handler(node)
        return f"/* unsupported: {type(node).__name__} */"

    # ── Statements ───────────────────────────────────────────
    def _emit_ShowStmt(self, node):
        self._line(f"print({self._emit_expr(node.value)})")

    def _emit_DeclareVar(self, node):
        self._line(f"{node.name} = {self._emit_expr(node.value)}")

    def _emit_AssignVar(self, node):
        self._line(f"{node.name} = {self._emit_expr(node.value)}")

    def _emit_IfStmt(self, node):
        self._line(f"if {self._emit_expr(node.condition)}:")
        self._indent += 1
        for s in node.body:
            self._emit_stmt(s)
        if not node.body:
            self._line("pass")
        self._indent -= 1
        for cond, body in node.elif_clauses:
            self._line(f"elif {self._emit_expr(cond)}:")
            self._indent += 1
            for s in body:
                self._emit_stmt(s)
            if not body:
                self._line("pass")
            self._indent -= 1
        if node.else_body is not None:
            self._line("else:")
            self._indent += 1
            for s in node.else_body:
                self._emit_stmt(s)
            if not node.else_body:
                self._line("pass")
            self._indent -= 1

    def _emit_WhileStmt(self, node):
        self._line(f"while {self._emit_expr(node.condition)}:")
        self._indent += 1
        for s in node.body:
            self._emit_stmt(s)
        if not node.body:
            self._line("pass")
        self._indent -= 1

    def _emit_ForStmt(self, node):
        self._line(f"for {node.var_name} in {self._emit_expr(node.iterable)}:")
        self._indent += 1
        for s in node.body:
            self._emit_stmt(s)
        if not node.body:
            self._line("pass")
        self._indent -= 1

    def _emit_FuncDef(self, node):
        params = ", ".join(p[0] for p in node.params)
        self._line(f"def {node.name}({params}):")
        self._indent += 1
        for s in node.body:
            self._emit_stmt(s)
        if not node.body:
            self._line("pass")
        self._indent -= 1
        self._line("")

    def _emit_ReturnStmt(self, node):
        if node.value:
            self._line(f"return {self._emit_expr(node.value)}")
        else:
            self._line("return")

    def _emit_ExprStmt(self, node):
        self._line(self._emit_expr(node.expr))

    def _emit_TriggerStmt(self, node):
        self._line(f"print(f'[MOL] Triggered: {{{self._emit_expr(node.event)}}}')")

    def _emit_LinkStmt(self, node):
        src = self._emit_expr(node.source)
        tgt = self._emit_expr(node.target)
        self._line(f"# link {src} → {tgt}")
        self._line(f"if hasattr({src}, 'connect'): {src}.connect({tgt})")

    def _emit_ProcessStmt(self, node):
        self._line(f"# process {self._emit_expr(node.target)}")

    def _emit_AccessStmt(self, node):
        self._line(f"# access check: {self._emit_expr(node.resource)}")

    def _emit_SyncStmt(self, node):
        expr = self._emit_expr(node.stream)
        self._line(f"if hasattr({expr}, 'sync'): {expr}.sync()")

    def _emit_EvolveStmt(self, node):
        expr = self._emit_expr(node.node)
        self._line(f"if hasattr({expr}, 'evolve'): {expr}.evolve()")

    def _emit_GuardStmt(self, node):
        cond = self._emit_expr(node.condition)
        msg = repr(node.message) if node.message else '"Guard assertion failed"'
        self._line(f"assert {cond}, {msg}")

    def _emit_PipelineDef(self, node):
        params = ", ".join(p[0] for p in node.params)
        self._line(f"def {node.name}({params}):  # pipeline")
        self._indent += 1
        for s in node.body:
            self._emit_stmt(s)
        if not node.body:
            self._line("pass")
        self._indent -= 1
        self._line("")

    # ── Expressions ──────────────────────────────────────────
    def _expr_NumberLiteral(self, node): return str(node.value)
    def _expr_StringLiteral(self, node): return repr(node.value)
    def _expr_BoolLiteral(self, node): return "True" if node.value else "False"
    def _expr_NullLiteral(self, node): return "None"
    def _expr_VarRef(self, node): return node.name
    def _expr_Group(self, node): return f"({self._emit_expr(node.expr)})"

    def _expr_ListLiteral(self, node):
        items = ", ".join(self._emit_expr(e) for e in node.elements)
        return f"[{items}]"

    def _expr_MapLiteral(self, node):
        pairs = ", ".join(f"{repr(k)}: {self._emit_expr(v)}" for k, v in node.pairs)
        return f"{{{pairs}}}"

    def _expr_BinaryOp(self, node):
        return f"({self._emit_expr(node.left)} {node.op} {self._emit_expr(node.right)})"

    def _expr_UnaryOp(self, node):
        return f"({node.op}{self._emit_expr(node.operand)})"

    def _expr_Comparison(self, node):
        return f"({self._emit_expr(node.left)} {node.op} {self._emit_expr(node.right)})"

    def _expr_LogicalOp(self, node):
        return f"({self._emit_expr(node.left)} {node.op} {self._emit_expr(node.right)})"

    def _expr_NotOp(self, node):
        return f"(not {self._emit_expr(node.operand)})"

    def _expr_FuncCall(self, node):
        args = ", ".join(self._emit_expr(a) for a in node.args)
        return f"{node.name}({args})"

    def _expr_MethodCall(self, node):
        args = ", ".join(self._emit_expr(a) for a in node.args)
        return f"{self._emit_expr(node.obj)}.{node.method}({args})"

    def _expr_FieldAccess(self, node):
        return f"{self._emit_expr(node.obj)}.{node.field_name}"

    def _expr_IndexAccess(self, node):
        return f"{self._emit_expr(node.obj)}[{self._emit_expr(node.index)}]"

    def _expr_PipeChain(self, node):
        # Desugar pipe chain: a |> f |> g(x) → g(f(a), x)
        result = self._emit_expr(node.stages[0])
        for stage in node.stages[1:]:
            if hasattr(stage, 'name') and hasattr(stage, 'args') and stage.args:
                # FuncCall with args
                args = ", ".join(self._emit_expr(a) for a in stage.args)
                result = f"{stage.name}({result}, {args})"
            elif hasattr(stage, 'name'):
                result = f"{stage.name}({result})"
            else:
                result = f"({self._emit_expr(stage)})({result})"
        return result


class JavaScriptTranspiler:
    """Transpile MOL AST → JavaScript source code."""

    def __init__(self):
        self._indent = 0
        self._lines: list[str] = []

    def transpile(self, program: Program) -> str:
        self._lines = [
            "// Auto-generated from MOL",
            "// ─────────────────────────",
            "",
        ]
        for stmt in program.statements:
            self._emit_stmt(stmt)
        return "\n".join(self._lines)

    def _line(self, text: str):
        self._lines.append("  " * self._indent + text)

    def _emit_stmt(self, node):
        method = f"_emit_{type(node).__name__}"
        handler = getattr(self, method, None)
        if handler:
            handler(node)
        else:
            self._line(f"// Unsupported: {type(node).__name__}")

    def _emit_expr(self, node) -> str:
        method = f"_expr_{type(node).__name__}"
        handler = getattr(self, method, None)
        if handler:
            return handler(node)
        return f"/* unsupported: {type(node).__name__} */"

    # ── Statements ───────────────────────────────────────────
    def _emit_ShowStmt(self, node):
        self._line(f"console.log({self._emit_expr(node.value)});")

    def _emit_DeclareVar(self, node):
        self._line(f"let {node.name} = {self._emit_expr(node.value)};")

    def _emit_AssignVar(self, node):
        self._line(f"{node.name} = {self._emit_expr(node.value)};")

    def _emit_IfStmt(self, node):
        self._line(f"if ({self._emit_expr(node.condition)}) {{")
        self._indent += 1
        for s in node.body:
            self._emit_stmt(s)
        self._indent -= 1
        for cond, body in node.elif_clauses:
            self._line(f"}} else if ({self._emit_expr(cond)}) {{")
            self._indent += 1
            for s in body:
                self._emit_stmt(s)
            self._indent -= 1
        if node.else_body is not None:
            self._line("} else {")
            self._indent += 1
            for s in node.else_body:
                self._emit_stmt(s)
            self._indent -= 1
        self._line("}")

    def _emit_WhileStmt(self, node):
        self._line(f"while ({self._emit_expr(node.condition)}) {{")
        self._indent += 1
        for s in node.body:
            self._emit_stmt(s)
        self._indent -= 1
        self._line("}")

    def _emit_ForStmt(self, node):
        self._line(f"for (const {node.var_name} of {self._emit_expr(node.iterable)}) {{")
        self._indent += 1
        for s in node.body:
            self._emit_stmt(s)
        self._indent -= 1
        self._line("}")

    def _emit_FuncDef(self, node):
        params = ", ".join(p[0] for p in node.params)
        self._line(f"function {node.name}({params}) {{")
        self._indent += 1
        for s in node.body:
            self._emit_stmt(s)
        self._indent -= 1
        self._line("}")
        self._line("")

    def _emit_ReturnStmt(self, node):
        if node.value:
            self._line(f"return {self._emit_expr(node.value)};")
        else:
            self._line("return;")

    def _emit_ExprStmt(self, node):
        self._line(f"{self._emit_expr(node.expr)};")

    def _emit_TriggerStmt(self, node):
        self._line(f"console.log(`[MOL] Triggered: ${{{self._emit_expr(node.event)}}}`);")

    def _emit_GuardStmt(self, node):
        cond = self._emit_expr(node.condition)
        msg = json.dumps(node.message) if node.message else '"Guard assertion failed"'
        self._line(f"if (!({cond})) throw new Error({msg});")

    def _emit_PipelineDef(self, node):
        params = ", ".join(p[0] for p in node.params)
        self._line(f"function {node.name}({params}) {{  // pipeline")
        self._indent += 1
        for s in node.body:
            self._emit_stmt(s)
        self._indent -= 1
        self._line("}")
        self._line("")

    # ── Expressions ──────────────────────────────────────────
    def _expr_NumberLiteral(self, node): return str(node.value)
    def _expr_StringLiteral(self, node): return f'"{node.value}"'
    def _expr_BoolLiteral(self, node): return "true" if node.value else "false"
    def _expr_NullLiteral(self, node): return "null"
    def _expr_VarRef(self, node): return node.name
    def _expr_Group(self, node): return f"({self._emit_expr(node.expr)})"

    def _expr_ListLiteral(self, node):
        items = ", ".join(self._emit_expr(e) for e in node.elements)
        return f"[{items}]"

    def _expr_MapLiteral(self, node):
        pairs = ", ".join(f'"{k}": {self._emit_expr(v)}' for k, v in node.pairs)
        return f"{{{pairs}}}"

    def _expr_BinaryOp(self, node):
        return f"({self._emit_expr(node.left)} {node.op} {self._emit_expr(node.right)})"

    def _expr_UnaryOp(self, node):
        return f"({node.op}{self._emit_expr(node.operand)})"

    def _expr_Comparison(self, node):
        op = node.op
        if op == "==":
            op = "==="
        elif op == "!=":
            op = "!=="
        return f"({self._emit_expr(node.left)} {op} {self._emit_expr(node.right)})"

    def _expr_LogicalOp(self, node):
        op = "||" if node.op == "or" else "&&"
        return f"({self._emit_expr(node.left)} {op} {self._emit_expr(node.right)})"

    def _expr_NotOp(self, node):
        return f"(!{self._emit_expr(node.operand)})"

    def _expr_FuncCall(self, node):
        args = ", ".join(self._emit_expr(a) for a in node.args)
        return f"{node.name}({args})"

    def _expr_MethodCall(self, node):
        args = ", ".join(self._emit_expr(a) for a in node.args)
        return f"{self._emit_expr(node.obj)}.{node.method}({args})"

    def _expr_FieldAccess(self, node):
        return f"{self._emit_expr(node.obj)}.{node.field_name}"

    def _expr_IndexAccess(self, node):
        return f"{self._emit_expr(node.obj)}[{self._emit_expr(node.index)}]"

    def _expr_PipeChain(self, node):
        result = self._emit_expr(node.stages[0])
        for stage in node.stages[1:]:
            if hasattr(stage, 'name') and hasattr(stage, 'args') and stage.args:
                args = ", ".join(self._emit_expr(a) for a in stage.args)
                result = f"{stage.name}({result}, {args})"
            elif hasattr(stage, 'name'):
                result = f"{stage.name}({result})"
            else:
                result = f"({self._emit_expr(stage)})({result})"
        return result