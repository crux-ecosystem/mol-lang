"""
MOL WASM/Browser Compiler — Compile MOL to run in-browser natively
===================================================================

Transpiles MOL source → JavaScript + bundles with the MOL runtime
to produce standalone HTML/JS that runs in any browser.

Targets:
  browser   →  Self-contained HTML with embedded JS (default)
  js        →  Standalone JavaScript file with runtime
  node      →  Node.js-compatible JavaScript module

Usage:
  mol build program.mol                   →  dist/program.html
  mol build program.mol --target js       →  dist/program.js
  mol build program.mol --target node     →  dist/program.mjs
  mol build program.mol -o output.html    →  output.html
"""

import os
import re
import sys
from pathlib import Path

from mol import __version__ as MOL_VERSION
from mol.parser import parse
from mol.transpiler import JavaScriptTranspiler


# ── ANSI Colors ──────────────────────────────────────────────
class C:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    DIM = "\033[2m"
    RESET = "\033[0m"


# ── Runtime Loader ───────────────────────────────────────────

def _get_runtime_js() -> str:
    """Load the MOL JavaScript runtime."""
    runtime_path = Path(__file__).parent / "runtime.js"
    if not runtime_path.exists():
        raise FileNotFoundError(f"MOL runtime not found at {runtime_path}")
    return runtime_path.read_text()


def _minify_js(code: str) -> str:
    """Basic JavaScript minification."""
    # Remove single-line comments (but not URLs)
    code = re.sub(r'(?<!:)\/\/.*$', '', code, flags=re.MULTILINE)
    # Remove multi-line comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # Collapse whitespace
    code = re.sub(r'\n\s*\n', '\n', code)
    # Remove leading/trailing whitespace on lines
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    return '\n'.join(lines)


# ── Browser HTML Template ────────────────────────────────────

BROWSER_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — MOL Program</title>
  <style>
    :root {{
      --bg: #0d1117; --fg: #e6edf3; --accent: #58a6ff;
      --green: #3fb950; --yellow: #d29922; --red: #f85149;
      --surface: #161b22; --border: #30363d;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
      background: var(--bg); color: var(--fg);
      display: flex; flex-direction: column; height: 100vh;
    }}
    header {{
      padding: 12px 20px; background: var(--surface);
      border-bottom: 1px solid var(--border);
      display: flex; align-items: center; gap: 12px;
    }}
    header .logo {{
      font-size: 1.1rem; font-weight: 700; color: var(--accent);
    }}
    header .meta {{
      font-size: 0.75rem; color: #8b949e;
    }}
    header .status {{
      margin-left: auto; font-size: 0.8rem;
    }}
    header .status.ok {{ color: var(--green); }}
    header .status.err {{ color: var(--red); }}
    #console {{
      flex: 1; overflow-y: auto; padding: 16px 20px;
      font-size: 0.9rem; line-height: 1.6;
    }}
    .line {{ margin-bottom: 2px; white-space: pre-wrap; word-break: break-all; }}
    .line-output {{ color: var(--fg); }}
    .line-error {{ color: var(--red); }}
    .line-trace {{ color: var(--yellow); font-style: italic; }}
    footer {{
      padding: 8px 20px; background: var(--surface);
      border-top: 1px solid var(--border);
      font-size: 0.7rem; color: #8b949e;
      display: flex; justify-content: space-between;
    }}
  </style>
</head>
<body>
  <header>
    <span class="logo">MOL</span>
    <span class="meta">{title} &middot; v{version}</span>
    <span id="status" class="status ok">Ready</span>
  </header>
  <div id="console"></div>
  <footer>
    <span>Compiled from MOL &middot; {filename}</span>
    <span id="timing"></span>
  </footer>

<script>
// ─── Console Override ──────────────────────────────────────
(function() {{
  const con = document.getElementById('console');
  const statusEl = document.getElementById('status');
  const timingEl = document.getElementById('timing');
  const origLog = console.log;

  function addLine(text, cls) {{
    const div = document.createElement('div');
    div.className = 'line ' + cls;
    div.textContent = text;
    con.appendChild(div);
    con.scrollTop = con.scrollHeight;
  }}

  console.log = function(...args) {{
    origLog.apply(console, args);
    const text = args.map(a => {{
      if (typeof a === 'object') return JSON.stringify(a);
      return String(a);
    }}).join(' ');
    addLine(text, 'line-output');
  }};

  console.error = function(...args) {{
    const text = args.map(a => String(a)).join(' ');
    addLine('ERROR: ' + text, 'line-error');
  }};

  // ─── MOL Runtime ──────────────────────────────────────────
  {runtime}

  // ─── Compiled MOL Program ─────────────────────────────────
  const __mol_start = performance.now();
  try {{
    {program}
    const elapsed = (performance.now() - __mol_start).toFixed(1);
    statusEl.textContent = 'Done';
    statusEl.className = 'status ok';
    timingEl.textContent = elapsed + 'ms';
  }} catch(err) {{
    console.error(err.message || err);
    statusEl.textContent = 'Error';
    statusEl.className = 'status err';
  }}
}})();
</script>
</body>
</html>
"""


# ── Node.js Template ─────────────────────────────────────────

NODE_TEMPLATE = """\
#!/usr/bin/env node
// MOL Compiled Program — Node.js target
// Generated by MOL v{version}
// Source: {filename}

{runtime}

// ─── Program ────────────────────────────────────────────────
{program}
"""


# ── Standalone JS Template ───────────────────────────────────

JS_TEMPLATE = """\
// MOL Compiled Program
// Generated by MOL v{version} — {filename}
// Run in browser or Node.js

(function() {{
  "use strict";

  {runtime}

  // ─── Program ──────────────────────────────────────────────
  {program}
}})();
"""


# ── Compiler Pipeline ────────────────────────────────────────

def compile_mol(source: str, filename: str = "program.mol") -> str:
    """Transpile MOL source code to JavaScript."""
    ast = parse(source)
    transpiler = JavaScriptTranspiler()
    js_code = transpiler.transpile(ast)
    return js_code


def build_browser(source: str, filename: str = "program.mol", minify: bool = False) -> str:
    """Build a self-contained HTML file with embedded JS."""
    js_code = compile_mol(source, filename)
    runtime = _get_runtime_js()

    if minify:
        runtime = _minify_js(runtime)
        js_code = _minify_js(js_code)

    title = Path(filename).stem.replace("_", " ").replace("-", " ").title()

    return BROWSER_TEMPLATE.format(
        title=title,
        version=MOL_VERSION,
        filename=filename,
        runtime=runtime,
        program=js_code,
    )


def build_js(source: str, filename: str = "program.mol", minify: bool = False) -> str:
    """Build a standalone JavaScript file."""
    js_code = compile_mol(source, filename)
    runtime = _get_runtime_js()

    if minify:
        runtime = _minify_js(runtime)
        js_code = _minify_js(js_code)

    return JS_TEMPLATE.format(
        version=MOL_VERSION,
        filename=filename,
        runtime=runtime,
        program=js_code,
    )


def build_node(source: str, filename: str = "program.mol", minify: bool = False) -> str:
    """Build a Node.js-compatible JavaScript file."""
    js_code = compile_mol(source, filename)
    runtime = _get_runtime_js()

    if minify:
        runtime = _minify_js(runtime)
        js_code = _minify_js(js_code)

    return NODE_TEMPLATE.format(
        version=MOL_VERSION,
        filename=filename,
        runtime=runtime,
        program=js_code,
    )


# ── CLI Command ──────────────────────────────────────────────

def cmd_build(args):
    """Handle 'mol build' command."""
    filepath = args.file
    target = args.target
    output = args.output
    minify = args.minify

    if not os.path.exists(filepath):
        print(f"{C.RED}Error: File not found: {filepath}{C.RESET}")
        sys.exit(1)

    with open(filepath) as f:
        source = f.read()

    filename = os.path.basename(filepath)
    stem = Path(filepath).stem

    print(f"{C.CYAN}Compiling {filename} → {target}...{C.RESET}")

    try:
        if target == "browser":
            result = build_browser(source, filename, minify)
            ext = ".html"
        elif target == "js":
            result = build_js(source, filename, minify)
            ext = ".js"
        elif target == "node":
            result = build_node(source, filename, minify)
            ext = ".mjs"
        else:
            print(f"{C.RED}Unknown target: {target}{C.RESET}")
            sys.exit(1)

        # Determine output path
        if output:
            out_path = Path(output)
        else:
            out_path = Path("dist") / f"{stem}{ext}"

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result)

        size_kb = out_path.stat().st_size / 1024
        print(f"  {C.GREEN}✓{C.RESET} {out_path} ({size_kb:.1f} KB)")

        if target == "browser":
            print(f"\n  {C.DIM}Open in browser: file://{out_path.resolve()}{C.RESET}")
            print(f"  {C.DIM}Or serve:        python3 -m http.server -d {out_path.parent}{C.RESET}")
        elif target == "node":
            print(f"\n  {C.DIM}Run with:  node {out_path}{C.RESET}")

        print(f"\n{C.GREEN}Build complete.{C.RESET}")

    except Exception as e:
        print(f"{C.RED}Build failed: {e}{C.RESET}")
        sys.exit(1)
