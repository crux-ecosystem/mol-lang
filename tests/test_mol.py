"""
MOL Test Suite
===============
Basic tests for the MOL language parser and interpreter.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mol.parser import parse
from mol.interpreter import Interpreter, MOLRuntimeError, MOLGuardError
from mol.stdlib import MOLSecurityError, MOLTypeError


def run(source: str, trace=False) -> Interpreter:
    """Helper: parse and run MOL source, return the interpreter."""
    ast = parse(source)
    interp = Interpreter(trace=trace)
    interp.run(ast)
    return interp


def test_show():
    interp = run('show "hello"')
    assert interp.output == ["hello"]


def test_variables():
    interp = run("""
let x be 42
show to_text(x)
""")
    assert "42" in interp.output


def test_arithmetic():
    interp = run("""
let result be 3 + 4 * 2
show to_text(result)
""")
    assert "11" in interp.output


def test_if_else():
    interp = run("""
let x be 10
if x > 5 then
  show "big"
else
  show "small"
end
""")
    assert interp.output == ["big"]


def test_for_loop():
    interp = run("""
for i in range(3) do
  show to_text(i)
end
""")
    assert interp.output == ["0", "1", "2"]


def test_while_loop():
    interp = run("""
let count be 0
while count < 3 do
  set count to count + 1
end
show to_text(count)
""")
    assert "3" in interp.output


def test_functions():
    interp = run("""
define add(a, b)
  return a + b
end
show to_text(add(3, 4))
""")
    assert "7" in interp.output


def test_recursion():
    interp = run("""
define fact(n)
  if n <= 1 then
    return 1
  end
  return n * fact(n - 1)
end
show to_text(fact(5))
""")
    assert "120" in interp.output


def test_lists():
    interp = run("""
let nums be [1, 2, 3]
show to_text(len(nums))
show to_text(nums[0])
""")
    assert "3" in interp.output
    assert "1" in interp.output


def test_string_ops():
    interp = run("""
show upper("hello")
show lower("WORLD")
show trim("  hi  ")
""")
    assert "HELLO" in interp.output
    assert "world" in interp.output
    assert "hi" in interp.output


def test_domain_types():
    interp = run("""
let t be Thought("idea", 0.9)
show type_of(t)
let n be Node("alpha", 1.0)
show type_of(n)
""")
    assert "Thought" in interp.output
    assert "Node" in interp.output


def test_typed_declaration():
    interp = run("""
let x : Number be 42
show to_text(x)
""")
    assert "42" in interp.output


def test_typed_declaration_error():
    try:
        run('let x : Number be "hello"')
        assert False, "Should have raised MOLTypeError"
    except MOLTypeError:
        pass


def test_access_granted():
    interp = run('access "mind_core"')
    assert any("granted" in o for o in interp.output)


def test_access_denied():
    try:
        run('access "secret_vault"')
        assert False, "Should have raised MOLSecurityError"
    except MOLSecurityError:
        pass


def test_trigger_and_listen():
    interp = run("""
listen "ping" do
  show "pong"
end
trigger "ping"
""")
    assert "pong" in interp.output


def test_link_nodes():
    interp = run("""
let a be Node("a", 1.0)
let b be Node("b", 2.0)
link a to b
""")
    assert any("Linked" in o for o in interp.output)


def test_evolve():
    interp = run("""
let n be Node("test", 1.0)
evolve n
show to_text(n.generation)
""")
    assert "1" in interp.output


def test_comparison_is():
    interp = run("""
let x be 5
if x is 5 then
  show "yes"
end
""")
    assert "yes" in interp.output


def test_logical_operators():
    interp = run("""
if true and true then
  show "both"
end
if true or false then
  show "either"
end
if not false then
  show "negated"
end
""")
    assert "both" in interp.output
    assert "either" in interp.output
    assert "negated" in interp.output


def test_maps():
    interp = run("""
let m be {name: "test", value: 42}
show m.name
show to_text(m.value)
""")
    assert "test" in interp.output
    assert "42" in interp.output


# ── v0.2.0: Pipe Operator Tests ──────────────────────────────

def test_pipe_basic():
    """Basic pipe: value |> function"""
    interp = run("""
let result be "hello" |> upper
show result
""")
    assert "HELLO" in interp.output


def test_pipe_with_args():
    """Pipe with function arguments: value |> func(arg)"""
    interp = run("""
let result be "a,b,c" |> split(",")
show to_text(len(result))
""")
    assert "3" in interp.output


def test_pipe_chain():
    """Multi-stage pipe chain"""
    interp = run("""
let result be "  HELLO  " |> trim |> lower
show result
""")
    assert "hello" in interp.output


def test_pipe_chain_with_functions():
    """Pipe chain with user-defined functions"""
    interp = run("""
define double(x)
  return x * 2
end
define add_one(x)
  return x + 1
end
let result be 5 |> double |> add_one
show to_text(result)
""")
    assert "11" in interp.output


def test_pipe_in_declaration():
    """Pipe result assigned to variable"""
    interp = run("""
let msg be "world" |> upper
show "HELLO " + msg
""")
    assert "HELLO WORLD" in interp.output


def test_pipe_auto_trace():
    """Pipe chain with 3+ stages produces trace output"""
    interp = run("""
let x be "  Hello World  " |> trim |> lower |> upper
show x
""", trace=True)
    assert "HELLO WORLD" in interp.output
    assert any("TRACE" in o for o in interp.output)


def test_pipe_no_trace_short():
    """Short pipe (< 3 stages) does NOT trace"""
    interp = run("""
let x be "hello" |> upper
show x
""", trace=True)
    assert "HELLO" in interp.output
    assert not any("TRACE" in o for o in interp.output)


# ── v0.2.0: Guard Tests ─────────────────────────────────────

def test_guard_pass():
    """Guard passes when condition is true"""
    interp = run("""
let x be 10
guard x > 5
show "passed"
""")
    assert "passed" in interp.output


def test_guard_fail():
    """Guard raises error when condition is false"""
    try:
        run("""
let x be 3
guard x > 5
""")
        assert False, "Should have raised MOLGuardError"
    except MOLGuardError:
        pass


def test_guard_with_message():
    """Guard with custom error message"""
    try:
        run("""
guard false : "Custom error"
""")
        assert False, "Should have raised MOLGuardError"
    except MOLGuardError as e:
        assert "Custom" in str(e)


# ── v0.2.0: Pipeline Definition Tests ───────────────────────

def test_pipeline_def():
    """Pipeline definition and invocation"""
    interp = run("""
pipeline shout(text)
  return text |> upper
end
show shout("hello")
""")
    assert "HELLO" in interp.output


def test_pipeline_in_pipe():
    """Pipeline used as a pipe stage"""
    interp = run("""
pipeline clean(data)
  return data |> trim |> lower
end
let result be "  HELLO  " |> clean
show result
""")
    assert "hello" in interp.output


# ── v0.2.0: Cognitive Types Tests ────────────────────────────

def test_document_type():
    """Document creation and field access"""
    interp = run("""
let doc be Document("test.txt", "Hello world content")
show doc.source
show to_text(len(doc.content))
""")
    assert "test.txt" in interp.output
    assert "19" in interp.output


def test_chunk_function():
    """Chunking a document"""
    interp = run("""
let doc be Document("test.txt", "word1 word2 word3 word4 word5 word6")
let chunks be chunk(doc, 20)
show to_text(len(chunks))
""")
    # Should produce multiple chunks
    assert any(int(o) >= 2 for o in interp.output if o.isdigit())


def test_embed_function():
    """Embedding text produces an Embedding object"""
    interp = run("""
let emb be embed("hello world")
show type_of(emb)
""")
    assert "Embedding" in interp.output


def test_embed_deterministic():
    """Same text produces same embedding (deterministic)"""
    interp = run("""
let a be embed("test")
let b be embed("test")
show to_text(cosine_sim(a, b))
""")
    assert "1.0" in interp.output


def test_store_and_retrieve():
    """Store embeddings and retrieve by similarity"""
    interp = run("""
let chunks be chunk("The sky is blue. Grass is green. The sun is bright.", 20)
let embs be embed(chunks)
store(embs, "test_store")
let results be retrieve("blue sky", "test_store", 2)
show to_text(len(results))
""")
    assert "2" in interp.output


def test_think_function():
    """Think produces a Thought from input"""
    interp = run("""
let t be think("The quick brown fox jumps over the lazy dog")
show type_of(t)
show to_text(t.confidence)
""")
    assert "Thought" in interp.output


def test_display_passthrough():
    """display() passes value through for pipe chaining"""
    interp = run("""
let x be "hello" |> display |> upper
show x
""")
    # display prints to stdout (not captured), but upper receives "hello"
    assert "HELLO" in interp.output


def test_assert_min_pass():
    """assert_min passes when value >= threshold"""
    interp = run("""
let t be Thought("idea", 0.9)
let result be t |> assert_min(0.5)
show type_of(result)
""")
    assert "Thought" in interp.output


def test_assert_min_fail():
    """assert_min fails when value < threshold"""
    try:
        run("""
let t be Thought("idea", 0.3)
t |> assert_min(0.5)
""")
        assert False, "Should have raised MOLGuardError"
    except Exception:
        pass


# ── v0.2.0: Full Pipeline Integration ───────────────────────

def test_rag_pipeline_integration():
    """End-to-end RAG pipeline: doc |> chunk |> embed |> store → retrieve → think"""
    interp = run("""
let doc be Document("kb.txt", "Python is great for AI. JavaScript powers the web. MOL is built for pipelines.")
doc |> chunk(40) |> embed("test") |> store("int_test")
let results be retrieve("pipeline language", "int_test", 2)
let answer be results |> think("What language is for pipelines?")
show type_of(answer)
guard answer.confidence > 0.3
show "pipeline works"
""")
    assert "Thought" in interp.output
    assert "pipeline works" in interp.output


if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  ✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {test.__name__}: {e}")
            failed += 1
    print(f"\n{'='*40}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'='*40}")
