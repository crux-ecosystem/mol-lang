# AlgoVerse: A Visual Algorithm Benchmarking & Analysis Engine

> **DAA Mini Project** — Implemented entirely in [MOL Language](https://github.com/crux-ecosystem/mol-lang)

## Overview

AlgoVerse implements **22 fundamental algorithms** from the Design & Analysis of Algorithms (DAA) curriculum. Each algorithm is benchmarked, its complexity empirically verified, and results displayed with formatted tables and visualizations — all written in MOL, a cognitive programming language.

## Modules

| # | Module | File | Algorithms |
|---|--------|------|------------|
| 1 | **Sorting Arena** | `01_sorting_arena.mol` | Bubble, Selection, Insertion, Merge, Quick, Heap Sort |
| 2 | **Graph Algorithms** | `02_graph_algorithms.mol` | BFS, DFS, Dijkstra, Kruskal MST, Topological Sort |
| 3 | **Dynamic Programming** | `03_dynamic_programming.mol` | 0/1 Knapsack, LCS, Matrix Chain, Edit Distance |
| 4 | **D&C vs Greedy** | `04_dc_vs_greedy.mol` | Closest Pair, Strassen's, Activity Selection, Huffman |
| 5 | **Complexity Analyzer** | `05_complexity_analyzer.mol` | Empirical O(n) verification, growth ratios, ASCII charts |

## How to Run

```bash
# Install MOL
pip install mol-lang

# Run individual modules
mol daa_project/01_sorting_arena.mol
mol daa_project/02_graph_algorithms.mol
mol daa_project/03_dynamic_programming.mol
mol daa_project/04_dc_vs_greedy.mol
mol daa_project/05_complexity_analyzer.mol

# Run the overview / demo
mol daa_project/00_algoverse_main.mol
```

## Algorithm Complexity Reference

| Algorithm | Best | Average | Worst | Space |
|-----------|------|---------|-------|-------|
| Bubble Sort | O(n) | O(n²) | O(n²) | O(1) |
| Selection Sort | O(n²) | O(n²) | O(n²) | O(1) |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) |
| BFS / DFS | O(V+E) | O(V+E) | O(V+E) | O(V) |
| Dijkstra | O(V²) | O(V²) | O(V²) | O(V) |
| Kruskal MST | O(E log E) | O(E log E) | O(E log E) | O(V) |
| 0/1 Knapsack | O(nW) | O(nW) | O(nW) | O(nW) |
| LCS | O(mn) | O(mn) | O(mn) | O(mn) |
| Matrix Chain | O(n³) | O(n³) | O(n³) | O(n²) |
| Edit Distance | O(mn) | O(mn) | O(mn) | O(mn) |
| Closest Pair | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Strassen | O(n^2.807) | O(n^2.807) | O(n^2.807) | O(n²) |
| Activity Selection | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Huffman Coding | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Linear Search | O(1) | O(n) | O(n) | O(1) |
| Binary Search | O(1) | O(log n) | O(log n) | O(1) |

## Key Features

- **22 algorithms** implemented from scratch — no imports, no libraries
- **Empirical complexity verification**: measures growth ratios to confirm Big-O
- **DP table visualization**: see the actual memoization tables being built
- **Huffman encoding demo**: character-level compression with bit output
- **Graph visualization**: adjacency list display, BFS/DFS traversal trees, shortest paths
- **Best/Worst/Average case benchmarks**: demonstrates how input affects performance
- **ASCII growth charts**: visual complexity comparison
- **Pipeline operators**: MOL's `|>` traces data flow through each step

## Author

**Mounesh Kodi** · CruxLabx · 2026
