"""
MOL Playground — Online compiler and runner for MOL language.
FastAPI backend that executes MOL code safely and returns results.
"""

import io
import re
import sys
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Add parent to path so we can import mol
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mol.parser import parse
from mol.interpreter import Interpreter

app = FastAPI(title="MOL Playground", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

EXAMPLE_PROGRAMS = {
    "hello": 'show "Hello from MOL!"\nshow "Welcome to the playground!"',
    "variables": 'let name be "IntraMind"\nlet score : Number be 42\nlet items be [1, 2, 3, 4, 5]\n\nshow "Name: " + name\nshow "Score: " + to_text(score)\nshow "Items: " + to_text(items)\nshow "Sum: " + to_text(sum(items))',
    "pipeline": 'let data be "  Hello, MOL World!  "\n\nlet result be data |> trim |> upper |> split(" ")\n\nshow result',
    "functions": 'define factorial(n)\n  if n <= 1 then\n    return 1\n  end\n  return n * factorial(n - 1)\nend\n\nfor i in range(10) do\n  show to_text(i) + "! = " + to_text(factorial(i))\nend',
    "rag_pipeline": 'let doc be Document("demo.txt", "Machine learning enables computers to learn from data. Deep learning uses neural networks with many layers.")\n\nlet index be doc |> chunk(50) |> embed |> store("demo")\n\nshow index\n\nlet results be retrieve("neural networks", "demo", 2)\nshow results',
    "algorithms": 'let numbers be [5, 3, 8, 1, 9, 2, 7, 4, 6, 10]\n\nshow "Original: " + to_text(numbers)\nshow "Sorted: " + to_text(sort(numbers))\nshow "Reversed: " + to_text(sort_desc(numbers))\nshow "Mean: " + to_text(mean(numbers))\nshow "Median: " + to_text(median(numbers))\nshow "Stdev: " + to_text(stdev(numbers))\n\ndefine is_even(n)\n  return n % 2 is 0\nend\n\nshow "Evens: " + to_text(filter(numbers, is_even))\nshow "Sum of squares: " + to_text(sum(map(numbers, square)))\n\ndefine square(x)\n  return x * x\nend',
    "domain_types": 'let thought be Thought("AI will transform computing", 0.92)\nshow thought\nshow "Confidence: " + to_text(thought.confidence)\n\nlet mem be Memory("session", "playground demo")\nshow mem\n\nlet node be Node("cortex", 0.8)\nlink node to Node("synapse", 0.5)\nevolve node\nshow node',
    "data_processing": 'let users be [\n  {"name": "Alice", "age": 30},\n  {"name": "Bob", "age": 25},\n  {"name": "Charlie", "age": 35}\n]\n\nfor user in users do\n  show user["name"] + " is " + to_text(user["age"]) + " years old"\nend\n\nlet config be {"host": "localhost", "port": 8080, "debug": true}\nshow "Config: " + to_json(config)\nshow "Keys: " + to_text(keys(config))',
}

MAX_EXECUTION_TIME = 5  # seconds
MAX_OUTPUT_SIZE = 50000  # characters


@app.post("/api/run")
async def run_code(request: Request):
    """Execute MOL code and return the output."""
    body = await request.json()
    code = body.get("code", "")

    if not code.strip():
        return JSONResponse({"output": "", "error": "No code provided", "time": 0})

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    start_time = time.time()
    error = None
    
    try:
        ast = parse(code)
        interp = Interpreter(trace=True)

        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            interp.run(ast)

    except Exception as e:
        error = f"{type(e).__name__}: {e}"

    elapsed = time.time() - start_time
    output = stdout_capture.getvalue()

    # Strip ANSI escape codes for clean web display
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    output = ansi_escape.sub('', output)

    # Truncate if too large
    if len(output) > MAX_OUTPUT_SIZE:
        output = output[:MAX_OUTPUT_SIZE] + "\n... (output truncated)"

    return JSONResponse({
        "output": output,
        "error": error,
        "time": round(elapsed * 1000, 2),  # ms
    })


@app.get("/api/examples")
async def get_examples():
    """Return the list of example programs."""
    return JSONResponse({
        name: {"name": name.replace("_", " ").title(), "code": code}
        for name, code in EXAMPLE_PROGRAMS.items()
    })


@app.get("/api/version")
async def get_version():
    from mol import __version__
    return JSONResponse({"version": __version__})


@app.get("/", response_class=HTMLResponse)
async def playground():
    """Serve the MOL Playground frontend."""
    return PLAYGROUND_HTML


# ═══════════════════════════════════════════════════════════
#  FRONTEND — Single-file HTML/CSS/JS playground
# ═══════════════════════════════════════════════════════════

PLAYGROUND_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MOL Playground</title>
<style>
  :root {
    --bg: #0f0d1a;
    --surface: #1a1726;
    --surface2: #231f33;
    --border: #2d2844;
    --text: #e2dff0;
    --muted: #8b85a0;
    --purple: #7c3aed;
    --pink: #ec4899;
    --green: #10b981;
    --orange: #f59e0b;
    --red: #ef4444;
    --blue: #3b82f6;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }
  
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--text);
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* ── Header ─────────────────────────────── */
  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0.6rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .logo h1 {
    font-size: 1.3rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--purple), var(--pink));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .logo span {
    font-size: 0.7rem;
    color: var(--muted);
    padding: 2px 8px;
    background: var(--surface2);
    border-radius: 10px;
    border: 1px solid var(--border);
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 0.8rem;
  }

  .btn {
    padding: 0.4rem 1rem;
    border: none;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }

  .btn-run {
    background: var(--green);
    color: #fff;
  }
  .btn-run:hover { background: #0d9668; }
  .btn-run.running { background: var(--orange); pointer-events: none; }

  .btn-share {
    background: var(--surface2);
    color: var(--text);
    border: 1px solid var(--border);
  }
  .btn-share:hover { border-color: var(--purple); }

  select {
    background: var(--surface2);
    color: var(--text);
    border: 1px solid var(--border);
    padding: 0.4rem 0.6rem;
    border-radius: 6px;
    font-size: 0.8rem;
    cursor: pointer;
  }

  /* ── Main ───────────────────────────────── */
  main {
    flex: 1;
    display: flex;
    overflow: hidden;
  }

  .panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .panel-header {
    background: var(--surface);
    padding: 0.4rem 1rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
  }

  .divider {
    width: 3px;
    background: var(--border);
    cursor: col-resize;
    flex-shrink: 0;
  }
  .divider:hover { background: var(--purple); }

  /* ── Editor ─────────────────────────────── */
  #editor {
    flex: 1;
    background: var(--bg);
    color: var(--text);
    font-family: 'JetBrains Mono', 'Source Code Pro', 'Fira Code', monospace;
    font-size: 13px;
    line-height: 1.6;
    padding: 1rem;
    border: none;
    outline: none;
    resize: none;
    tab-size: 2;
    overflow: auto;
  }

  /* ── Output ─────────────────────────────── */
  #output {
    flex: 1;
    background: var(--bg);
    font-family: 'JetBrains Mono', 'Source Code Pro', monospace;
    font-size: 12.5px;
    line-height: 1.6;
    padding: 1rem;
    overflow: auto;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .output-success { color: var(--green); }
  .output-error { color: var(--red); }
  .output-trace { color: var(--purple); opacity: 0.9; }
  .output-info { color: var(--muted); font-style: italic; }

  .time-badge {
    font-size: 0.7rem;
    padding: 1px 6px;
    border-radius: 8px;
    background: var(--surface2);
    color: var(--green);
  }

  /* ── Footer ─────────────────────────────── */
  footer {
    background: var(--surface);
    border-top: 1px solid var(--border);
    padding: 0.3rem 1.5rem;
    font-size: 0.7rem;
    color: var(--muted);
    display: flex;
    justify-content: space-between;
    flex-shrink: 0;
  }

  footer a { color: var(--purple); text-decoration: none; }
  footer a:hover { text-decoration: underline; }

  /* ── Keyboard shortcut hint ─────────────── */
  kbd {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 3px;
    padding: 0 4px;
    font-size: 0.7rem;
    font-family: inherit;
  }

  @media (max-width: 768px) {
    main { flex-direction: column; }
    .divider { width: 100%; height: 3px; cursor: row-resize; }
  }
</style>
</head>
<body>

<header>
  <div class="logo">
    <h1>MOL</h1>
    <span id="version">v0.3.0</span>
  </div>
  <div class="header-right">
    <select id="examples" onchange="loadExample(this.value)">
      <option value="">Load Example...</option>
    </select>
    <button class="btn btn-run" id="runBtn" onclick="runCode()">
      ▶ Run <kbd>Ctrl+Enter</kbd>
    </button>
    <button class="btn btn-share" onclick="shareCode()">
      ↗ Share
    </button>
    <a class="btn btn-share" href="https://github.com/crux-ecosystem/mol-lang" target="_blank">
      GitHub
    </a>
  </div>
</header>

<main>
  <div class="panel">
    <div class="panel-header">
      <span>Editor</span>
      <span style="color:var(--purple)">mol</span>
    </div>
    <textarea id="editor" spellcheck="false" placeholder="-- Write MOL code here...
-- Press Ctrl+Enter to run

show &quot;Hello from MOL!&quot;
"></textarea>
  </div>

  <div class="divider" id="divider"></div>

  <div class="panel">
    <div class="panel-header">
      <span>Output</span>
      <span id="timeDisplay"></span>
    </div>
    <div id="output">
      <span class="output-info">Press ▶ Run or Ctrl+Enter to execute your code.</span>
    </div>
  </div>
</main>

<footer>
  <span>MOL — The Cognitive Programming Language · Built for IntraMind by CruxLabx</span>
  <span>
    <a href="https://github.com/crux-ecosystem/mol-lang">Documentation</a> ·
    Creator: Mounesh Kodi
  </span>
</footer>

<script>
const editor = document.getElementById('editor');
const output = document.getElementById('output');
const runBtn = document.getElementById('runBtn');
const timeDisplay = document.getElementById('timeDisplay');
const examplesSelect = document.getElementById('examples');

// Load examples
fetch('/api/examples')
  .then(r => r.json())
  .then(examples => {
    for (const [key, val] of Object.entries(examples)) {
      const opt = document.createElement('option');
      opt.value = key;
      opt.textContent = val.name;
      examplesSelect.appendChild(opt);
    }
    window._examples = examples;
  });

// Load default code
editor.value = `-- Welcome to MOL Playground!
-- The cognitive programming language with auto-tracing pipelines

show "Hello from MOL!"

let numbers be [1, 2, 3, 4, 5]
show "Sum: " + to_text(sum(numbers))
show "Mean: " + to_text(mean(numbers))

-- Try the pipe operator:
let result be "  hello world  " |> trim |> upper |> split(" ")
show result`;

function loadExample(key) {
  if (key && window._examples && window._examples[key]) {
    editor.value = window._examples[key].code;
    examplesSelect.value = '';
  }
}

async function runCode() {
  const code = editor.value;
  if (!code.trim()) return;

  runBtn.classList.add('running');
  runBtn.innerHTML = '⏳ Running...';
  output.innerHTML = '<span class="output-info">Executing...</span>';
  timeDisplay.innerHTML = '';

  try {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    });
    const data = await res.json();

    let html = '';

    if (data.output) {
      // Highlight trace lines
      const lines = data.output.split('\n');
      for (const line of lines) {
        if (line.includes('Pipeline Trace') || line.includes('│') || line.includes('└') || line.includes('┌')) {
          html += `<span class="output-trace">${escapeHtml(line)}\n</span>`;
        } else {
          html += `<span class="output-success">${escapeHtml(line)}\n</span>`;
        }
      }
    }

    if (data.error) {
      html += `<span class="output-error">\n✗ ${escapeHtml(data.error)}</span>`;
    }

    if (!data.output && !data.error) {
      html = '<span class="output-info">Program executed with no output.</span>';
    }

    output.innerHTML = html;
    timeDisplay.innerHTML = `<span class="time-badge">⚡ ${data.time}ms</span>`;

  } catch (err) {
    output.innerHTML = `<span class="output-error">Connection error: ${err.message}</span>`;
  }

  runBtn.classList.remove('running');
  runBtn.innerHTML = '▶ Run <kbd>Ctrl+Enter</kbd>';
}

function shareCode() {
  const code = editor.value;
  const encoded = btoa(encodeURIComponent(code));
  const url = window.location.origin + '?code=' + encoded;
  navigator.clipboard.writeText(url).then(() => {
    alert('Share link copied to clipboard!');
  });
}

function escapeHtml(text) {
  return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Load shared code from URL
const params = new URLSearchParams(window.location.search);
if (params.has('code')) {
  try {
    editor.value = decodeURIComponent(atob(params.get('code')));
  } catch (e) {}
}

// Keyboard shortcuts
editor.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    runCode();
  }
  // Tab inserts 2 spaces
  if (e.key === 'Tab') {
    e.preventDefault();
    const start = editor.selectionStart;
    editor.value = editor.value.substring(0, start) + '  ' + editor.value.substring(editor.selectionEnd);
    editor.selectionStart = editor.selectionEnd = start + 2;
  }
});

// Fetch version
fetch('/api/version').then(r => r.json()).then(d => {
  document.getElementById('version').textContent = 'v' + d.version;
});
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    print("\n  🟣 MOL Playground running at http://localhost:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
