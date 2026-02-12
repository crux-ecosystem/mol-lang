"""
MOL Interpreter — Visitor Pattern AST Walker
==============================================

Walks the AST and executes MOL programs. Features:
  - Scoped variable environments
  - Safety-rail enforcement via SecurityContext
  - Domain-type awareness (Thought, Memory, Node, Stream)
  - Event system for trigger/listen
"""

from mol.ast_nodes import *
from mol.types import Thought, Memory, Node, Stream, Document, Chunk, Embedding, VectorStore
from mol.stdlib import STDLIB, SecurityContext, MOLSecurityError, MOLTypeError, MOLTask, _THREAD_POOL
from mol.stdlib import MOLAssertionError
import time as _time


class MOLRuntimeError(Exception):
    """Raised when the interpreter encounters a runtime error."""
    pass


class MOLGuardError(Exception):
    """Raised when a guard assertion fails."""
    pass


class ReturnSignal(Exception):
    """Used internally to unwind the stack on `return`."""
    def __init__(self, value=None):
        self.value = value


class YieldSignal(Exception):
    """Used internally to collect yield values from generators."""
    def __init__(self, value=None):
        self.value = value


class Environment:
    """Scoped variable environment with parent chain."""

    def __init__(self, parent=None):
        self._store: dict = {}
        self._parent: Environment | None = parent

    def get(self, name: str):
        if name in self._store:
            return self._store[name]
        if self._parent:
            return self._parent.get(name)
        raise MOLRuntimeError(f"Undefined variable: '{name}'")

    def set(self, name: str, value):
        self._store[name] = value

    def update(self, name: str, value):
        if name in self._store:
            self._store[name] = value
            return
        if self._parent:
            self._parent.update(name, value)
            return
        raise MOLRuntimeError(f"Cannot set undefined variable: '{name}'. Use 'let' first.")

    def has(self, name: str) -> bool:
        if name in self._store:
            return True
        if self._parent:
            return self._parent.has(name)
        return False


class MOLFunction:
    """A user-defined MOL function."""

    def __init__(self, name, params, body, closure_env):
        self.name = name
        self.params = params      # list of (name, type_or_None)
        self.body = body          # list of statements
        self.closure_env = closure_env
        self._interpreter = None  # set by interpreter after creation

    def __call__(self, *args):
        """Allow MOLFunction to be used as a Python callable."""
        if self._interpreter is None:
            raise MOLRuntimeError(f"Function '{self.name}' has no interpreter bound")
        return self._interpreter._invoke_callable(self, list(args), self.name)


class MOLPipeline:
    """A named pipeline — like a function but with auto-tracing."""

    def __init__(self, name, params, body, closure_env):
        self.name = name
        self.params = params
        self.body = body
        self.closure_env = closure_env
        self._interpreter = None

    def __call__(self, *args):
        if self._interpreter is None:
            raise MOLRuntimeError(f"Pipeline '{self.name}' has no interpreter bound")
        return self._interpreter._invoke_callable(self, list(args), self.name)


class MOLLambda:
    """An anonymous lambda: fn(x) -> expr"""

    def __init__(self, params, body_expr, closure_env):
        self.name = "<lambda>"
        self.params = params       # list of (name, type_or_None)
        self.body_expr = body_expr # single expression AST node
        self.closure_env = closure_env
        self._interpreter = None

    def __call__(self, *args):
        if self._interpreter is None:
            raise MOLRuntimeError("Lambda has no interpreter bound")
        return self._interpreter._invoke_lambda(self, list(args))


class MOLStructDef:
    """Metadata for a user-defined struct type."""

    def __init__(self, name, field_names, field_types=None):
        self.name = name
        self.field_names = field_names    # list of str
        self.field_types = field_types or {}  # name → type_name
        self.methods = {}                 # name → MOLFunction

    def __repr__(self):
        return f"<struct {self.name}>"


class MOLStructInstance:
    """An instance of a user-defined struct."""

    def __init__(self, struct_def, field_values):
        self._struct_def = struct_def
        self._fields = dict(field_values)

    def get_field(self, name):
        if name in self._fields:
            return self._fields[name]
        if name in self._struct_def.methods:
            return self._struct_def.methods[name]
        raise MOLRuntimeError(f"Struct '{self._struct_def.name}' has no field '{name}'")

    def set_field(self, name, value):
        if name not in self._fields:
            raise MOLRuntimeError(f"Struct '{self._struct_def.name}' has no field '{name}'")
        self._fields[name] = value

    def __repr__(self):
        pairs = ", ".join(f"{k}: {_repr_val(v)}" for k, v in self._fields.items())
        return f"{self._struct_def.name} {{ {pairs} }}"


def _repr_val(v):
    if isinstance(v, str):
        return f'"{v}"'
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return repr(v)


class MOLGenerator:
    """A lazy generator produced by functions that use yield."""

    def __init__(self, gen_iter):
        self._iter = gen_iter
        self._exhausted = False

    def __iter__(self):
        return self._iter

    def __next__(self):
        try:
            return next(self._iter)
        except StopIteration:
            self._exhausted = True
            raise

    def to_list(self):
        return list(self._iter)

    def __repr__(self):
        return "<Generator>"


class Interpreter:
    """
    The MOL interpreter. Walks the AST and executes each node.

    Usage:
        from mol.parser import parse
        from mol.interpreter import Interpreter

        ast = parse(source_code)
        interp = Interpreter()
        interp.run(ast)
    """

    def __init__(self, security: SecurityContext | None = None, trace: bool = True):
        self.global_env = Environment()
        self.security = security or SecurityContext()
        self.output: list[str] = []           # captured output
        self._event_listeners: dict = {}      # event → [callbacks]
        self._trace_enabled = trace           # auto-trace pipe chains
        self._current_line = 0                # v0.8.0: line tracking for errors
        self._current_col = 0                 # v0.8.0: column tracking
        self._source_file = "<stdin>"         # v0.8.0: current file name

        # Load standard library into global scope
        for name, fn in STDLIB.items():
            self.global_env.set(name, fn)

    # ── Public API ───────────────────────────────────────────
    def run(self, program: Program):
        """Execute a full MOL program."""
        return self._exec_block(program.statements, self.global_env)

    # ── Statement Execution ──────────────────────────────────
    def _exec_block(self, stmts: list, env: Environment):
        result = None
        for stmt in stmts:
            result = self._exec(stmt, env)
        return result

    def _exec(self, node, env: Environment):
        """Dispatch execution to the appropriate handler."""
        # Track line info for error messages (v0.8.0)
        if hasattr(node, 'line') and node.line > 0:
            self._current_line = node.line
            self._current_col = node.column
        method_name = f"_exec_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise MOLRuntimeError(f"Unknown AST node: {type(node).__name__}")
        try:
            return method(node, env)
        except MOLRuntimeError:
            raise  # Already has context
        except (ReturnSignal, YieldSignal):
            raise  # Control flow, not errors
        except (MOLSecurityError, MOLTypeError, MOLGuardError, MOLAssertionError):
            raise  # Domain-specific errors, don't wrap
        except Exception as e:
            if self._current_line > 0:
                raise MOLRuntimeError(
                    f"[{self._source_file}:{self._current_line}] {e}"
                ) from e
            raise

    # ── Show ─────────────────────────────────────────────────
    def _exec_ShowStmt(self, node: ShowStmt, env):
        value = self._eval(node.value, env)
        text = self._to_string(value)
        self.output.append(text)
        print(text)
        return None

    # ── Variables ────────────────────────────────────────────
    def _exec_DeclareVar(self, node: DeclareVar, env):
        value = self._eval(node.value, env)
        if node.type_name:
            self._check_type(value, node.type_name, node.name)
        env.set(node.name, value)
        return value

    def _exec_AssignVar(self, node: AssignVar, env):
        value = self._eval(node.value, env)
        env.update(node.name, value)
        return value

    def _exec_AssignField(self, node: AssignField, env):
        obj = self._eval(node.obj, env)
        value = self._eval(node.value, env)
        if isinstance(obj, MOLStructInstance):
            obj.set_field(node.field_name, value)
        elif isinstance(obj, dict):
            obj[node.field_name] = value
        else:
            raise MOLRuntimeError(f"Cannot set field '{node.field_name}' on {type(obj).__name__}")
        return value

    def _exec_AssignIndex(self, node: AssignIndex, env):
        obj = self._eval(node.obj, env)
        idx = self._eval(node.index, env)
        value = self._eval(node.value, env)
        if isinstance(obj, list):
            obj[int(idx)] = value
        elif isinstance(obj, dict):
            obj[idx] = value
        else:
            raise MOLRuntimeError(f"Cannot set index on {type(obj).__name__}")
        return value

    # ── Control Flow ─────────────────────────────────────────
    def _exec_IfStmt(self, node: IfStmt, env):
        if self._truthy(self._eval(node.condition, env)):
            return self._exec_block(node.body, Environment(env))
        for cond, body in node.elif_clauses:
            if self._truthy(self._eval(cond, env)):
                return self._exec_block(body, Environment(env))
        if node.else_body is not None:
            return self._exec_block(node.else_body, Environment(env))
        return None

    def _exec_WhileStmt(self, node: WhileStmt, env):
        iterations = 0
        max_iterations = 1_000_000
        while self._truthy(self._eval(node.condition, env)):
            self._exec_block(node.body, Environment(env))
            iterations += 1
            if iterations > max_iterations:
                raise MOLRuntimeError("Infinite loop detected (exceeded 1,000,000 iterations)")
        return None

    def _exec_ForStmt(self, node: ForStmt, env):
        iterable = self._eval(node.iterable, env)
        if not hasattr(iterable, '__iter__'):
            raise MOLRuntimeError(f"Cannot iterate over {type(iterable).__name__}")
        for item in iterable:
            loop_env = Environment(env)
            loop_env.set(node.var_name, item)
            self._exec_block(node.body, loop_env)
        return None

    # ── Functions ────────────────────────────────────────────
    def _exec_FuncDef(self, node: FuncDef, env):
        func = MOLFunction(node.name, node.params, node.body, env)
        func._interpreter = self
        env.set(node.name, func)
        return func

    def _exec_ReturnStmt(self, node: ReturnStmt, env):
        value = self._eval(node.value, env) if node.value else None
        raise ReturnSignal(value)

    # ── Domain Specific ──────────────────────────────────────
    def _exec_TriggerStmt(self, node: TriggerStmt, env):
        event = self._eval(node.event, env)
        event_name = self._to_string(event)
        print(f"[MOL] ⚡ Triggered: {event_name}")
        self.output.append(f"[MOL] ⚡ Triggered: {event_name}")
        # fire listeners
        if event_name in self._event_listeners:
            for body, listener_env in self._event_listeners[event_name]:
                self._exec_block(body, Environment(listener_env))
        return None

    def _exec_LinkStmt(self, node: LinkStmt, env):
        source = self._eval(node.source, env)
        target = self._eval(node.target, env)
        # Handle Node-to-Node linking
        if isinstance(source, Node) and isinstance(target, Node):
            source.connect(target)
            msg = f"[MOL] 🔗 Linked: {source.mol_repr()} → {target.mol_repr()}"
        elif isinstance(source, Thought) and isinstance(target, Thought):
            source.link(target)
            msg = f"[MOL] 🔗 Linked: {source.mol_repr()} → {target.mol_repr()}"
        else:
            msg = f"[MOL] 🔗 Linked: {self._to_string(source)} → {self._to_string(target)}"
        print(msg)
        self.output.append(msg)
        return None

    def _exec_ProcessStmt(self, node: ProcessStmt, env):
        target = self._eval(node.target, env)
        with_val = self._eval(node.with_expr, env) if node.with_expr else None
        if isinstance(target, Node):
            target.activate()
            if with_val is not None and isinstance(with_val, (int, float)):
                target.weight += with_val
            msg = f"[MOL] ⚙️  Processed: {target.mol_repr()}"
        else:
            msg = f"[MOL] ⚙️  Processed: {self._to_string(target)}"
            if with_val is not None:
                msg += f" with {self._to_string(with_val)}"
        print(msg)
        self.output.append(msg)
        return target

    def _exec_AccessStmt(self, node: AccessStmt, env):
        resource = self._eval(node.resource, env)
        resource_name = self._to_string(resource)
        self.security.check_access(resource_name)
        msg = f"[MOL] 🔓 Access granted: {resource_name}"
        print(msg)
        self.output.append(msg)
        return True

    def _exec_SyncStmt(self, node: SyncStmt, env):
        stream = self._eval(node.stream, env)
        if isinstance(stream, Stream):
            stream.sync()
            msg = f"[MOL] 🔄 Synced: {stream.mol_repr()}"
        else:
            msg = f"[MOL] 🔄 Synced: {self._to_string(stream)}"
        print(msg)
        self.output.append(msg)
        return stream

    def _exec_EvolveStmt(self, node: EvolveStmt, env):
        target = self._eval(node.node, env)
        if isinstance(target, Node):
            target.evolve()
            msg = f"[MOL] 🧬 Evolved: {target.mol_repr()}"
        else:
            msg = f"[MOL] 🧬 Evolved: {self._to_string(target)}"
        print(msg)
        self.output.append(msg)
        return target

    def _exec_EmitStmt(self, node: EmitStmt, env):
        data = self._eval(node.data, env)
        msg = f"[MOL] 📡 Emitted: {self._to_string(data)}"
        print(msg)
        self.output.append(msg)
        return data

    def _exec_ListenStmt(self, node: ListenStmt, env):
        event = self._eval(node.event, env)
        event_name = self._to_string(event)
        if event_name not in self._event_listeners:
            self._event_listeners[event_name] = []
        self._event_listeners[event_name].append((node.body, env))
        msg = f"[MOL] 👂 Listening for: {event_name}"
        print(msg)
        self.output.append(msg)
        return None

    def _exec_BlockStmt(self, node: BlockStmt, env):
        return self._exec_block(node.body, Environment(env))

    def _exec_ExprStmt(self, node: ExprStmt, env):
        return self._eval(node.expr, env)

    # ── Guard ─────────────────────────────────────────────
    def _exec_GuardStmt(self, node: GuardStmt, env):
        value = self._eval(node.condition, env)
        if not self._truthy(value):
            msg = node.message or "Guard assertion failed"
            raise MOLGuardError(f"\U0001f6e1 {msg}")
        return True

    # ── Pipeline Definition ──────────────────────────────────
    def _exec_PipelineDef(self, node: PipelineDef, env):
        pipe = MOLPipeline(node.name, node.params, node.body, env)
        pipe._interpreter = self
        env.set(node.name, pipe)
        return pipe

    # ── Use (import) Statement ───────────────────────────────
    def _exec_UseStmt(self, node, env):
        """Handle 'use' — import package or file into current scope."""
        from mol.package_manager import (
            get_package_exports, load_mol_file, BUILTIN_PACKAGES
        )

        module = node.module
        exports = {}

        # Determine if it's a file path or a package name
        if module.endswith(".mol") or module.startswith("./") or module.startswith("../") or "/" in module:
            # Local file import
            try:
                exports = load_mol_file(module)
            except FileNotFoundError as exc:
                raise MOLRuntimeError(str(exc))
        else:
            # Package import
            exports = get_package_exports(module)
            if not exports:
                raise MOLRuntimeError(f"Package not found: '{module}'. Run 'mol install {module}' first.")

        if node.alias:
            # use "math" as M → create namespace map
            env.set(node.alias, exports)
        elif node.symbols:
            # use "math" : sin, cos → import specific symbols
            for sym in node.symbols:
                if sym in exports:
                    env.set(sym, exports[sym])
                else:
                    raise MOLRuntimeError(
                        f"Symbol '{sym}' not found in package '{module}'"
                    )
        else:
            # use "math" → import all exports
            for name, val in exports.items():
                env.set(name, val)

        return None

    # ── v0.6.0 — Destructuring ──────────────────────────────
    def _exec_DestructureList(self, node, env):
        """let [a, b, c] be expr  or  let [head, ...tail] be expr"""
        value = self._eval(node.value, env)
        if not isinstance(value, list):
            raise MOLRuntimeError(f"Cannot destructure {type(value).__name__} as list")
        for i, name in enumerate(node.names):
            if name != "_":
                if i < len(value):
                    env.set(name, value[i])
                else:
                    env.set(name, None)
        if node.rest:
            rest_start = len(node.names)
            env.set(node.rest, value[rest_start:])
        return None

    def _exec_DestructureMap(self, node, env):
        """let {x, y, z} be expr"""
        value = self._eval(node.value, env)
        if not isinstance(value, dict):
            raise MOLRuntimeError(f"Cannot destructure {type(value).__name__} as map")
        for key in node.keys:
            if key in value:
                env.set(key, value[key])
            else:
                env.set(key, None)
        return None

    # ── v0.6.0 — Try/Rescue/Ensure ──────────────────────────
    def _exec_TryRescue(self, node, env):
        """try ... rescue [name] ... ensure ... end"""
        try:
            result = self._exec_block(node.body, Environment(env))
        except (ReturnSignal, YieldSignal):
            raise  # Don't catch control flow signals
        except (MOLRuntimeError, MOLGuardError, Exception) as e:
            rescue_env = Environment(env)
            if node.rescue_name:
                rescue_env.set(node.rescue_name, str(e))
            result = self._exec_block(node.rescue_body, rescue_env)
        finally:
            if node.ensure_body:
                self._exec_block(node.ensure_body, Environment(env))
        return result

    # ── v0.6.0 — Test Block ─────────────────────────────────
    def _exec_TestBlock(self, node, env):
        """test "description" do ... end — only runs in test mode."""
        # Store test blocks for later execution by `mol test`
        if not hasattr(self, '_test_blocks'):
            self._test_blocks = []
        self._test_blocks.append(node)
        return None

    # ── v0.8.0 — Structs ────────────────────────────────────
    def _exec_StructDef(self, node, env):
        """struct Name do field1, field2 end — register struct type."""
        field_names = [f[0] for f in node.fields]
        field_types = {f[0]: f[1] for f in node.fields if f[1]}
        sdef = MOLStructDef(node.name, field_names, field_types)
        env.set(node.name, sdef)
        return None

    def _exec_ImplBlock(self, node, env):
        """impl Name do ... end — attach methods to a struct."""
        sdef = env.get(node.struct_name)
        if not isinstance(sdef, MOLStructDef):
            raise MOLRuntimeError(f"impl: '{node.struct_name}' is not a struct")
        for method_node in node.methods:
            func = MOLFunction(method_node.name, method_node.params, method_node.body, env)
            func._interpreter = self
            sdef.methods[method_node.name] = func
        return None

    # ── v0.8.0 — Yield ──────────────────────────────────────
    def _exec_YieldStmt(self, node, env):
        """yield expr — throw a YieldSignal."""
        value = self._eval(node.value, env)
        raise YieldSignal(value)

    # ── v0.8.0 — Export ─────────────────────────────────────
    def _exec_ExportStmt(self, node, env):
        """export name1, name2 — mark symbols for module export."""
        if not hasattr(self, '_exports'):
            self._exports = set()
        for name in node.names:
            self._exports.add(name)
        return None

    # ── Expression Evaluation ────────────────────────────────
    def _eval(self, node, env: Environment):
        if node is None:
            return None
        # Track line info for error messages
        if hasattr(node, 'line') and node.line > 0:
            self._current_line = node.line
            self._current_col = node.column
        method_name = f"_eval_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            # Might be a statement used as expression
            exec_method = f"_exec_{type(node).__name__}"
            exec_m = getattr(self, exec_method, None)
            if exec_m:
                return exec_m(node, env)
            raise MOLRuntimeError(f"Cannot evaluate: {type(node).__name__}")
        return method(node, env)

    def _eval_NumberLiteral(self, node, env):
        return node.value

    def _eval_StringLiteral(self, node, env):
        return node.value

    def _eval_BoolLiteral(self, node, env):
        return node.value

    def _eval_NullLiteral(self, node, env):
        return None

    def _eval_ListLiteral(self, node, env):
        return [self._eval(el, env) for el in node.elements]

    def _eval_MapLiteral(self, node, env):
        return {k: self._eval(v, env) for k, v in node.pairs}

    def _eval_VarRef(self, node, env):
        return env.get(node.name)

    def _eval_Group(self, node, env):
        return self._eval(node.expr, env)

    def _eval_BinaryOp(self, node, env):
        left = self._eval(node.left, env)
        right = self._eval(node.right, env)
        ops = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: self._safe_div(a, b),
            "%": lambda a, b: a % b,
        }
        if node.op not in ops:
            raise MOLRuntimeError(f"Unknown operator: {node.op}")
        return ops[node.op](left, right)

    def _eval_UnaryOp(self, node, env):
        val = self._eval(node.operand, env)
        if node.op == "-":
            return -val
        raise MOLRuntimeError(f"Unknown unary operator: {node.op}")

    def _eval_Comparison(self, node, env):
        left = self._eval(node.left, env)
        right = self._eval(node.right, env)
        ops = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">":  lambda a, b: a > b,
            "<":  lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
        }
        return ops[node.op](left, right)

    def _eval_LogicalOp(self, node, env):
        left = self._eval(node.left, env)
        if node.op == "or":
            return left if self._truthy(left) else self._eval(node.right, env)
        if node.op == "and":
            return self._eval(node.right, env) if self._truthy(left) else left
        raise MOLRuntimeError(f"Unknown logical op: {node.op}")

    def _eval_NotOp(self, node, env):
        return not self._truthy(self._eval(node.operand, env))

    # ── v0.6.0 — Null Coalescing ────────────────────────────
    def _eval_NullCoalesce(self, node, env):
        """expr ?? default — returns right if left is null."""
        left = self._eval(node.left, env)
        if left is None:
            return self._eval(node.right, env)
        return left

    # ── v0.6.0 — Lambda Expression ──────────────────────────
    def _eval_LambdaExpr(self, node, env):
        """fn(x, y) -> expr — returns a callable closure."""
        # Create a MOLFunction-like closure that evaluates a single expression
        params = [(p, None) for p in node.params]
        lambda_fn = MOLLambda(params, node.body, env)
        lambda_fn._interpreter = self
        return lambda_fn

    # ── v0.7.0 — Spawn / Await (Concurrency) ────────────────
    def _eval_SpawnExpr(self, node, env):
        """spawn do ... end — execute block in background thread, return Task."""
        # Capture the environment snapshot for the spawned thread
        spawn_env = Environment(env)

        def _run_spawned():
            result = self._exec_block(node.body, spawn_env)
            return result

        future = _THREAD_POOL.submit(_run_spawned)
        return MOLTask(future)

    def _eval_AwaitExpr(self, node, env):
        """await task — block until the Task completes, return its result."""
        task = self._eval(node.expr, env)
        if isinstance(task, MOLTask):
            return task.result()
        # If it's not a task, just return the value (already resolved)
        return task

    # ── v0.6.0 — Match Expression ───────────────────────────
    def _eval_MatchExpr(self, node, env):
        """match expr with | pattern -> body end"""
        subject = self._eval(node.subject, env)
        for arm in node.arms:
            match_env = Environment(env)
            if self._match_pattern(arm.pattern, subject, match_env):
                # Check guard if present
                if arm.guard:
                    if not self._truthy(self._eval(arm.guard, match_env)):
                        continue
                try:
                    body = arm.body
                    # Single inline expression — evaluate directly
                    if len(body) == 1 and not hasattr(self, f"_exec_{type(body[0]).__name__}"):
                        return self._eval(body[0], match_env)
                    result = self._exec_block(body, match_env)
                except ReturnSignal as ret:
                    return ret.value
                return result
        return None  # no match

    def _match_pattern(self, pattern, value, env) -> bool:
        """Check if a value matches a pattern, binding variables."""
        if pattern.kind == "wildcard":
            return True
        elif pattern.kind == "literal":
            return value == pattern.value
        elif pattern.kind == "binding":
            env.set(pattern.value, value)
            return True
        elif pattern.kind == "list":
            if not isinstance(value, list):
                return False
            if len(value) != len(pattern.children):
                return False
            for sub_pat, sub_val in zip(pattern.children, value):
                if not self._match_pattern(sub_pat, sub_val, env):
                    return False
            return True
        elif pattern.kind == "list_rest":
            if not isinstance(value, list):
                return False
            if len(value) < len(pattern.children):
                return False
            for i, sub_pat in enumerate(pattern.children):
                if not self._match_pattern(sub_pat, value[i], env):
                    return False
            # Bind rest
            if pattern.value:
                env.set(pattern.value, value[len(pattern.children):])
            return True
        return False

    # ── v0.6.0 — String Interpolation ───────────────────────
    def _eval_InterpolatedString(self, node, env):
        """f"Hello {name}" — evaluate interpolated parts."""
        parts = []
        for p in node.parts:
            if isinstance(p, str):
                parts.append(p)
            else:
                val = self._eval(p, env)
                parts.append(self._to_string(val))
        return "".join(parts)

    # ── Pipe Chain (THE KILLER FEATURE) ─────────────────────
    def _eval_PipeChain(self, node, env):
        """Evaluate a |> pipe chain with automatic tracing."""
        stages = node.stages
        value = self._eval(stages[0], env)

        if len(stages) < 2:
            return value

        traces = []
        total_start = _time.time()

        # Record initial value
        traces.append({
            "step": 0,
            "name": "input",
            "time_ms": 0.0,
            "value_desc": self._describe_value(value),
        })

        for i, stage in enumerate(stages[1:], 1):
            step_start = _time.time()
            stage_name = self._pipe_stage_name(stage)

            # Execute the pipe stage
            value = self._eval_pipe_stage(stage, value, env)

            elapsed = (_time.time() - step_start) * 1000
            traces.append({
                "step": i,
                "name": stage_name,
                "time_ms": elapsed,
                "value_desc": self._describe_value(value),
            })

        total_ms = (_time.time() - total_start) * 1000

        if self._trace_enabled and len(traces) >= 3:
            self._print_trace(traces, total_ms)

        return value

    def _eval_pipe_stage(self, stage, piped_value, env):
        """Evaluate a single pipe stage, passing piped_value as first arg."""
        if isinstance(stage, FuncCall):
            func = env.get(stage.name)
            args = [piped_value] + [self._eval(a, env) for a in stage.args]
            return self._invoke_callable(func, args, stage.name)
        elif isinstance(stage, VarRef):
            func = env.get(stage.name)
            return self._invoke_callable(func, [piped_value], stage.name)
        elif isinstance(stage, MethodCall):
            obj = self._eval(stage.obj, env)
            method = getattr(obj, stage.method, None)
            if method and callable(method):
                args = [self._eval(a, env) for a in stage.args]
                return method(*args)
            raise MOLRuntimeError(f"No method '{stage.method}' on {type(obj).__name__}")
        else:
            # Try evaluating as a callable expression
            func = self._eval(stage, env)
            if callable(func):
                return func(piped_value)
            raise MOLRuntimeError(
                f"Cannot pipe into {type(stage).__name__} — expected a callable"
            )

    def _invoke_callable(self, func, args, name="<anon>"):
        """Invoke a builtin, MOLFunction, MOLPipeline, or MOLLambda with args."""
        if callable(func) and not isinstance(func, (MOLFunction, MOLPipeline, MOLLambda, MOLStructDef)):
            return func(*args)
        if isinstance(func, MOLLambda):
            return self._invoke_lambda(func, args)
        if isinstance(func, (MOLFunction, MOLPipeline)):
            # Handle default parameters (v0.6.0)
            required = 0
            for p in func.params:
                if len(p) < 3:  # no default
                    required += 1
            if len(args) < required:
                raise MOLRuntimeError(
                    f"'{func.name}' expects at least {required} args, got {len(args)}"
                )
            if len(args) > len(func.params):
                raise MOLRuntimeError(
                    f"'{func.name}' expects at most {len(func.params)} args, got {len(args)}"
                )
            call_env = Environment(func.closure_env)
            for i, param in enumerate(func.params):
                param_name = param[0]
                param_type = param[1] if len(param) > 1 else None
                if i < len(args):
                    arg_val = args[i]
                else:
                    # Use default value (3rd element of param tuple)
                    if len(param) >= 3:
                        arg_val = self._eval(param[2], call_env)
                    else:
                        arg_val = None
                if param_type:
                    self._check_type(arg_val, param_type, param_name)
                call_env.set(param_name, arg_val)

            # Check if function is a generator (contains yield)
            if self._body_has_yield(func.body):
                return self._invoke_generator(func.body, call_env)

            try:
                self._exec_block(func.body, call_env)
            except ReturnSignal as ret:
                return ret.value
            return None
        raise MOLRuntimeError(f"'{name}' is not callable")

    def _body_has_yield(self, body):
        """Check if a function body contains any yield statement."""
        for stmt in body:
            if isinstance(stmt, YieldStmt):
                return True
            # Check nested blocks (if/while/for etc)
            if hasattr(stmt, 'body') and isinstance(stmt.body, list):
                if self._body_has_yield(stmt.body):
                    return True
            if hasattr(stmt, 'else_body') and isinstance(stmt.else_body, list):
                if self._body_has_yield(stmt.else_body):
                    return True
        return False

    def _invoke_generator(self, body, call_env):
        """Execute a generator function, collecting yields into a MOLGenerator."""
        def gen_iter():
            try:
                self._exec_block(body, call_env)
            except YieldSignal as ys:
                yield ys.value
                # Continue executing — we need a more sophisticated approach
                # Use a step-by-step generator
            except ReturnSignal:
                return

        # Build a proper step-by-step generator
        def step_gen():
            for stmt in body:
                yield from self._gen_exec_stmt(stmt, call_env)

        return MOLGenerator(step_gen())

    def _gen_exec_stmt(self, node, env):
        """Execute a statement inside a generator, yielding on YieldStmt."""
        if isinstance(node, YieldStmt):
            yield self._eval(node.value, env)
            return
        if isinstance(node, ForStmt):
            iterable = self._eval(node.iterable, env)
            for item in iterable:
                loop_env = Environment(env)
                loop_env.set(node.var_name, item)
                for s in node.body:
                    yield from self._gen_exec_stmt(s, loop_env)
            return
        if isinstance(node, WhileStmt):
            while self._truthy(self._eval(node.condition, env)):
                for s in node.body:
                    yield from self._gen_exec_stmt(s, env)
            return
        if isinstance(node, IfStmt):
            if self._truthy(self._eval(node.condition, env)):
                for s in node.body:
                    yield from self._gen_exec_stmt(s, env)
            else:
                matched = False
                for cond, body in node.elif_clauses:
                    if self._truthy(self._eval(cond, env)):
                        for s in body:
                            yield from self._gen_exec_stmt(s, env)
                        matched = True
                        break
                if not matched and node.else_body:
                    for s in node.else_body:
                        yield from self._gen_exec_stmt(s, env)
            return
        if isinstance(node, ReturnStmt):
            return  # Stop generator
        # For all other statements, just execute normally
        self._exec(node, env)


    def _invoke_lambda(self, lam, args):
        """Invoke a lambda expression: fn(x) -> expr"""
        if len(args) != len(lam.params):
            raise MOLRuntimeError(
                f"Lambda expects {len(lam.params)} args, got {len(args)}"
            )
        call_env = Environment(lam.closure_env)
        for (param_name, _), arg_val in zip(lam.params, args):
            call_env.set(param_name, arg_val)
        return self._eval(lam.body_expr, call_env)

    def _pipe_stage_name(self, stage) -> str:
        """Get a human-readable name for a pipe stage."""
        if isinstance(stage, FuncCall):
            args_str = ", ".join(".." for _ in stage.args)
            return f"{stage.name}({args_str})" if stage.args else stage.name
        if isinstance(stage, VarRef):
            return stage.name
        if isinstance(stage, MethodCall):
            return f".{stage.method}()"
        return type(stage).__name__

    def _describe_value(self, value) -> str:
        """Concise description of a value for trace output."""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return f"Number({value})"
        if isinstance(value, float):
            return f"Number({value:.2f})"
        if isinstance(value, str):
            if len(value) > 35:
                return f'Text("{value[:32]}...")'
            return f'Text("{value}")'
        if isinstance(value, list):
            if len(value) > 0:
                first = value[0]
                inner = type(first).__name__
                return f"List<{len(value)} {inner}s>"
            return "List<empty>"
        if isinstance(value, dict):
            return f"Map<{len(value)} entries>"
        if isinstance(value, (Thought, Memory, Node, Stream,
                              Document, Chunk, Embedding, VectorStore)):
            return value.mol_repr()
        return str(value)[:35]

    def _print_trace(self, traces, total_ms):
        """Print a beautiful pipeline trace."""
        C_CYAN = "\033[36m"
        C_DIM = "\033[90m"
        C_YEL = "\033[33m"
        C_GRN = "\033[32m"
        C_RST = "\033[0m"

        header = f"  {C_CYAN}\u250c\u2500 Pipeline Trace \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500{C_RST}"
        print(header)
        self.output.append("[TRACE] Pipeline Trace")

        for t in traces:
            step = t["step"]
            name = t["name"]
            ms = t["time_ms"]
            desc = t["value_desc"]

            if step == 0:
                line = (f"  {C_CYAN}\u2502{C_RST} {C_DIM}{step}.{C_RST}  "
                        f"{C_YEL}{name:<16}{C_RST} {C_DIM}{'\u2500':>8}{C_RST}  {desc}")
            else:
                line = (f"  {C_CYAN}\u2502{C_RST} {C_DIM}{step}.{C_RST}  "
                        f"{C_YEL}{name:<16}{C_RST} {C_DIM}{ms:>6.1f}ms{C_RST}  "
                        f"{C_GRN}\u2192{C_RST} {desc}")
            print(line)
            self.output.append(f"[TRACE] {step}. {name:<16} {ms:>6.1f}ms  \u2192 {desc}")

        n_steps = len(traces) - 1
        footer = (f"  {C_CYAN}\u2514\u2500 {n_steps} steps \u00b7 {total_ms:.1f}ms total "
                  f"\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500{C_RST}")
        print(footer)
        self.output.append(f"[TRACE] {n_steps} steps \u00b7 {total_ms:.1f}ms total")

    # ── Call / Access Evaluation ─────────────────────────────
    def _eval_FuncCall(self, node: FuncCall, env):
        func = env.get(node.name)
        # Struct constructor call: Point(10, 20)
        if isinstance(func, MOLStructDef):
            args = [self._eval(a, env) for a in node.args]
            if len(args) != len(func.field_names):
                raise MOLRuntimeError(
                    f"Struct '{func.name}' expects {len(func.field_names)} fields, got {len(args)}"
                )
            field_values = list(zip(func.field_names, args))
            return MOLStructInstance(func, field_values)
        args = [self._eval(a, env) for a in node.args]
        return self._invoke_callable(func, args, node.name)

    def _eval_StructLiteral(self, node: StructLiteral, env):
        """Name { field: value, ... } — create struct instance."""
        sdef = env.get(node.struct_name)
        if not isinstance(sdef, MOLStructDef):
            raise MOLRuntimeError(f"'{node.struct_name}' is not a struct")
        field_values = []
        for key, val_expr in node.fields:
            if key not in sdef.field_names:
                raise MOLRuntimeError(
                    f"Struct '{sdef.name}' has no field '{key}'"
                )
            field_values.append((key, self._eval(val_expr, env)))
        # Fill missing fields with null
        provided = {k for k, _ in field_values}
        for fname in sdef.field_names:
            if fname not in provided:
                field_values.append((fname, None))
        return MOLStructInstance(sdef, field_values)

    def _eval_MethodCall(self, node: MethodCall, env):
        obj = self._eval(node.obj, env)
        args = [self._eval(a, env) for a in node.args]

        # Struct method call — bind self
        if isinstance(obj, MOLStructInstance):
            method_name = node.method
            if method_name in obj._struct_def.methods:
                func = obj._struct_def.methods[method_name]
                call_env = Environment(func.closure_env)
                call_env.set("self", obj)
                # Bind function params, skipping 'self' (already bound)
                param_list = [p for p in func.params if p[0] != "self"]
                for i, param in enumerate(param_list):
                    param_name = param[0]
                    if i < len(args):
                        call_env.set(param_name, args[i])
                    elif len(param) >= 3:
                        call_env.set(param_name, self._eval(param[2], call_env))
                    else:
                        call_env.set(param_name, None)
                try:
                    self._exec_block(func.body, call_env)
                except ReturnSignal as ret:
                    return ret.value
                return None
            raise MOLRuntimeError(
                f"Struct '{obj._struct_def.name}' has no method '{method_name}'"
            )

        # Generator methods
        if isinstance(obj, MOLGenerator):
            if node.method == "to_list":
                return obj.to_list()
            if node.method == "next":
                try:
                    return next(obj)
                except StopIteration:
                    return None

        # Try native Python method
        method = getattr(obj, node.method, None)
        if method and callable(method):
            return method(*args)

        # List built-in methods
        if isinstance(obj, list):
            if node.method == "push":
                obj.append(args[0])
                return obj
            if node.method == "pop":
                return obj.pop()
            if node.method == "length":
                return len(obj)

        # String methods
        if isinstance(obj, str):
            if node.method == "length":
                return len(obj)

        raise MOLRuntimeError(f"No method '{node.method}' on {type(obj).__name__}")

    def _eval_FieldAccess(self, node: FieldAccess, env):
        obj = self._eval(node.obj, env)

        # Struct field access
        if isinstance(obj, MOLStructInstance):
            return obj.get_field(node.field_name)

        # Dict field access
        if isinstance(obj, dict) and node.field_name in obj:
            return obj[node.field_name]

        # Object attribute access
        if hasattr(obj, node.field_name):
            return getattr(obj, node.field_name)

        raise MOLRuntimeError(f"No field '{node.field_name}' on {type(obj).__name__}")

    def _eval_IndexAccess(self, node: IndexAccess, env):
        obj = self._eval(node.obj, env)
        idx = self._eval(node.index, env)
        try:
            if isinstance(obj, dict):
                return obj.get(idx)  # Returns None for missing keys
            return obj[idx] if isinstance(idx, str) else obj[int(idx)]
        except (IndexError, KeyError, TypeError) as e:
            raise MOLRuntimeError(f"Index error: {e}")

    # ── Helpers ──────────────────────────────────────────────
    def _truthy(self, value) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, list):
            return len(value) > 0
        return True

    def _to_string(self, value) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, float):
            if value == int(value):
                return str(int(value))
            return str(value)
        if isinstance(value, (Thought, Memory, Node, Stream,
                              Document, Chunk, Embedding, VectorStore)):
            return value.mol_repr()
        return str(value)

    def _safe_div(self, a, b):
        if b == 0:
            raise MOLRuntimeError("Division by zero")
        result = a / b
        if isinstance(a, int) and isinstance(b, int) and result == int(result):
            return int(result)
        return result

    def _check_type(self, value, type_name: str, var_name: str):
        """Enforce MOL's type constraints (safety rail)."""
        type_checks = {
            "Number": lambda v: isinstance(v, (int, float)),
            "Text": lambda v: isinstance(v, str),
            "Bool": lambda v: isinstance(v, bool),
            "List": lambda v: isinstance(v, list),
            "Thought": lambda v: isinstance(v, Thought),
            "Memory": lambda v: isinstance(v, Memory),
            "Node": lambda v: isinstance(v, Node),
            "Stream": lambda v: isinstance(v, Stream),
            "Document": lambda v: isinstance(v, Document),
            "Chunk": lambda v: isinstance(v, Chunk),
            "Embedding": lambda v: isinstance(v, Embedding),
            "VectorStore": lambda v: isinstance(v, VectorStore),
        }
        checker = type_checks.get(type_name)
        if checker and not checker(value):
            raise MOLTypeError(
                f"Type error: '{var_name}' expected {type_name}, "
                f"got {type(value).__name__}"
            )
