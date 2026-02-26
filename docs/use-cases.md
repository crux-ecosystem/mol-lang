# Use Cases

MOL is built for **three domains** where pipeline visibility and readable code directly reduce debugging time and onboarding cost.

---

## 1. AI & ML Pipelines

**The original use case.** Every RAG pipeline is invisible glue code — MOL makes every stage visible.

```text
let index be doc |> chunk(512) |> embed("model-v1") |> store("kb")
let answer be retrieve(query, "kb", 5) |> think("answer this")
guard answer.confidence > 0.5 : "Low confidence"
```

**Auto-trace output:**
```text
  ┌─ Pipeline Trace ──────────────────────────────────────
  │ 0.  input                   ─  <Document "data.txt">
  │ 1.  chunk(512)          0.1ms  → List<5 Chunks>
  │ 2.  embed("model-v1")   0.2ms  → List<5 Embeddings>
  │ 3.  store("kb")         0.0ms  → <VectorStore "kb">
  └─ 3 steps · 0.4ms total ───────────────────────────
```

**Why MOL beats Python for this:**

| Task | Python | MOL |
|------|--------|-----|
| Build a RAG pipeline | 50+ lines of glue code | 3 lines |
| Debug pipeline failures | Add `print()` and `logging` | Auto-traced |
| Validate pipeline output | Manual assertions | `guard` built-in |
| Share pipeline logic | "Read my code" | Reads like English |

---

## 2. Data Processing & ETL

**Smart functions make data transforms effortless.** No boilerplate — just describe what you want.

```text
let sales be load_data("sales.json")

-- Top performers: filter → sort → extract
let top_reps be sales |>
  filter("closed") |>
  where(fn(s) -> s["amount"] > 15000) |>
  sort_by("amount") |>
  pluck("rep")

-- Revenue by region
let by_region be sales |> filter("closed") |> group_by("region")

-- Stats
let total be sales |> filter("closed") |> pluck("amount") |> sum_list
let avg be sales |> pluck("amount") |> mean
```

**Why MOL beats Python/SQL for this:**

| Task | Python (pandas) | SQL | MOL |
|------|-----------------|-----|-----|
| Filter by property | `df[df["active"]==True]` | `WHERE active = true` | `filter("active")` |
| Extract a column | `df["name"].tolist()` | `SELECT name` | `pluck("name")` |
| Chain transforms | Nested method calls | CTEs or subqueries | `\|>` pipes |
| See execution flow | Add logging | `EXPLAIN` | **Auto-traced** |
| Validate data | Try/except | Constraints | `guard` assertions |

---

## 3. Log Analysis & Monitoring

**Process structured logs, detect anomalies, generate reports — with full pipeline traceability.**

```text
let logs be load_data("app.log")

-- Find errors
let errors be logs |>
  where(fn(l) -> l["level"] == "ERROR") |>
  select(fn(l) -> l["service"] + ": " + l["message"])

-- Service health
let by_service be logs |> group_by("service")
for svc in keys(by_service) do
  let entries be by_service[svc]
  let error_rate be entries |> where(fn(l) -> l["level"] == "ERROR") |> len
  let avg_latency be entries |> pluck("latency") |> mean |> round(1)
  show svc + ": " + to_text(avg_latency) + "ms avg, " + to_text(error_rate) + " errors"
end

-- SLA check
let p95 be logs |> pluck("latency") |> percentile(95)
guard p95 < 1000 : "P95 latency exceeds SLA"
```

**Why MOL beats custom scripts for this:**

| Task | Bash/Python scripts | MOL |
|------|---------------------|-----|
| Parse + filter logs | `grep \| awk \| sort` | `where(fn(l) -> ...)` |
| Aggregate stats | Custom code | `mean`, `median`, `percentile` |
| Group by field | Manual dict building | `group_by("service")` |
| SLA validation | Exit codes | `guard` assertions |
| Audit trail | None | **Auto-traced pipelines** |

---

## 4. API & Microservice Logic

**Request validation, data transformation, and JSON response building — all traceable.**

```text
-- Validate request
guard request["action"] is not null : "Missing action"
guard request["limit"] <= 100 : "Limit too high"

-- Process: filter → sort → paginate
let result be users |>
  filter("active") |>
  where(fn(u) -> u["age"] >= min_age) |>
  sort_by("name") |>
  take(request["limit"])

-- Build response
let response be {
  "status": "ok",
  "count": len(result),
  "data": result |> select(fn(u) -> pick(u, "id", "name", "role"))
}
show json_stringify(response)
```

---

## Enterprise Benefits

### For Engineering Teams

- **Faster debugging** — Auto-tracing means no more "add print everywhere"
- **Readable code** — New team members understand pipelines immediately
- **Built-in validation** — `guard` assertions catch bad data at every stage
- **Sandboxed execution** — Run untrusted code safely in the playground

### For Technical Leaders

- **Reduce pipeline debugging time** by 60-80% (no manual logging)
- **Lower onboarding cost** — MOL reads like English, not like Perl
- **Audit-ready** — Every pipeline execution is traced and timed
- **No vendor lock-in** — Transpile to Python or JavaScript anytime

### For DevOps & SRE

- **Scripting replacement** — More readable than bash, safer than Python
- **Built-in statistics** — `mean`, `median`, `percentile`, `stdev` for monitoring
- **Data validation** — `guard` assertions as SLA checks
- **Reproducible** — Same code, same trace, every time

---

## Try It

```bash
pipx install mol-lang    # recommended
# or: pip install mol-lang  (in a venv)

mol run your_pipeline.mol
```

Or try the [online playground](https://mol.cruxlabx.in) — no installation required.
