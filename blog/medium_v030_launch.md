# MOL v0.3.0: Our Programming Language Now Has an Online Playground, 90+ Functions, and You Can pip install It

*By [Mounesh Kodi](https://medium.com/@kaliyugiheart) — creator of [MOL](https://github.com/crux-ecosystem/mol-lang) at CruxLabx*

---

Two months ago, I introduced MOL — a programming language where pipelines trace themselves automatically. It started as a language experiment inside IntraMind, our cognitive computing platform. Today, it's a real tool you can install and use.

**MOL v0.3.0 is live.** Here's everything that changed.

---

## You Can Now Install MOL in 5 Seconds

```bash
pipx install mol-lang
mol repl
```

That's it. MOL is on [PyPI](https://pypi.org/project/mol-lang/). You get the full interpreter, 90+ standard library functions, the pipe operator with auto-tracing, and all 12 domain types. No configuration, no setup.

Write a file called `hello.mol`:

```
let data be [5, 3, 8, 1, 9, 2, 7]

show "Sorted: " + to_text(sort(data))
show "Mean: " + to_text(mean(data))
show "Median: " + to_text(median(data))

let result be "  hello world  " |> trim |> upper |> split(" ")
show result
```

Run it:

```bash
mol run hello.mol
```

You get the output *and* a pipeline trace showing exactly what happened at each step, with timing.

---

## The Online Playground

Don't want to install anything? **Try MOL in your browser:**

**[▶ http://135.235.138.217:8000](http://135.235.138.217:8000)**

The playground gives you:

- A code editor with 8 built-in examples (hello world, pipelines, RAG, algorithms, domain types, data processing)
- One-click execution with Ctrl+Enter
- Auto-tracing output — you see the pipeline trace rendered in real-time
- Shareable links — send your MOL program to anyone

It's built with FastAPI and deployed on Azure. The whole playground is one Python file — 500 lines of server code serving an embedded HTML/CSS/JS frontend. No build tools, no node_modules, no webpack.

---

## What's New in v0.3.0

### 90+ Standard Library Functions

v0.2.0 had 45 functions. v0.3.0 has **90+**. Here's what we added:

**Functional programming:**
```
let evens be filter([1,2,3,4,5,6], is_even)
let squares be map([1,2,3,4], square)
let total be reduce([1,2,3,4], add, 0)
let pairs be zip([1,2,3], ["a","b","c"])
```

**Math & statistics:**
```
show mean([1, 2, 3, 4, 5])          -- 3.0
show median([1, 2, 3, 4, 5])        -- 3
show stdev([2, 4, 4, 4, 5, 5, 7])   -- 1.399...
show sqrt(144)                       -- 12.0
show clamp(15, 0, 10)               -- 10
```

**Hashing & encoding:**
```
show md5("hello")       -- 5d41402abc4b2a76...
show sha256("hello")    -- 2cf24dba5fb0a30e...
show base64_encode("MOL is cool")
```

**Sorting:**
```
show sort([5, 3, 1, 4])        -- [1, 3, 4, 5]
show sort_desc([5, 3, 1, 4])   -- [5, 4, 3, 1]
show sort_by(users, "age")     -- sorted by field
```

**String utilities, random numbers, type checks, map operations** — all built in, no imports needed.

### Functions and Pipelines Are Now Callable

In v0.2.0, you could define functions and pipelines. In v0.3.0, `MOLFunction` and `MOLPipeline` objects are first-class callable values. You can pass them to `map()`, `filter()`, and `reduce()`:

```
define double(x)
  return x * 2
end

let results be map([1, 2, 3, 4, 5], double)
show results   -- [2, 4, 6, 8, 10]
```

This was the most requested feature from early testers.

---

## The Speed Question

"But it's interpreted! It must be slow!"

We benchmarked it. MOL processes **10,000 items through a filter→map→sum pipeline in 0.14 seconds**. A full RAG pipeline (chunk→embed→store→retrieve) runs in **0.5 milliseconds**. String pipeline (1000 iterations): **0.018 seconds**.

For an interpreted DSL, that's fast. Faster than most people need. And if you need more speed, MOL transpiles to Python — so you can optimize the hot path with native code.

---

## Closed-Source Distribution

This one's for other language creators: we built a distribution pipeline that compiles MOL into a standalone binary.

```bash
python build_dist.py pyinstaller
```

This produces an **8.7 MB single executable**. Users run `./mol run program.mol` and they get the full interpreter — but they can't see the source code. No Python installation required on their machine.

We also support Nuitka (compiles to C) and standard wheel distribution. The build script handles all three.

---

## The Numbers

| Metric | v0.2.0 | v0.3.0 |
|:---|:---:|:---:|
| Tests passing | 43 | 68 |
| Stdlib functions | 45+ | 90+ |
| Domain types | 12 | 12 |
| Distribution | GitHub only | PyPI + Binary + Playground |
| Online playground | ✗ | ✅ Live |
| `pip install` | ✗ | ✅ `mol-lang` |
| Standalone binary | ✗ | ✅ 8.7 MB |

---

## What's Next

- **v0.4.0** — Cloud playground on a custom domain, Docker image, more examples
- **v0.5.0** — Language Server Protocol (LSP) for real IDE autocomplete
- **v0.6.0** — WASM compilation for browser-native execution
- **v1.0.0** — Production release with LangChain/LlamaIndex integration

---

## Try It

```bash
pipx install mol-lang
mol repl
```

Or open the playground: **[http://135.235.138.217:8000](http://135.235.138.217:8000)**

Or browse the source: **[github.com/crux-ecosystem/mol-lang](https://github.com/crux-ecosystem/mol-lang)**

---

*MOL is built by [CruxLabx](https://github.com/crux-ecosystem) — the team behind IntraMind. If you're building AI pipelines and tired of invisible data flows, give MOL a try.*

*Found a bug? Want a feature? [Open an issue](https://github.com/crux-ecosystem/mol-lang/issues).*

---

**MOL: Where pipelines think.**
