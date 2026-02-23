# MOL Language — Research & Benchmarks

This directory contains the research paper, benchmark suite, and generated
figures for the MOL programming language.

## Structure

```
research/
├── paper.tex                     # LaTeX research paper (main document)
├── README.md                     # This file
├── benchmarks/
│   ├── bench_01_loc_comparison.py    # Lines of Code & Readability
│   ├── bench_02_stdlib_coverage.py   # Standard Library Feature Matrix
│   ├── bench_03_performance.py       # Execution Performance (MOL vs Python)
│   ├── bench_04_security.py          # Security Feature Comparison
│   ├── bench_05_innovation.py        # Innovation & Language Design Scoring
│   ├── run_all.py                    # Master runner for all benchmarks
│   └── generate_charts.py           # Chart generator (matplotlib)
├── data/                             # JSON benchmark results
│   ├── bench_01_loc.json
│   ├── bench_02_stdlib.json
│   ├── bench_03_performance.json
│   ├── bench_04_security.json
│   ├── bench_05_innovation.json
│   └── all_benchmarks.json
└── figures/                          # Generated charts (PNG + SVG)
    ├── fig_01_avg_loc.*
    ├── fig_02_loc_per_task.*
    ├── fig_03_stdlib_heatmap.*
    ├── fig_04_stdlib_totals.*
    ├── fig_05_security_radar.*
    ├── fig_06_security_scores.*
    ├── fig_07_innovation_scores.*
    ├── fig_08_performance_overhead.*
    ├── fig_09_imports.*
    └── fig_10_dashboard.*
```

## Quick Start

```bash
# Run all benchmarks and generate data
cd benchmarks && python run_all.py

# Generate publication charts
python generate_charts.py

# Compile paper (requires LaTeX)
cd .. && pdflatex paper.tex
```

## Key Findings

| Metric | MOL | Best Competitor | Advantage |
|--------|-----|-----------------|-----------|
| Avg LOC (6 tasks) | **7.2** | Python: 9.8 | 27% fewer lines |
| Zero-import functions | **143** | Elixir: 62 | 2.3x more |
| Stdlib categories (16) | **16/16** | Elixir: 8/16 | 2x coverage |
| Security features | **10/10** | Elixir: 7/10 | 43% more |
| Innovation score | **100/100** | F#: 28/100 | 3.6x higher |

## Compared Languages

- **Python** — General-purpose, dominant in AI/ML
- **JavaScript** — Web-native, growing AI presence
- **Elixir** — Functional, native pipe operator, actor model
- **Rust** — Systems language, borrow checker, memory safety
- **F#** — Functional, pipe operator, strong typing

## Paper Abstract

> We present MOL, a domain-specific language for AI-native computing with
> built-in observability, cryptographic primitives, and RAG pipelines.
> MOL achieves 27–54% fewer lines of code, provides 143 zero-import functions
> across 16 categories (6 unique to MOL), and offers 10/10 built-in security
> features — including homomorphic encryption and zero-knowledge proofs.
