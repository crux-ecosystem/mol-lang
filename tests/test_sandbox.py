"""
Tests for MOL Playground Sandbox Security (v0.10.0)
====================================================
Verifies that dangerous functions are blocked in sandbox mode
while safe functions continue to work.
"""

import pytest
import io
from contextlib import redirect_stdout

from mol.parser import parse
from mol.interpreter import Interpreter
from mol.stdlib import MOLSecurityError, SANDBOX_BLOCKED_FUNCTIONS, get_sandbox_stdlib


# ── Helper ───────────────────────────────────────────────────
def run_sandbox(code: str) -> str:
    """Run MOL code in sandbox mode, return captured stdout."""
    ast = parse(code)
    interp = Interpreter(trace=False, sandbox=True)
    buf = io.StringIO()
    with redirect_stdout(buf):
        interp.run(ast)
    return buf.getvalue().strip()


def run_sandbox_error(code: str) -> str:
    """Run MOL code in sandbox mode, return error message."""
    with pytest.raises(MOLSecurityError) as exc_info:
        ast = parse(code)
        interp = Interpreter(trace=False, sandbox=True)
        interp.run(ast)
    return str(exc_info.value)


# ── Sandbox blocks dangerous functions ──────────────────────

class TestSandboxBlocked:
    """All dangerous functions must raise MOLSecurityError in sandbox."""

    def test_read_file_blocked(self):
        err = run_sandbox_error('read_file("/etc/passwd")')
        assert "not available in the playground" in err
        assert "read_file" in err

    def test_write_file_blocked(self):
        err = run_sandbox_error('write_file("/tmp/hack.txt", "pwned")')
        assert "not available in the playground" in err

    def test_delete_file_blocked(self):
        err = run_sandbox_error('delete_file("/etc/hosts")')
        assert "not available in the playground" in err

    def test_append_file_blocked(self):
        err = run_sandbox_error('append_file("/tmp/log", "data")')
        assert "not available in the playground" in err

    def test_list_dir_blocked(self):
        err = run_sandbox_error('list_dir("/")')
        assert "not available in the playground" in err

    def test_make_dir_blocked(self):
        err = run_sandbox_error('make_dir("/tmp/evil")')
        assert "not available in the playground" in err

    def test_file_exists_blocked(self):
        err = run_sandbox_error('file_exists("/etc/passwd")')
        assert "not available in the playground" in err

    def test_file_size_blocked(self):
        err = run_sandbox_error('file_size("/etc/passwd")')
        assert "not available in the playground" in err

    def test_fetch_blocked(self):
        err = run_sandbox_error('fetch("http://169.254.169.254/")')
        assert "not available in the playground" in err

    def test_serve_blocked(self):
        err = run_sandbox_error('serve(9999, fn(r) -> {"status": 200})')
        assert "not available in the playground" in err

    def test_sleep_blocked(self):
        err = run_sandbox_error('sleep(10000)')
        assert "not available in the playground" in err

    def test_channel_blocked(self):
        err = run_sandbox_error('let ch be channel()')
        assert "not available in the playground" in err

    def test_parallel_blocked(self):
        err = run_sandbox_error('parallel([1,2,3], fn(x) -> x * 2)')
        assert "not available in the playground" in err

    def test_panic_blocked(self):
        err = run_sandbox_error('panic("crash")')
        assert "not available in the playground" in err

    def test_load_text_blocked(self):
        err = run_sandbox_error('load_text("secret.txt")')
        assert "not available in the playground" in err

    def test_path_join_blocked(self):
        err = run_sandbox_error('path_join("/etc", "passwd")')
        assert "not available in the playground" in err

    def test_url_encode_blocked(self):
        err = run_sandbox_error('url_encode({"key": "val"})')
        assert "not available in the playground" in err


# ── Safe functions still work in sandbox ─────────────────────

class TestSandboxAllowed:
    """Safe functions must continue to work normally in sandbox."""

    def test_show_works(self):
        assert run_sandbox('show "hello"') == "hello"

    def test_math_works(self):
        assert run_sandbox('show to_text(2 + 3)') == "5"

    def test_string_ops_work(self):
        assert run_sandbox('show upper("hello")') == "HELLO"

    def test_list_ops_work(self):
        assert run_sandbox('show to_text(sort([3,1,2]))') == "[1, 2, 3]"

    def test_map_filter_work(self):
        out = run_sandbox('''
define double(x)
  return x * 2
end
show to_text(map([1,2,3], double))
''')
        assert out == "[2, 4, 6]"

    def test_pipe_works(self):
        out = run_sandbox('show "  hello  " |> trim |> upper')
        assert out == "HELLO"

    def test_structs_work(self):
        out = run_sandbox('struct Point do\n  x, y\nend\nlet p be Point(3, 4)\nshow to_text(p.x) + "," + to_text(p.y)')
        assert out == "3,4"

    def test_hash_works(self):
        out = run_sandbox('show hash("test")')
        assert len(out) == 64  # SHA-256 hex

    def test_uuid_works(self):
        out = run_sandbox('show uuid()')
        assert len(out) == 36  # UUID format

    def test_json_works(self):
        out = run_sandbox('show json_stringify({"a": 1})')
        assert '"a"' in out

    def test_random_works(self):
        out = run_sandbox('show to_text(random_int(1, 100))')
        val = int(out)
        assert 1 <= val <= 100

    def test_mean_works(self):
        out = run_sandbox('show to_text(mean([1,2,3,4,5]))')
        assert "3" in out

    def test_type_checks_work(self):
        assert "rue" in run_sandbox('show to_text(is_number(42))')
        assert "rue" in run_sandbox('show to_text(is_text("hi"))')


# ── get_sandbox_stdlib correctness ───────────────────────────

class TestSandboxStdlib:
    """Verify the sandbox stdlib registry is correct."""

    def test_all_blocked_functions_exist(self):
        """Every function in SANDBOX_BLOCKED_FUNCTIONS must exist in STDLIB."""
        from mol.stdlib import STDLIB
        for name in SANDBOX_BLOCKED_FUNCTIONS:
            assert name in STDLIB, f"'{name}' in SANDBOX_BLOCKED_FUNCTIONS but not in STDLIB"

    def test_sandbox_stdlib_has_all_keys(self):
        """Sandbox stdlib must have same keys as full stdlib."""
        from mol.stdlib import STDLIB
        safe = get_sandbox_stdlib()
        assert set(safe.keys()) == set(STDLIB.keys())

    def test_blocked_funcs_are_replaced(self):
        """Blocked functions in sandbox should raise MOLSecurityError."""
        safe = get_sandbox_stdlib()
        for name in SANDBOX_BLOCKED_FUNCTIONS:
            with pytest.raises(MOLSecurityError):
                safe[name]()  # Call with no args — should raise before arg check

    def test_safe_funcs_not_replaced(self):
        """Non-blocked functions should be the original functions."""
        from mol.stdlib import STDLIB
        safe = get_sandbox_stdlib()
        for name in safe:
            if name not in SANDBOX_BLOCKED_FUNCTIONS:
                assert safe[name] is STDLIB[name], f"'{name}' was incorrectly replaced"
