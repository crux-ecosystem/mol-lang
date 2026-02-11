"""
MOL Language Server Protocol (LSP) Implementation
Provides: autocomplete, hover docs, diagnostics, signature help, go-to-definition
"""

import re
import logging
from typing import Optional

from lsprotocol import types as lsp
from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument

# ─── MOL Imports ─────────────────────────────────────────────────
from mol.parser import parse
from mol import __version__ as MOL_VERSION

logger = logging.getLogger("mol-lsp")

# ═══════════════════════════════════════════════════════════════════
#  STDLIB REGISTRY — all 99 functions with signatures & docs
# ═══════════════════════════════════════════════════════════════════

STDLIB_FUNCTIONS = {
    # ── General Utilities ──────────────────────────────
    "len": {
        "signature": "(obj)",
        "params": [{"name": "obj", "doc": "A list, text, or map"}],
        "doc": "Return the length of a list, text, or map.",
        "returns": "Number",
        "category": "utility",
    },
    "type_of": {
        "signature": "(obj)",
        "params": [{"name": "obj", "doc": "Any value"}],
        "doc": "Return the MOL type name as text.",
        "returns": "Text",
        "category": "utility",
    },
    "to_text": {
        "signature": "(obj)",
        "params": [{"name": "obj", "doc": "Any value to convert"}],
        "doc": "Convert any value to its text representation.",
        "returns": "Text",
        "category": "conversion",
    },
    "to_number": {
        "signature": "(obj)",
        "params": [{"name": "obj", "doc": "Text or number to convert"}],
        "doc": "Convert text to a number.",
        "returns": "Number",
        "category": "conversion",
    },
    "range": {
        "signature": "(start_or_end, end?, step?)",
        "params": [
            {"name": "start_or_end", "doc": "End value (if only arg) or start value"},
            {"name": "end", "doc": "End value (optional)"},
            {"name": "step", "doc": "Step size (optional, default 1)"},
        ],
        "doc": "Generate a list of numbers. `range(5)` → [0,1,2,3,4]. `range(1,5)` → [1,2,3,4].",
        "returns": "List",
        "category": "utility",
    },
    "abs": {
        "signature": "(x)",
        "params": [{"name": "x", "doc": "A number"}],
        "doc": "Return the absolute value of a number.",
        "returns": "Number",
        "category": "math",
    },
    "round": {
        "signature": "(x, n?)",
        "params": [
            {"name": "x", "doc": "Number to round"},
            {"name": "n", "doc": "Decimal places (default 0)"},
        ],
        "doc": "Round a number to n decimal places.",
        "returns": "Number",
        "category": "math",
    },
    "sqrt": {
        "signature": "(x)",
        "params": [{"name": "x", "doc": "A non-negative number"}],
        "doc": "Return the square root of x.",
        "returns": "Number",
        "category": "math",
    },
    "max": {
        "signature": "(list_or_args...)",
        "params": [{"name": "list_or_args", "doc": "A list or multiple arguments"}],
        "doc": "Return the maximum value from a list or arguments.",
        "returns": "Number",
        "category": "math",
    },
    "min": {
        "signature": "(list_or_args...)",
        "params": [{"name": "list_or_args", "doc": "A list or multiple arguments"}],
        "doc": "Return the minimum value from a list or arguments.",
        "returns": "Number",
        "category": "math",
    },
    "sum": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list of numbers"}],
        "doc": "Return the sum of all numbers in a list.",
        "returns": "Number",
        "category": "math",
    },
    "sort": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list to sort"}],
        "doc": "Sort a list in ascending order. Returns a new list.",
        "returns": "List",
        "category": "list",
    },
    "reverse": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list to reverse"}],
        "doc": "Reverse a list. Returns a new list.",
        "returns": "List",
        "category": "list",
    },
    "push": {
        "signature": "(lst, item)",
        "params": [
            {"name": "lst", "doc": "The list to append to"},
            {"name": "item", "doc": "The item to add"},
        ],
        "doc": "Append an item to the end of a list. Modifies the list in place.",
        "returns": "List",
        "category": "list",
    },
    "pop": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "The list to pop from"}],
        "doc": "Remove and return the last element of a list.",
        "returns": "Any",
        "category": "list",
    },
    "keys": {
        "signature": "(map)",
        "params": [{"name": "map", "doc": "A map/dictionary"}],
        "doc": "Return all keys of a map as a list.",
        "returns": "List",
        "category": "map",
    },
    "values": {
        "signature": "(map)",
        "params": [{"name": "map", "doc": "A map/dictionary"}],
        "doc": "Return all values of a map as a list.",
        "returns": "List",
        "category": "map",
    },
    "contains": {
        "signature": "(collection, item)",
        "params": [
            {"name": "collection", "doc": "A list, text, or map"},
            {"name": "item", "doc": "The item to search for"},
        ],
        "doc": "Check if a collection contains an item. Works with lists, text, and maps.",
        "returns": "Bool",
        "category": "utility",
    },
    "join": {
        "signature": "(lst, sep?)",
        "params": [
            {"name": "lst", "doc": "A list of values"},
            {"name": "sep", "doc": 'Separator text (default " ")'},
        ],
        "doc": 'Join a list into a single text string. `join(["a","b"], ", ")` → "a, b".',
        "returns": "Text",
        "category": "text",
    },
    "split": {
        "signature": "(text, sep?)",
        "params": [
            {"name": "text", "doc": "Text to split"},
            {"name": "sep", "doc": 'Split delimiter (default " ")'},
        ],
        "doc": 'Split text into a list. `split("a,b,c", ",")` → ["a","b","c"].',
        "returns": "List",
        "category": "text",
    },
    "upper": {
        "signature": "(text)",
        "params": [{"name": "text", "doc": "Text to uppercase"}],
        "doc": "Convert text to uppercase.",
        "returns": "Text",
        "category": "text",
    },
    "lower": {
        "signature": "(text)",
        "params": [{"name": "text", "doc": "Text to lowercase"}],
        "doc": "Convert text to lowercase.",
        "returns": "Text",
        "category": "text",
    },
    "trim": {
        "signature": "(text)",
        "params": [{"name": "text", "doc": "Text to trim"}],
        "doc": "Remove leading and trailing whitespace from text.",
        "returns": "Text",
        "category": "text",
    },
    "replace": {
        "signature": "(text, old, new)",
        "params": [
            {"name": "text", "doc": "The original text"},
            {"name": "old", "doc": "Substring to find"},
            {"name": "new", "doc": "Replacement text"},
        ],
        "doc": "Replace all occurrences of a substring in text.",
        "returns": "Text",
        "category": "text",
    },
    "slice": {
        "signature": "(obj, start, end?)",
        "params": [
            {"name": "obj", "doc": "A list or text"},
            {"name": "start", "doc": "Start index (0-based)"},
            {"name": "end", "doc": "End index (exclusive, optional)"},
        ],
        "doc": "Extract a portion of a list or text.",
        "returns": "List | Text",
        "category": "utility",
    },
    "clock": {
        "signature": "()",
        "params": [],
        "doc": "Return the current Unix timestamp in seconds.",
        "returns": "Number",
        "category": "utility",
    },
    "wait": {
        "signature": "(seconds)",
        "params": [{"name": "seconds", "doc": "Seconds to sleep"}],
        "doc": "Pause execution for the given number of seconds.",
        "returns": "null",
        "category": "utility",
    },
    "to_json": {
        "signature": "(obj)",
        "params": [{"name": "obj", "doc": "A value to serialize"}],
        "doc": "Serialize a MOL value to JSON text.",
        "returns": "Text",
        "category": "conversion",
    },
    "from_json": {
        "signature": "(text)",
        "params": [{"name": "text", "doc": "JSON text to parse"}],
        "doc": "Parse JSON text into a MOL value (map, list, etc.).",
        "returns": "Any",
        "category": "conversion",
    },
    "inspect": {
        "signature": "(obj)",
        "params": [{"name": "obj", "doc": "Any MOL value"}],
        "doc": "Return a detailed text inspection of any MOL object, including type and internal state.",
        "returns": "Text",
        "category": "utility",
    },
    "display": {
        "signature": "(value)",
        "params": [{"name": "value", "doc": "Value to display"}],
        "doc": "Print a value and pass it through (pipe-friendly). Useful in pipelines for debugging.",
        "returns": "Any (passthrough)",
        "category": "utility",
    },
    "tap": {
        "signature": "(value, label?)",
        "params": [
            {"name": "value", "doc": "Value to inspect"},
            {"name": "label", "doc": 'Debug label (default "tap")'},
        ],
        "doc": "Debug print with a label, then pass the value through. For pipeline debugging.",
        "returns": "Any (passthrough)",
        "category": "utility",
    },
    "assert_min": {
        "signature": "(value, threshold)",
        "params": [
            {"name": "value", "doc": "Numeric value to check"},
            {"name": "threshold", "doc": "Minimum allowed value"},
        ],
        "doc": "Assert that a value is >= threshold. Raises error otherwise.",
        "returns": "Any (passthrough)",
        "category": "guard",
    },
    "assert_not_null": {
        "signature": "(value)",
        "params": [{"name": "value", "doc": "Value to check"}],
        "doc": "Assert that a value is not null. Raises error otherwise.",
        "returns": "Any (passthrough)",
        "category": "guard",
    },
    "print": {
        "signature": "(args...)",
        "params": [{"name": "args", "doc": "One or more values to print"}],
        "doc": "Print one or more values to stdout, separated by spaces.",
        "returns": "null",
        "category": "utility",
    },

    # ── IntraMind Constructors ─────────────────────────
    "Thought": {
        "signature": "(content?, confidence?)",
        "params": [
            {"name": "content", "doc": 'Thought text (default "")'},
            {"name": "confidence", "doc": "Confidence 0.0–1.0 (default 1.0)"},
        ],
        "doc": "Create a Thought — a cognitive unit with content and confidence score.",
        "returns": "Thought",
        "category": "intramind",
    },
    "Memory": {
        "signature": "(key?, value?)",
        "params": [
            {"name": "key", "doc": 'Memory key (default "")'},
            {"name": "value", "doc": "Stored value (default null)"},
        ],
        "doc": "Create a Memory — a key-value cognitive store with recall tracking.",
        "returns": "Memory",
        "category": "intramind",
    },
    "Node": {
        "signature": "(label?, weight?)",
        "params": [
            {"name": "label", "doc": 'Node label (default "")'},
            {"name": "weight", "doc": "Node weight 0.0–1.0 (default 0.0)"},
        ],
        "doc": "Create a Node — a neural network building block with connections, activation, and evolution.",
        "returns": "Node",
        "category": "intramind",
    },
    "Stream": {
        "signature": "(name?)",
        "params": [
            {"name": "name", "doc": 'Stream name (default "")'},
        ],
        "doc": "Create a Stream — an event channel for emit/subscribe/sync patterns.",
        "returns": "Stream",
        "category": "intramind",
    },
    "Document": {
        "signature": "(source?, content?)",
        "params": [
            {"name": "source", "doc": 'Source identifier (default "")'},
            {"name": "content", "doc": 'Document text (default "")'},
        ],
        "doc": "Create a Document — a text container for RAG pipelines.",
        "returns": "Document",
        "category": "rag",
    },
    "Embedding": {
        "signature": "(text?, model?)",
        "params": [
            {"name": "text", "doc": 'Text to embed (default "")'},
            {"name": "model", "doc": 'Embedding model (default "mol-sim-v1")'},
        ],
        "doc": "Create an Embedding — a vector representation of text.",
        "returns": "Embedding",
        "category": "rag",
    },
    "Chunk": {
        "signature": "(content?, index?, source?)",
        "params": [
            {"name": "content", "doc": 'Chunk text (default "")'},
            {"name": "index", "doc": "Chunk index (default 0)"},
            {"name": "source", "doc": 'Source identifier (default "")'},
        ],
        "doc": "Create a Chunk — a text fragment from splitting a Document.",
        "returns": "Chunk",
        "category": "rag",
    },

    # ── Pipeline / RAG ─────────────────────────────────
    "load_text": {
        "signature": "(path)",
        "params": [{"name": "path", "doc": "File path to load"}],
        "doc": "Load text from a file and return a Document.",
        "returns": "Document",
        "category": "rag",
    },
    "chunk": {
        "signature": "(data, size?)",
        "params": [
            {"name": "data", "doc": "Text, Document, or string to split"},
            {"name": "size", "doc": "Chunk size in characters (default 512)"},
        ],
        "doc": "Split text or a Document into Chunks of the given size.",
        "returns": "List<Chunk>",
        "category": "rag",
    },
    "embed": {
        "signature": "(data, model?)",
        "params": [
            {"name": "data", "doc": "Text, Chunk, or list to embed"},
            {"name": "model", "doc": 'Embedding model (default "mol-sim-v1")'},
        ],
        "doc": "Create embedding vectors from text, Chunks, or a list of Chunks.",
        "returns": "Embedding | List<Embedding>",
        "category": "rag",
    },
    "store": {
        "signature": "(data, name?)",
        "params": [
            {"name": "data", "doc": "Embeddings to store"},
            {"name": "name", "doc": 'VectorStore name (default "default")'},
        ],
        "doc": "Store embeddings in a named VectorStore for later retrieval.",
        "returns": "VectorStore",
        "category": "rag",
    },
    "retrieve": {
        "signature": "(query, store_name?, top_k?)",
        "params": [
            {"name": "query", "doc": "Query text to search for"},
            {"name": "store_name", "doc": 'VectorStore name (default "default")'},
            {"name": "top_k", "doc": "Number of results (default 3)"},
        ],
        "doc": "Retrieve the top-k most similar entries from a VectorStore.",
        "returns": "List",
        "category": "rag",
    },
    "cosine_sim": {
        "signature": "(a, b)",
        "params": [
            {"name": "a", "doc": "First Embedding"},
            {"name": "b", "doc": "Second Embedding"},
        ],
        "doc": "Compute cosine similarity between two Embeddings (0.0–1.0).",
        "returns": "Number",
        "category": "rag",
    },
    "think": {
        "signature": "(data, prompt?)",
        "params": [
            {"name": "data", "doc": "Input data to think about"},
            {"name": "prompt", "doc": 'Thinking prompt (default "")'},
        ],
        "doc": "Synthesize a Thought from data with an optional reasoning prompt.",
        "returns": "Thought",
        "category": "rag",
    },
    "recall": {
        "signature": "(key_or_mem)",
        "params": [{"name": "key_or_mem", "doc": "Memory object or key text"}],
        "doc": "Recall a Memory's value by key or Memory object.",
        "returns": "Any",
        "category": "intramind",
    },
    "classify": {
        "signature": "(text, categories...)",
        "params": [
            {"name": "text", "doc": "Text to classify"},
            {"name": "categories", "doc": "Category names"},
        ],
        "doc": "Classify text into one of the given categories.",
        "returns": "Text",
        "category": "rag",
    },
    "summarize": {
        "signature": "(text, max_len?)",
        "params": [
            {"name": "text", "doc": "Text to summarize"},
            {"name": "max_len", "doc": "Maximum length (default 100)"},
        ],
        "doc": "Summarize text by truncating to the nearest sentence boundary.",
        "returns": "Text",
        "category": "rag",
    },

    # ── Functional Programming ─────────────────────────
    "map": {
        "signature": "(lst, func)",
        "params": [
            {"name": "lst", "doc": "List to transform"},
            {"name": "func", "doc": "Function to apply to each element"},
        ],
        "doc": "Apply a function to every element of a list. Returns a new list.",
        "returns": "List",
        "category": "functional",
    },
    "filter": {
        "signature": "(lst, func)",
        "params": [
            {"name": "lst", "doc": "List to filter"},
            {"name": "func", "doc": "Predicate function (returns Bool)"},
        ],
        "doc": "Keep only elements where the function returns true.",
        "returns": "List",
        "category": "functional",
    },
    "reduce": {
        "signature": "(lst, func, initial?)",
        "params": [
            {"name": "lst", "doc": "List to reduce"},
            {"name": "func", "doc": "Function(accumulator, element)"},
            {"name": "initial", "doc": "Initial accumulator (optional)"},
        ],
        "doc": "Reduce a list to a single value by applying a function cumulatively.",
        "returns": "Any",
        "category": "functional",
    },
    "flatten": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A nested list"}],
        "doc": "Flatten a nested list into a single-level list.",
        "returns": "List",
        "category": "functional",
    },
    "unique": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list"}],
        "doc": "Remove duplicate elements, preserving order.",
        "returns": "List",
        "category": "functional",
    },
    "zip": {
        "signature": "(a, b)",
        "params": [
            {"name": "a", "doc": "First list"},
            {"name": "b", "doc": "Second list"},
        ],
        "doc": "Pair elements from two lists: `zip([1,2],[\"a\",\"b\"])` → [[1,\"a\"],[2,\"b\"]].",
        "returns": "List",
        "category": "functional",
    },
    "enumerate": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list"}],
        "doc": "Add indices: `enumerate([\"a\",\"b\"])` → [[0,\"a\"],[1,\"b\"]].",
        "returns": "List",
        "category": "functional",
    },
    "count": {
        "signature": "(lst, item)",
        "params": [
            {"name": "lst", "doc": "A list to search"},
            {"name": "item", "doc": "Item to count"},
        ],
        "doc": "Count occurrences of an item in a list.",
        "returns": "Number",
        "category": "functional",
    },
    "find": {
        "signature": "(lst, func)",
        "params": [
            {"name": "lst", "doc": "A list to search"},
            {"name": "func", "doc": "Predicate function"},
        ],
        "doc": "Return the first element matching the predicate, or null.",
        "returns": "Any | null",
        "category": "functional",
    },
    "find_index": {
        "signature": "(lst, item)",
        "params": [
            {"name": "lst", "doc": "A list to search"},
            {"name": "item", "doc": "Item to find"},
        ],
        "doc": "Return the index of the first occurrence, or -1.",
        "returns": "Number",
        "category": "functional",
    },
    "take": {
        "signature": "(lst, n)",
        "params": [
            {"name": "lst", "doc": "A list"},
            {"name": "n", "doc": "Number of elements"},
        ],
        "doc": "Return the first n elements of a list.",
        "returns": "List",
        "category": "functional",
    },
    "drop": {
        "signature": "(lst, n)",
        "params": [
            {"name": "lst", "doc": "A list"},
            {"name": "n", "doc": "Number of elements to skip"},
        ],
        "doc": "Return a list with the first n elements removed.",
        "returns": "List",
        "category": "functional",
    },
    "group_by": {
        "signature": "(lst, func)",
        "params": [
            {"name": "lst", "doc": "A list to group"},
            {"name": "func", "doc": "Grouping function (returns the group key)"},
        ],
        "doc": "Group list elements by the result of a function. Returns a map.",
        "returns": "Map",
        "category": "functional",
    },
    "chunk_list": {
        "signature": "(lst, size)",
        "params": [
            {"name": "lst", "doc": "A list to split"},
            {"name": "size", "doc": "Size of each chunk"},
        ],
        "doc": "Split a list into chunks of the given size.",
        "returns": "List<List>",
        "category": "functional",
    },
    "every": {
        "signature": "(lst, func)",
        "params": [
            {"name": "lst", "doc": "A list"},
            {"name": "func", "doc": "Predicate function"},
        ],
        "doc": "Return true if ALL elements match the predicate.",
        "returns": "Bool",
        "category": "functional",
    },
    "some": {
        "signature": "(lst, func)",
        "params": [
            {"name": "lst", "doc": "A list"},
            {"name": "func", "doc": "Predicate function"},
        ],
        "doc": "Return true if ANY element matches the predicate.",
        "returns": "Bool",
        "category": "functional",
    },

    # ── Math & Statistics ──────────────────────────────
    "floor": {
        "signature": "(x)",
        "params": [{"name": "x", "doc": "A number"}],
        "doc": "Return the largest integer ≤ x.",
        "returns": "Number",
        "category": "math",
    },
    "ceil": {
        "signature": "(x)",
        "params": [{"name": "x", "doc": "A number"}],
        "doc": "Return the smallest integer ≥ x.",
        "returns": "Number",
        "category": "math",
    },
    "log": {
        "signature": "(x, base?)",
        "params": [
            {"name": "x", "doc": "A positive number"},
            {"name": "base", "doc": "Logarithm base (default: natural log)"},
        ],
        "doc": "Compute the logarithm of x. Natural log by default, or specify a base.",
        "returns": "Number",
        "category": "math",
    },
    "sin": {
        "signature": "(x)",
        "params": [{"name": "x", "doc": "Angle in radians"}],
        "doc": "Compute the sine of x.",
        "returns": "Number",
        "category": "math",
    },
    "cos": {
        "signature": "(x)",
        "params": [{"name": "x", "doc": "Angle in radians"}],
        "doc": "Compute the cosine of x.",
        "returns": "Number",
        "category": "math",
    },
    "tan": {
        "signature": "(x)",
        "params": [{"name": "x", "doc": "Angle in radians"}],
        "doc": "Compute the tangent of x.",
        "returns": "Number",
        "category": "math",
    },
    "pi": {
        "signature": "()",
        "params": [],
        "doc": "Return the mathematical constant π (3.14159...).",
        "returns": "Number",
        "category": "math",
    },
    "e": {
        "signature": "()",
        "params": [],
        "doc": "Return Euler's number e (2.71828...).",
        "returns": "Number",
        "category": "math",
    },
    "pow": {
        "signature": "(base, exp)",
        "params": [
            {"name": "base", "doc": "Base number"},
            {"name": "exp", "doc": "Exponent"},
        ],
        "doc": "Compute base raised to the power of exp.",
        "returns": "Number",
        "category": "math",
    },
    "clamp": {
        "signature": "(value, lo, hi)",
        "params": [
            {"name": "value", "doc": "Number to clamp"},
            {"name": "lo", "doc": "Minimum bound"},
            {"name": "hi", "doc": "Maximum bound"},
        ],
        "doc": "Clamp a value to the range [lo, hi].",
        "returns": "Number",
        "category": "math",
    },
    "lerp": {
        "signature": "(a, b, t)",
        "params": [
            {"name": "a", "doc": "Start value"},
            {"name": "b", "doc": "End value"},
            {"name": "t", "doc": "Interpolation factor (0.0–1.0)"},
        ],
        "doc": "Linear interpolation between a and b. `lerp(0, 100, 0.5)` → 50.",
        "returns": "Number",
        "category": "math",
    },
    "mean": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list of numbers"}],
        "doc": "Compute the arithmetic mean (average) of a list.",
        "returns": "Number",
        "category": "statistics",
    },
    "median": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list of numbers"}],
        "doc": "Compute the median of a list.",
        "returns": "Number",
        "category": "statistics",
    },
    "stdev": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list of numbers"}],
        "doc": "Compute the standard deviation of a list.",
        "returns": "Number",
        "category": "statistics",
    },
    "variance": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list of numbers"}],
        "doc": "Compute the variance of a list.",
        "returns": "Number",
        "category": "statistics",
    },
    "percentile": {
        "signature": "(lst, p)",
        "params": [
            {"name": "lst", "doc": "A list of numbers"},
            {"name": "p", "doc": "Percentile (0–100)"},
        ],
        "doc": "Compute the p-th percentile of a list.",
        "returns": "Number",
        "category": "statistics",
    },

    # ── String Algorithms ──────────────────────────────
    "starts_with": {
        "signature": "(text, prefix)",
        "params": [
            {"name": "text", "doc": "Text to check"},
            {"name": "prefix", "doc": "Prefix to match"},
        ],
        "doc": "Check if text starts with the given prefix.",
        "returns": "Bool",
        "category": "text",
    },
    "ends_with": {
        "signature": "(text, suffix)",
        "params": [
            {"name": "text", "doc": "Text to check"},
            {"name": "suffix", "doc": "Suffix to match"},
        ],
        "doc": "Check if text ends with the given suffix.",
        "returns": "Bool",
        "category": "text",
    },
    "pad_left": {
        "signature": "(text, width, char?)",
        "params": [
            {"name": "text", "doc": "Text to pad"},
            {"name": "width", "doc": "Target width"},
            {"name": "char", "doc": 'Padding character (default " ")'},
        ],
        "doc": "Pad text on the left to the given width.",
        "returns": "Text",
        "category": "text",
    },
    "pad_right": {
        "signature": "(text, width, char?)",
        "params": [
            {"name": "text", "doc": "Text to pad"},
            {"name": "width", "doc": "Target width"},
            {"name": "char", "doc": 'Padding character (default " ")'},
        ],
        "doc": "Pad text on the right to the given width.",
        "returns": "Text",
        "category": "text",
    },
    "repeat": {
        "signature": "(text, n)",
        "params": [
            {"name": "text", "doc": "Text to repeat"},
            {"name": "n", "doc": "Number of repetitions"},
        ],
        "doc": 'Repeat text n times. `repeat("ab", 3)` → "ababab".',
        "returns": "Text",
        "category": "text",
    },
    "char_at": {
        "signature": "(text, index)",
        "params": [
            {"name": "text", "doc": "Text to index"},
            {"name": "index", "doc": "0-based character index"},
        ],
        "doc": "Get the character at the given index.",
        "returns": "Text",
        "category": "text",
    },
    "index_of": {
        "signature": "(text, sub)",
        "params": [
            {"name": "text", "doc": "Text to search in"},
            {"name": "sub", "doc": "Substring to find"},
        ],
        "doc": "Find the index of a substring. Returns -1 if not found.",
        "returns": "Number",
        "category": "text",
    },
    "format": {
        "signature": "(template, args...)",
        "params": [
            {"name": "template", "doc": "Text with {} placeholders"},
            {"name": "args", "doc": "Values to fill in"},
        ],
        "doc": 'Format text with placeholders. `format("Hello, {}!", "MOL")` → "Hello, MOL!".',
        "returns": "Text",
        "category": "text",
    },

    # ── Hashing & Encoding ─────────────────────────────
    "hash": {
        "signature": "(text, algo?)",
        "params": [
            {"name": "text", "doc": "Text to hash"},
            {"name": "algo", "doc": 'Algorithm: "sha256" (default), "md5", "sha1", "sha512"'},
        ],
        "doc": "Hash text with the specified algorithm. Default is SHA-256.",
        "returns": "Text",
        "category": "crypto",
    },
    "uuid": {
        "signature": "()",
        "params": [],
        "doc": "Generate a random UUID v4 string.",
        "returns": "Text",
        "category": "crypto",
    },
    "base64_encode": {
        "signature": "(text)",
        "params": [{"name": "text", "doc": "Text to encode"}],
        "doc": "Encode text to Base64.",
        "returns": "Text",
        "category": "crypto",
    },
    "base64_decode": {
        "signature": "(text)",
        "params": [{"name": "text", "doc": "Base64 text to decode"}],
        "doc": "Decode Base64 text back to plain text.",
        "returns": "Text",
        "category": "crypto",
    },

    # ── Sorting ────────────────────────────────────────
    "sort_by": {
        "signature": "(lst, func)",
        "params": [
            {"name": "lst", "doc": "A list to sort"},
            {"name": "func", "doc": "Key function for sorting"},
        ],
        "doc": "Sort a list using a custom key function.",
        "returns": "List",
        "category": "list",
    },
    "sort_desc": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list to sort"}],
        "doc": "Sort a list in descending order.",
        "returns": "List",
        "category": "list",
    },
    "binary_search": {
        "signature": "(lst, target)",
        "params": [
            {"name": "lst", "doc": "A sorted list"},
            {"name": "target", "doc": "Value to search for"},
        ],
        "doc": "Binary search on a sorted list. Returns index or -1.",
        "returns": "Number",
        "category": "list",
    },

    # ── Random ─────────────────────────────────────────
    "random": {
        "signature": "()",
        "params": [],
        "doc": "Return a random float between 0.0 and 1.0.",
        "returns": "Number",
        "category": "random",
    },
    "random_int": {
        "signature": "(lo, hi)",
        "params": [
            {"name": "lo", "doc": "Lower bound (inclusive)"},
            {"name": "hi", "doc": "Upper bound (inclusive)"},
        ],
        "doc": "Return a random integer between lo and hi (inclusive).",
        "returns": "Number",
        "category": "random",
    },
    "shuffle": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list to shuffle"}],
        "doc": "Return a new list with elements in random order.",
        "returns": "List",
        "category": "random",
    },
    "sample": {
        "signature": "(lst, n)",
        "params": [
            {"name": "lst", "doc": "A list to sample from"},
            {"name": "n", "doc": "Number of items to pick"},
        ],
        "doc": "Return n random items from a list (without replacement).",
        "returns": "List",
        "category": "random",
    },
    "choice": {
        "signature": "(lst)",
        "params": [{"name": "lst", "doc": "A list to choose from"}],
        "doc": "Return one random element from a list.",
        "returns": "Any",
        "category": "random",
    },

    # ── Maps ───────────────────────────────────────────
    "merge": {
        "signature": "(maps...)",
        "params": [{"name": "maps", "doc": "Two or more maps to merge"}],
        "doc": "Merge multiple maps. Later values overwrite earlier ones.",
        "returns": "Map",
        "category": "map",
    },
    "pick": {
        "signature": "(map, fields...)",
        "params": [
            {"name": "map", "doc": "A map"},
            {"name": "fields", "doc": "Field names to keep"},
        ],
        "doc": "Return a new map with only the specified fields.",
        "returns": "Map",
        "category": "map",
    },
    "omit": {
        "signature": "(map, fields...)",
        "params": [
            {"name": "map", "doc": "A map"},
            {"name": "fields", "doc": "Field names to exclude"},
        ],
        "doc": "Return a new map without the specified fields.",
        "returns": "Map",
        "category": "map",
    },

    # ── Type Checks ────────────────────────────────────
    "is_null": {
        "signature": "(val)",
        "params": [{"name": "val", "doc": "Value to check"}],
        "doc": "Return true if the value is null.",
        "returns": "Bool",
        "category": "type",
    },
    "is_number": {
        "signature": "(val)",
        "params": [{"name": "val", "doc": "Value to check"}],
        "doc": "Return true if the value is a Number.",
        "returns": "Bool",
        "category": "type",
    },
    "is_text": {
        "signature": "(val)",
        "params": [{"name": "val", "doc": "Value to check"}],
        "doc": "Return true if the value is a Text (string).",
        "returns": "Bool",
        "category": "type",
    },
    "is_list": {
        "signature": "(val)",
        "params": [{"name": "val", "doc": "Value to check"}],
        "doc": "Return true if the value is a List.",
        "returns": "Bool",
        "category": "type",
    },
    "is_map": {
        "signature": "(val)",
        "params": [{"name": "val", "doc": "Value to check"}],
        "doc": "Return true if the value is a Map.",
        "returns": "Bool",
        "category": "type",
    },
}

# ── Keywords ──────────────────────────────────────────────────────
MOL_KEYWORDS = [
    "let", "be", "set", "to", "show", "if", "then", "elif", "else", "end",
    "while", "for", "in", "do", "define", "return", "begin",
    "and", "or", "not", "is", "true", "false", "null",
    "trigger", "link", "process", "access", "sync", "evolve",
    "emit", "listen", "with", "pipeline", "guard",
]

KEYWORD_DOCS = {
    "let": "Declare a variable.\n\n```mol\nlet x be 42\nlet name be \"MOL\"\n```",
    "be": "Assign a value in a `let` declaration.\n\n```mol\nlet x be 42\n```",
    "set": "Reassign a variable.\n\n```mol\nset x to 100\n```",
    "to": "Target value in a `set` assignment or `link` statement.",
    "show": "Print a value to stdout.\n\n```mol\nshow \"Hello, World!\"\nshow 42\n```",
    "if": "Conditional branch.\n\n```mol\nif x > 0\n  show \"positive\"\nelif x is 0\n  show \"zero\"\nelse\n  show \"negative\"\nend\n```",
    "elif": "Additional condition in an `if` block.",
    "else": "Default branch in an `if` block.",
    "end": "Close a block (`if`, `for`, `while`, `define`, `pipeline`, `begin`).",
    "while": "Loop while condition is true.\n\n```mol\nwhile x > 0\n  set x to x - 1\nend\n```",
    "for": "Iterate over a list.\n\n```mol\nfor item in [1, 2, 3] do\n  show item\nend\n```",
    "in": "Iterator source in a `for` loop.",
    "do": "Begin the body of a `for` loop.",
    "define": "Define a function.\n\n```mol\ndefine greet(name)\n  return \"Hello, \" + name\nend\n```",
    "return": "Return a value from a function.\n\n```mol\ndefine add(a, b)\n  return a + b\nend\n```",
    "begin": "Begin a block scope.\n\n```mol\nbegin\n  let temp be 42\n  show temp\nend\n```",
    "guard": "Assert a condition, fail with message if false.\n\n```mol\nguard len(data) > 0 : \"Data is empty\"\nguard confidence > 0.5 : \"Low confidence\"\n```",
    "pipeline": "Define a reusable pipeline.\n\n```mol\npipeline process(data)\n  show data\nend\n```",
    "trigger": "Trigger an event.\n\n```mol\ntrigger \"data_ready\"\n```",
    "link": "Link two nodes.\n\n```mol\nlink nodeA to nodeB\n```",
    "evolve": "Evolve a neural node.\n\n```mol\nevolve node\n```",
    "emit": "Emit data to a stream.\n\n```mol\nemit data\n```",
    "listen": "Listen for events.\n\n```mol\nlisten \"event\" do\n  show \"received\"\nend\n```",
    "access": "Access a resource with credentials.\n\n```mol\naccess \"mind_core\" with \"admin\"\n```",
    "sync": "Synchronize a stream.\n\n```mol\nsync stream\n```",
    "process": "Process a node or data.\n\n```mol\nprocess data with transform\n```",
    "and": "Logical AND operator.",
    "or": "Logical OR operator.",
    "not": "Logical NOT operator.",
    "is": "Equality comparison.\n\n```mol\nif x is 42\n  show \"match\"\nend\n```",
    "true": "Boolean true literal.",
    "false": "Boolean false literal.",
    "null": "Null literal (absence of value).",
}

# ── Snippet templates ─────────────────────────────────────────────
SNIPPETS = [
    {
        "label": "let",
        "detail": "Declare a variable",
        "insertText": 'let ${1:name} be ${2:value}',
        "kind": lsp.CompletionItemKind.Snippet,
    },
    {
        "label": "if-else",
        "detail": "If/else block",
        "insertText": 'if ${1:condition}\n  ${2:body}\nelse\n  ${3:else_body}\nend',
        "kind": lsp.CompletionItemKind.Snippet,
    },
    {
        "label": "for-loop",
        "detail": "For loop",
        "insertText": 'for ${1:item} in ${2:list} do\n  ${3:body}\nend',
        "kind": lsp.CompletionItemKind.Snippet,
    },
    {
        "label": "while-loop",
        "detail": "While loop",
        "insertText": 'while ${1:condition}\n  ${2:body}\nend',
        "kind": lsp.CompletionItemKind.Snippet,
    },
    {
        "label": "define",
        "detail": "Define a function",
        "insertText": 'define ${1:name}(${2:params})\n  ${3:body}\nend',
        "kind": lsp.CompletionItemKind.Snippet,
    },
    {
        "label": "pipeline",
        "detail": "Define a pipeline",
        "insertText": 'pipeline ${1:name}(${2:params})\n  ${3:body}\nend',
        "kind": lsp.CompletionItemKind.Snippet,
    },
    {
        "label": "guard",
        "detail": "Guard assertion",
        "insertText": 'guard ${1:condition} : "${2:message}"',
        "kind": lsp.CompletionItemKind.Snippet,
    },
    {
        "label": "pipe",
        "detail": "Pipe chain",
        "insertText": '${1:value} |> ${2:func1} |> ${3:func2}',
        "kind": lsp.CompletionItemKind.Snippet,
    },
    {
        "label": "rag-pipeline",
        "detail": "RAG pipeline template",
        "insertText": 'let index be Document("${1:source}", ${2:content}) |> chunk(${3:512}) |> embed("${4:mol-sim-v1}") |> store("${5:kb}")\nlet answer be retrieve("${6:query}", "${5:kb}", ${7:3}) |> think("${8:prompt}")\nguard answer.confidence > ${9:0.5} : "Low confidence"',
        "kind": lsp.CompletionItemKind.Snippet,
    },
]


# ═══════════════════════════════════════════════════════════════════
#  MOL LANGUAGE SERVER
# ═══════════════════════════════════════════════════════════════════

server = LanguageServer("mol-language-server", f"v{MOL_VERSION}",
                        text_document_sync_kind=lsp.TextDocumentSyncKind.Full)


def _get_word_at_position(doc: TextDocument, position: lsp.Position) -> str:
    """Extract the word under the cursor."""
    try:
        lines = doc.source.splitlines()
        if position.line >= len(lines):
            return ""
        line = lines[position.line]
        col = min(position.character, len(line))

        # Walk backwards to find word start
        start = col
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1

        # Walk forward to find word end
        end = col
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1

        return line[start:end]
    except Exception:
        return ""


def _get_prefix(doc: TextDocument, position: lsp.Position) -> str:
    """Get the text before the cursor on the current line (for filtering completions)."""
    try:
        lines = doc.source.splitlines()
        if position.line >= len(lines):
            return ""
        line = lines[position.line]
        col = min(position.character, len(line))

        start = col
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1

        return line[start:col]
    except Exception:
        return ""


def _extract_user_definitions(source: str) -> dict:
    """Extract user-defined variables and functions from source text for local completions."""
    definitions = {}

    # Find `let X be ...`
    for m in re.finditer(r'\blet\s+(\w+)\s+be\b', source):
        name = m.group(1)
        definitions[name] = {
            "kind": lsp.CompletionItemKind.Variable,
            "detail": "variable",
            "doc": f"User variable `{name}`",
            "line": source[:m.start()].count('\n'),
        }

    # Find `define NAME(params)`
    for m in re.finditer(r'\bdefine\s+(\w+)\s*\(([^)]*)\)', source):
        name = m.group(1)
        params = m.group(2).strip()
        definitions[name] = {
            "kind": lsp.CompletionItemKind.Function,
            "detail": f"({params})" if params else "()",
            "doc": f"User function `{name}({params})`",
            "line": source[:m.start()].count('\n'),
        }

    # Find `pipeline NAME(params)`
    for m in re.finditer(r'\bpipeline\s+(\w+)\s*\(([^)]*)\)', source):
        name = m.group(1)
        params = m.group(2).strip()
        definitions[name] = {
            "kind": lsp.CompletionItemKind.Function,
            "detail": f"pipeline({params})" if params else "pipeline()",
            "doc": f"User pipeline `{name}({params})`",
            "line": source[:m.start()].count('\n'),
        }

    # Find `set X to ...` (marks X as mutable)
    for m in re.finditer(r'\bset\s+(\w+)\s+to\b', source):
        name = m.group(1)
        if name not in definitions:
            definitions[name] = {
                "kind": lsp.CompletionItemKind.Variable,
                "detail": "variable",
                "doc": f"User variable `{name}`",
                "line": source[:m.start()].count('\n'),
            }

    # Find `for X in ...`
    for m in re.finditer(r'\bfor\s+(\w+)\s+in\b', source):
        name = m.group(1)
        if name not in definitions:
            definitions[name] = {
                "kind": lsp.CompletionItemKind.Variable,
                "detail": "loop variable",
                "doc": f"Loop variable `{name}`",
                "line": source[:m.start()].count('\n'),
            }

    return definitions


def _validate_document(doc: TextDocument) -> list[lsp.Diagnostic]:
    """Parse the document and return diagnostics."""
    source = doc.source
    diagnostics = []

    if not source.strip():
        return diagnostics

    try:
        parse(source)
    except Exception as exc:
        msg = str(exc)
        line = 0
        col = 0

        # Extract line/col from error message
        line_match = re.search(r'line\s+(\d+)', msg, re.IGNORECASE)
        col_match = re.search(r'col(?:umn)?\s+(\d+)', msg, re.IGNORECASE)

        if line_match:
            line = max(0, int(line_match.group(1)) - 1)
        if col_match:
            col = max(0, int(col_match.group(1)) - 1)

        # Clean up the error message
        clean_msg = msg
        if "Unexpected token" in msg:
            clean_msg = msg.split("\n")[0]
        elif "could not convert" in msg:
            clean_msg = msg.strip()

        diagnostics.append(
            lsp.Diagnostic(
                range=lsp.Range(
                    start=lsp.Position(line=line, character=col),
                    end=lsp.Position(line=line, character=col + 10),
                ),
                message=clean_msg,
                severity=lsp.DiagnosticSeverity.Error,
                source="mol",
            )
        )

    return diagnostics


# ── Diagnostics (on open/change/save) ────────────────────────────

@server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def did_open(params: lsp.DidOpenTextDocumentParams):
    doc = server.workspace.get_text_document(params.text_document.uri)
    diagnostics = _validate_document(doc)
    server.publish_diagnostics(doc.uri, diagnostics)


@server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
def did_change(params: lsp.DidChangeTextDocumentParams):
    doc = server.workspace.get_text_document(params.text_document.uri)
    diagnostics = _validate_document(doc)
    server.publish_diagnostics(doc.uri, diagnostics)


@server.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
def did_save(params: lsp.DidSaveTextDocumentParams):
    doc = server.workspace.get_text_document(params.text_document.uri)
    diagnostics = _validate_document(doc)
    server.publish_diagnostics(doc.uri, diagnostics)


# ── Completions ───────────────────────────────────────────────────

@server.feature(
    lsp.TEXT_DOCUMENT_COMPLETION,
    lsp.CompletionOptions(trigger_characters=[".", "|", "(", '"'], resolve_provider=False),
)
def completions(params: lsp.CompletionParams) -> lsp.CompletionList:
    doc = server.workspace.get_text_document(params.text_document.uri)
    prefix = _get_prefix(doc, params.position)
    items: list[lsp.CompletionItem] = []

    # 1. Stdlib functions
    for name, info in STDLIB_FUNCTIONS.items():
        if prefix and not name.lower().startswith(prefix.lower()):
            continue

        # Determine icon
        if info["category"] == "intramind":
            kind = lsp.CompletionItemKind.Class
        elif info["category"] == "rag":
            kind = lsp.CompletionItemKind.Module
        elif info["category"] in ("math", "statistics", "random"):
            kind = lsp.CompletionItemKind.Value
        elif info["category"] == "functional":
            kind = lsp.CompletionItemKind.Interface
        else:
            kind = lsp.CompletionItemKind.Function

        items.append(
            lsp.CompletionItem(
                label=name,
                kind=kind,
                detail=f"{name}{info['signature']} → {info['returns']}",
                documentation=lsp.MarkupContent(
                    kind=lsp.MarkupKind.Markdown,
                    value=f"**{name}**{info['signature']}\n\n{info['doc']}\n\n*Returns:* `{info['returns']}`\n\n*Category:* {info['category']}",
                ),
                insert_text=f"{name}($1)" if info['params'] else f"{name}()",
                insert_text_format=lsp.InsertTextFormat.Snippet,
                sort_text=f"0_{name}",  # stdlib first
            )
        )

    # 2. Keywords
    for kw in MOL_KEYWORDS:
        if prefix and not kw.lower().startswith(prefix.lower()):
            continue
        doc_text = KEYWORD_DOCS.get(kw, f"MOL keyword `{kw}`")
        items.append(
            lsp.CompletionItem(
                label=kw,
                kind=lsp.CompletionItemKind.Keyword,
                detail=f"keyword",
                documentation=lsp.MarkupContent(
                    kind=lsp.MarkupKind.Markdown,
                    value=doc_text,
                ),
                sort_text=f"2_{kw}",  # keywords after functions
            )
        )

    # 3. User-defined symbols
    user_defs = _extract_user_definitions(doc.source)
    for name, info in user_defs.items():
        if prefix and not name.lower().startswith(prefix.lower()):
            continue
        items.append(
            lsp.CompletionItem(
                label=name,
                kind=info["kind"],
                detail=info["detail"],
                documentation=lsp.MarkupContent(
                    kind=lsp.MarkupKind.Markdown,
                    value=info["doc"],
                ),
                sort_text=f"1_{name}",  # user defs between stdlib and keywords
            )
        )

    # 4. Snippets
    for snip in SNIPPETS:
        if prefix and not snip["label"].lower().startswith(prefix.lower()):
            continue
        items.append(
            lsp.CompletionItem(
                label=snip["label"],
                kind=snip["kind"],
                detail=snip["detail"],
                insert_text=snip["insertText"],
                insert_text_format=lsp.InsertTextFormat.Snippet,
                sort_text=f"3_{snip['label']}",  # snippets last
            )
        )

    # 5. Pipe operator suggestions (after |>)
    try:
        lines = doc.source.splitlines()
        line = lines[params.position.line] if params.position.line < len(lines) else ""
        before_cursor = line[:params.position.character]
        if "|>" in before_cursor:
            # After pipe — suggest pipe-friendly functions
            pipe_funcs = [
                "trim", "upper", "lower", "split", "join", "reverse", "sort",
                "flatten", "unique", "map", "filter", "reduce",
                "chunk", "embed", "store", "retrieve", "think",
                "display", "tap", "assert_min", "assert_not_null",
            ]
            for fn_name in pipe_funcs:
                if fn_name in STDLIB_FUNCTIONS and (not prefix or fn_name.startswith(prefix)):
                    info = STDLIB_FUNCTIONS[fn_name]
                    items.append(
                        lsp.CompletionItem(
                            label=f"|> {fn_name}",
                            kind=lsp.CompletionItemKind.Operator,
                            detail=f"pipe → {fn_name}{info['signature']}",
                            documentation=lsp.MarkupContent(
                                kind=lsp.MarkupKind.Markdown,
                                value=f"**Pipe: |> {fn_name}**\n\n{info['doc']}",
                            ),
                            insert_text=fn_name,
                            sort_text=f"0_pipe_{fn_name}",
                        )
                    )
    except Exception:
        pass

    return lsp.CompletionList(is_incomplete=False, items=items)


# ── Hover ─────────────────────────────────────────────────────────

@server.feature(lsp.TEXT_DOCUMENT_HOVER)
def hover(params: lsp.HoverParams) -> Optional[lsp.Hover]:
    doc = server.workspace.get_text_document(params.text_document.uri)
    word = _get_word_at_position(doc, params.position)

    if not word:
        return None

    # Check stdlib
    if word in STDLIB_FUNCTIONS:
        info = STDLIB_FUNCTIONS[word]
        params_doc = ""
        if info["params"]:
            params_doc = "\n\n**Parameters:**\n"
            for p in info["params"]:
                params_doc += f"- `{p['name']}` — {p['doc']}\n"

        md = f"## `{word}`{info['signature']}\n\n{info['doc']}{params_doc}\n\n**Returns:** `{info['returns']}`\n\n*Category: {info['category']}*"
        return lsp.Hover(
            contents=lsp.MarkupContent(kind=lsp.MarkupKind.Markdown, value=md)
        )

    # Check keywords
    if word in KEYWORD_DOCS:
        md = f"## `{word}` (keyword)\n\n{KEYWORD_DOCS[word]}"
        return lsp.Hover(
            contents=lsp.MarkupContent(kind=lsp.MarkupKind.Markdown, value=md)
        )

    # Check user definitions
    user_defs = _extract_user_definitions(doc.source)
    if word in user_defs:
        info = user_defs[word]
        md = f"## `{word}` ({info['detail']})\n\n{info['doc']}\n\nDefined at line {info['line'] + 1}"
        return lsp.Hover(
            contents=lsp.MarkupContent(kind=lsp.MarkupKind.Markdown, value=md)
        )

    # Pipe operator
    if word == "|>" or word == "pipe":
        md = "## `|>` Pipe Operator\n\nChain function calls left-to-right with **automatic tracing**.\n\n```mol\nlet result be \"hello\" |> upper |> split(\"\") |> reverse\n```\n\nWhen 3+ stages are chained, MOL automatically traces timing and types at each step."
        return lsp.Hover(
            contents=lsp.MarkupContent(kind=lsp.MarkupKind.Markdown, value=md)
        )

    return None


# ── Signature Help ────────────────────────────────────────────────

@server.feature(
    lsp.TEXT_DOCUMENT_SIGNATURE_HELP,
    lsp.SignatureHelpOptions(trigger_characters=["(", ","]),
)
def signature_help(params: lsp.SignatureHelpParams) -> Optional[lsp.SignatureHelp]:
    doc = server.workspace.get_text_document(params.text_document.uri)

    try:
        lines = doc.source.splitlines()
        if params.position.line >= len(lines):
            return None
        line = lines[params.position.line]
        col = params.position.character

        # Walk back to find function name and opening paren
        before = line[:col]

        # Count commas to determine active parameter
        paren_depth = 0
        comma_count = 0
        func_name = ""
        for i in range(len(before) - 1, -1, -1):
            ch = before[i]
            if ch == ')':
                paren_depth += 1
            elif ch == '(':
                if paren_depth == 0:
                    # Found the opening paren — extract func name
                    j = i - 1
                    while j >= 0 and (before[j].isalnum() or before[j] == '_'):
                        j -= 1
                    func_name = before[j+1:i]
                    break
                paren_depth -= 1
            elif ch == ',' and paren_depth == 0:
                comma_count += 1

        if not func_name or func_name not in STDLIB_FUNCTIONS:
            return None

        info = STDLIB_FUNCTIONS[func_name]
        param_infos = []
        for p in info["params"]:
            param_infos.append(
                lsp.ParameterInformation(
                    label=p["name"],
                    documentation=lsp.MarkupContent(
                        kind=lsp.MarkupKind.Markdown,
                        value=p["doc"],
                    ),
                )
            )

        sig = lsp.SignatureInformation(
            label=f"{func_name}{info['signature']}",
            documentation=lsp.MarkupContent(
                kind=lsp.MarkupKind.Markdown,
                value=info["doc"],
            ),
            parameters=param_infos,
        )

        active_param = min(comma_count, len(param_infos) - 1) if param_infos else 0

        return lsp.SignatureHelp(
            signatures=[sig],
            active_signature=0,
            active_parameter=active_param,
        )
    except Exception:
        return None


# ── Go to Definition ──────────────────────────────────────────────

@server.feature(lsp.TEXT_DOCUMENT_DEFINITION)
def definition(params: lsp.DefinitionParams) -> Optional[lsp.Location]:
    doc = server.workspace.get_text_document(params.text_document.uri)
    word = _get_word_at_position(doc, params.position)

    if not word:
        return None

    user_defs = _extract_user_definitions(doc.source)
    if word in user_defs:
        line = user_defs[word]["line"]
        return lsp.Location(
            uri=doc.uri,
            range=lsp.Range(
                start=lsp.Position(line=line, character=0),
                end=lsp.Position(line=line, character=0),
            ),
        )

    return None


# ── Document Symbols ──────────────────────────────────────────────

@server.feature(lsp.TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbols(params: lsp.DocumentSymbolParams) -> list[lsp.DocumentSymbol]:
    doc = server.workspace.get_text_document(params.text_document.uri)
    symbols: list[lsp.DocumentSymbol] = []

    user_defs = _extract_user_definitions(doc.source)
    for name, info in user_defs.items():
        line = info["line"]
        kind_map = {
            lsp.CompletionItemKind.Function: lsp.SymbolKind.Function,
            lsp.CompletionItemKind.Variable: lsp.SymbolKind.Variable,
        }
        sym_kind = kind_map.get(info["kind"], lsp.SymbolKind.Variable)

        symbols.append(
            lsp.DocumentSymbol(
                name=name,
                kind=sym_kind,
                range=lsp.Range(
                    start=lsp.Position(line=line, character=0),
                    end=lsp.Position(line=line, character=0),
                ),
                selection_range=lsp.Range(
                    start=lsp.Position(line=line, character=0),
                    end=lsp.Position(line=line, character=len(name)),
                ),
                detail=info["detail"],
            )
        )

    return symbols


# ── Entry Point ───────────────────────────────────────────────────

def main():
    """Start the MOL Language Server via stdio."""
    logging.basicConfig(level=logging.WARNING)
    server.start_io()


if __name__ == "__main__":
    main()
