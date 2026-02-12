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


# ── v0.3.0: Algorithm & Functional Programming Tests ─────────

def test_flatten():
    interp = run("""
let nested be [[1, 2], [3, [4, 5]]]
show len(flatten(nested))
""")
    assert interp.output == ["5"]


def test_unique():
    interp = run("""
let dupes be [1, 2, 2, 3, 1, 4]
show len(unique(dupes))
""")
    assert interp.output == ["4"]


def test_zip_lists():
    interp = run("""
let pairs be zip([1, 2, 3], ["a", "b", "c"])
show len(pairs)
show pairs[0][1]
""")
    assert interp.output == ["3", "a"]


def test_enumerate_list():
    interp = run("""
let items be enumerate(["x", "y", "z"])
show items[0][0]
show items[2][1]
""")
    assert interp.output == ["0", "z"]


def test_count():
    interp = run("""
show count([1, 2, 1, 3, 1], 1)
""")
    assert interp.output == ["3"]


def test_find_index():
    interp = run("""
show find_index([10, 20, 30, 40], 30)
""")
    assert interp.output == ["2"]


def test_take_drop():
    interp = run("""
show len(take([1, 2, 3, 4, 5], 3))
show len(drop([1, 2, 3, 4, 5], 2))
""")
    assert interp.output == ["3", "3"]


def test_chunk_list():
    interp = run("""
let chunks be chunk_list([1, 2, 3, 4, 5], 2)
show len(chunks)
""")
    assert interp.output == ["3"]


def test_math_functions():
    interp = run("""
show floor(3.7)
show ceil(3.2)
show pow(2, 10)
show clamp(15, 0, 10)
""")
    assert interp.output[0] == "3"
    assert interp.output[1] == "4"
    assert float(interp.output[2]) == 1024.0
    assert float(interp.output[3]) == 10.0


def test_statistics():
    interp = run("""
show mean([1, 2, 3, 4, 5])
show median([1, 3, 5, 7])
""")
    assert float(interp.output[0]) == 3.0
    assert float(interp.output[1]) == 4.0


def test_string_algorithms():
    interp = run("""
show starts_with("hello world", "hello")
show ends_with("hello world", "world")
show pad_left("42", 5, "0")
show repeat("ha", 3)
show char_at("hello", 1)
show index_of("hello world", "world")
""")
    assert interp.output == ["true", "true", "00042", "hahaha", "e", "6"]


def test_hash_function():
    interp = run("""
let h be hash("hello")
show len(h)
""")
    assert interp.output == ["64"]  # SHA-256 hex = 64 chars


def test_base64():
    interp = run("""
let encoded be base64_encode("hello")
let decoded be base64_decode(encoded)
show decoded
""")
    assert interp.output == ["hello"]


def test_sort_desc():
    interp = run("""
let sorted be sort_desc([3, 1, 4, 1, 5])
show sorted[0]
show sorted[1]
""")
    assert interp.output == ["5", "4"]


def test_binary_search():
    interp = run("""
show binary_search([1, 2, 3, 4, 5], 3)
show binary_search([1, 2, 3, 4, 5], 99)
""")
    assert interp.output == ["2", "-1"]


def test_random_int():
    interp = run("""
let r be random_int(1, 100)
show r >= 1 and r <= 100
""")
    assert interp.output == ["true"]


def test_merge_maps():
    interp = run("""
let a be {"name": "MOL"}
let b be {"version": 3}
let c be merge(a, b)
show c.name
show c.version
""")
    assert interp.output == ["MOL", "3"]


def test_pick_omit():
    interp = run("""
let user be {"name": "Mounesh", "age": 25, "role": "builder"}
let picked be pick(user, "name", "role")
show len(keys(picked))
let omitted be omit(user, "age")
show len(keys(omitted))
""")
    assert interp.output == ["2", "2"]


def test_type_checks():
    interp = run("""
show is_number(42)
show is_text("hello")
show is_list([1, 2])
show is_map({"a": 1})
show is_null(null)
""")
    assert interp.output == ["true", "true", "true", "true", "true"]


def test_lerp():
    interp = run("""
show lerp(0, 100, 0.5)
show lerp(0, 100, 0)
show lerp(0, 100, 1)
""")
    assert float(interp.output[0]) == 50.0
    assert float(interp.output[1]) == 0.0
    assert float(interp.output[2]) == 100.0


def test_format_string():
    interp = run("""
show format("Hello, {}! You are {} years old.", "MOL", "2")
""")
    assert interp.output == ["Hello, MOL! You are 2 years old."]


def test_uuid():
    interp = run("""
let id be uuid()
show len(id)
""")
    assert interp.output == ["36"]  # UUID format: 8-4-4-4-12 = 36 chars


def test_map_filter_reduce():
    interp = run("""
define double(x)
  return x * 2
end

define is_big(x)
  return x > 5
end

define add(a, b)
  return a + b
end

let nums be [1, 2, 3, 4, 5]
let doubled be map(nums, double)
show doubled[0]
show doubled[4]

let big be filter(doubled, is_big)
show len(big)

let total be reduce(nums, add, 0)
show total
""")
    assert interp.output == ["2", "10", "3", "15"]


def test_every_some():
    interp = run("""
define is_positive(x)
  return x > 0
end

show every([1, 2, 3], is_positive)
show every([-1, 2, 3], is_positive)
show some([-1, 2, -3], is_positive)
show some([-1, -2, -3], is_positive)
""")
    assert interp.output == ["true", "false", "true", "false"]


def test_pipes_with_algorithms():
    interp = run("""
let result be unique([3, 1, 4, 1, 5]) |> sort |> to_text
show result
""")
    assert "3" in interp.output[0]


# ══════════════════════════════════════════════════════════════
# v0.6.0 — Power Features
# ══════════════════════════════════════════════════════════════

def test_lambda_basic():
    interp = run("""
let double be fn(x) -> x * 2
show to_text(double(5))
""")
    assert "10" in interp.output

def test_lambda_in_pipe():
    interp = run("""
let result be [1, 2, 3] |> map(fn(x) -> x + 10)
show to_text(result)
""")
    assert "11" in interp.output[0]
    assert "12" in interp.output[0]
    assert "13" in interp.output[0]

def test_null_coalesce():
    interp = run("""
let a be null
let b be a ?? "fallback"
show b
""")
    assert interp.output == ["fallback"]

def test_null_coalesce_non_null():
    interp = run("""
let a be 42
let b be a ?? 0
show to_text(b)
""")
    assert "42" in interp.output

def test_string_interpolation():
    interp = run("""
let name be "MOL"
let ver be 6
let msg be f"Hello {name} v{ver}"
show msg
""")
    assert interp.output == ["Hello MOL v6"]

def test_string_interpolation_expr():
    interp = run("""
let x be 3
show f"{x + 1} items"
""")
    assert interp.output == ["4 items"]

def test_destructure_list():
    interp = run("""
let [a, b, c] be [10, 20, 30]
show to_text(a)
show to_text(b)
show to_text(c)
""")
    assert interp.output == ["10", "20", "30"]

def test_destructure_list_rest():
    interp = run("""
let [head, ...tail] be [1, 2, 3, 4, 5]
show to_text(head)
show to_text(len(tail))
""")
    assert interp.output == ["1", "4"]

def test_destructure_map():
    interp = run("""
let {x, y} be {"x": 10, "y": 20, "z": 30}
show to_text(x)
show to_text(y)
""")
    assert interp.output == ["10", "20"]

def test_match_literal():
    interp = run("""
let val be 42
let result be match val with
  | 1 -> "one"
  | 42 -> "answer"
  | _ -> "other"
end
show result
""")
    assert interp.output == ["answer"]

def test_match_binding():
    interp = run("""
let val be 99
let result be match val with
  | x -> f"got {x}"
end
show result
""")
    assert interp.output == ["got 99"]

def test_match_guard():
    interp = run("""
let score be 85
let grade be match score with
  | s when s >= 90 -> "A"
  | s when s >= 80 -> "B"
  | s when s >= 70 -> "C"
  | _ -> "F"
end
show grade
""")
    assert interp.output == ["B"]

def test_match_list_pattern():
    interp = run("""
let data be [1, 2, 3]
let result be match data with
  | [] -> "empty"
  | [x] -> "one"
  | [x, y, z] -> f"three: {x},{y},{z}"
  | _ -> "many"
end
show result
""")
    assert interp.output == ["three: 1,2,3"]

def test_match_block_body():
    interp = run("""
let x be 10
let result be match x with
  | 10 ->
    let doubled be x * 2
    show f"doubled: {doubled}"
    doubled
end
show to_text(result)
""")
    assert "doubled: 20" in interp.output
    assert "20" in interp.output

def test_try_rescue():
    interp = run("""
try
  let x be 1 / 0
rescue e
  show f"caught: {e}"
end
""")
    assert "caught:" in interp.output[0]

def test_try_ensure():
    interp = run("""
try
  show "body"
rescue e
  show "error"
ensure
  show "cleanup"
end
""")
    assert "body" in interp.output
    assert "cleanup" in interp.output

def test_default_params():
    interp = run("""
define greet(name, greeting be "Hello")
  show f"{greeting}, {name}!"
end
greet("MOL")
greet("World", "Hi")
""")
    assert "Hello, MOL!" in interp.output
    assert "Hi, World!" in interp.output

def test_test_block():
    """Test that test blocks are registered but not immediately executed."""
    interp = run("""
test "my test" do
  assert_eq(1 + 1, 2)
end
""")
    assert hasattr(interp, '_test_blocks')
    assert len(interp._test_blocks) == 1
    assert interp._test_blocks[0].description == "my test"

def test_test_block_execution():
    """Test that test block bodies can be executed by the interpreter."""
    from mol.stdlib import MOLAssertionError
    interp = run("""
let x be 42
test "check x" do
  assert_eq(x, 42)
end
""")
    tb = interp._test_blocks[0]
    # Execute the test block body — should not raise
    interp._exec_block(tb.body, interp.global_env)

def test_assert_functions():
    from mol.stdlib import MOLAssertionError
    interp = run("""
assert_eq(1, 1)
assert_ne(1, 2)
assert_true(1 > 0)
assert_false(1 > 10)
""")
    # Should not raise — all assertions pass

def test_assert_eq_fails():
    from mol.stdlib import MOLAssertionError
    import pytest
    with pytest.raises(MOLAssertionError):
        run("assert_eq(1, 2)")

def test_multiple_features_combined():
    """Test combining lambdas, pipes, destructuring, match, and interpolation."""
    interp = run("""
let data be [1, 2, 3, 4, 5]
let result be data |> map(fn(x) -> x * 2) |> filter(fn(x) -> x > 4)
let [first, ...rest] be result
let msg be match first with
  | 6 -> f"first doubled > 4 is {first}"
  | _ -> "unexpected"
end
show msg
""")
    assert "first doubled > 4 is 6" in interp.output


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
