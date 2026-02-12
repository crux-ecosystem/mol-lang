/**
 * MOL Runtime — JavaScript Standard Library
 * ==========================================
 * Complete port of MOL's stdlib to JavaScript.
 * Used by the WASM/browser compilation target.
 *
 * This file is bundled with compiled MOL programs
 * to provide all 90+ stdlib functions in the browser.
 */

const MOL_RUNTIME = (() => {
  "use strict";

  // ═══════════════════════════════════════════════════════════
  //  Domain Types
  // ═══════════════════════════════════════════════════════════

  class Thought {
    constructor(content, mood) {
      this.content = content || "";
      this.mood = mood || "neutral";
      this.created = Date.now();
      this.linked = [];
    }
    link(other) { this.linked.push(other); }
    mol_repr() { return `Thought("${this.content}", mood=${this.mood})`; }
  }

  class Memory {
    constructor(key, value) {
      this.key = key || "";
      this.value = value || null;
      this.created = Date.now();
      this.recalls = 0;
    }
    recall() { this.recalls++; return this.value; }
    mol_repr() { return `Memory("${this.key}")`; }
  }

  class Node {
    constructor(label, weight) {
      this.label = label || "";
      this.weight = weight || 1.0;
      this.connections = [];
      this.active = false;
    }
    connect(other) { this.connections.push(other); }
    activate() { this.active = true; }
    mol_repr() { return `Node("${this.label}", w=${this.weight})`; }
  }

  class Stream {
    constructor(name) {
      this.name = name || "";
      this.buffer = [];
      this.synced = false;
    }
    push(item) { this.buffer.push(item); }
    sync() { this.synced = true; }
    mol_repr() { return `Stream("${this.name}", len=${this.buffer.length})`; }
  }

  // ═══════════════════════════════════════════════════════════
  //  Standard Library Functions
  // ═══════════════════════════════════════════════════════════

  // ── General Utilities ──────────────────────────────────────
  function len(obj) {
    if (typeof obj === "string") return obj.length;
    if (Array.isArray(obj)) return obj.length;
    if (obj && typeof obj === "object") return Object.keys(obj).length;
    return 0;
  }

  function type_of(val) {
    if (val === null || val === undefined) return "null";
    if (typeof val === "number") return "Number";
    if (typeof val === "string") return "Text";
    if (typeof val === "boolean") return "Bool";
    if (Array.isArray(val)) return "List";
    if (val instanceof Thought) return "Thought";
    if (val instanceof Memory) return "Memory";
    if (val instanceof Node) return "Node";
    if (val instanceof Stream) return "Stream";
    if (typeof val === "object") return "Map";
    if (typeof val === "function") return "Function";
    return "Unknown";
  }

  function to_text(val) {
    if (val === null || val === undefined) return "null";
    if (typeof val === "string") return val;
    if (Array.isArray(val)) return JSON.stringify(val);
    if (typeof val === "object") return JSON.stringify(val);
    return String(val);
  }

  function to_number(val) {
    const n = Number(val);
    if (isNaN(n)) throw new Error(`Cannot convert '${val}' to number`);
    return n;
  }

  function range(...args) {
    let start, stop, step;
    if (args.length === 1) { start = 0; stop = args[0]; step = 1; }
    else if (args.length === 2) { start = args[0]; stop = args[1]; step = 1; }
    else { start = args[0]; stop = args[1]; step = args[2]; }
    const result = [];
    if (step > 0) { for (let i = start; i < stop; i += step) result.push(i); }
    else if (step < 0) { for (let i = start; i > stop; i += step) result.push(i); }
    return result;
  }

  // ── Math Functions ─────────────────────────────────────────
  const abs = Math.abs;
  function round_num(x, digits) {
    if (digits === undefined) return Math.round(x);
    const f = Math.pow(10, digits);
    return Math.round(x * f) / f;
  }
  const sqrt = Math.sqrt;
  const max = (...args) => args.length === 1 && Array.isArray(args[0]) ? Math.max(...args[0]) : Math.max(...args);
  const min = (...args) => args.length === 1 && Array.isArray(args[0]) ? Math.min(...args[0]) : Math.min(...args);
  const sum = (arr) => arr.reduce((a, b) => a + b, 0);
  const floor = Math.floor;
  const ceil = Math.ceil;
  const log = Math.log;
  const sin = Math.sin;
  const cos = Math.cos;
  const tan = Math.tan;
  const pi = () => Math.PI;
  const e = () => Math.E;
  const pow = Math.pow;
  function clamp(val, lo, hi) { return Math.max(lo, Math.min(hi, val)); }
  function lerp(a, b, t) { return a + (b - a) * t; }

  // ── Statistics ─────────────────────────────────────────────
  function mean(arr) { return sum(arr) / arr.length; }

  function median(arr) {
    const sorted = [...arr].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
  }

  function stdev(arr) {
    const m = mean(arr);
    const sq = arr.map(x => (x - m) ** 2);
    return Math.sqrt(sum(sq) / arr.length);
  }

  function variance(arr) {
    const m = mean(arr);
    return sum(arr.map(x => (x - m) ** 2)) / arr.length;
  }

  function percentile(arr, p) {
    const sorted = [...arr].sort((a, b) => a - b);
    const idx = (p / 100) * (sorted.length - 1);
    const lo = Math.floor(idx);
    const hi = Math.ceil(idx);
    if (lo === hi) return sorted[lo];
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
  }

  // ── List Functions ─────────────────────────────────────────
  function sort(arr) { return [...arr].sort((a, b) => a < b ? -1 : a > b ? 1 : 0); }
  function reverse(arr) { return [...arr].reverse(); }
  function push(arr, item) { return [...arr, item]; }
  function pop(arr) { return arr.slice(0, -1); }
  function keys(obj) { return Object.keys(obj); }
  function values(obj) { return Object.values(obj); }
  function contains(coll, item) {
    if (typeof coll === "string") return coll.includes(item);
    if (Array.isArray(coll)) return coll.includes(item);
    if (typeof coll === "object") return item in coll;
    return false;
  }

  // ── String Functions ───────────────────────────────────────
  function join(arr, sep) { return arr.join(sep === undefined ? "" : sep); }
  function split(str, sep) { return str.split(sep === undefined ? "" : sep); }
  function upper(str) { return str.toUpperCase(); }
  function lower(str) { return str.toLowerCase(); }
  function trim(str) { return str.trim(); }
  function replace(str, from, to) { return str.split(from).join(to); }
  function slice(obj, start, end) { return obj.slice(start, end); }
  function starts_with(str, prefix) { return str.startsWith(prefix); }
  function ends_with(str, suffix) { return str.endsWith(suffix); }
  function pad_left(str, len, ch) { return String(str).padStart(len, ch || " "); }
  function pad_right(str, len, ch) { return String(str).padEnd(len, ch || " "); }
  function repeat(str, n) { return str.repeat(n); }
  function char_at(str, idx) { return str.charAt(idx); }
  function index_of(str, sub) { return str.indexOf(sub); }
  function format(template, ...args) {
    let result = template;
    args.forEach((arg, i) => { result = result.replace(`{${i}}`, to_text(arg)); });
    return result;
  }

  // ── JSON ───────────────────────────────────────────────────
  function to_json(val) { return JSON.stringify(val); }
  function from_json(str) { return JSON.parse(str); }

  // ── Time ───────────────────────────────────────────────────
  function clock() { return Date.now() / 1000; }
  function wait(seconds) {
    return new Promise(resolve => setTimeout(resolve, seconds * 1000));
  }

  // ── Functional ─────────────────────────────────────────────
  function map_fn(arr, fn) { return arr.map(fn); }
  function filter_fn(arr, fn) { return arr.filter(fn); }
  function reduce_fn(arr, fn, init) {
    return init !== undefined ? arr.reduce(fn, init) : arr.reduce(fn);
  }
  function flatten(arr) { return arr.flat(Infinity); }
  function unique(arr) { return [...new Set(arr)]; }
  function zip_fn(a, b) { return a.map((x, i) => [x, b[i]]); }
  function enumerate_fn(arr) { return arr.map((x, i) => [i, x]); }
  function count(arr, fn) { return arr.filter(fn).length; }
  function find(arr, fn) { return arr.find(fn) ?? null; }
  function find_index(arr, fn) { return arr.findIndex(fn); }
  function take(arr, n) { return arr.slice(0, n); }
  function drop(arr, n) { return arr.slice(n); }
  function group_by(arr, fn) {
    return arr.reduce((acc, x) => {
      const key = fn(x);
      if (!acc[key]) acc[key] = [];
      acc[key].push(x);
      return acc;
    }, {});
  }
  function chunk_list(arr, size) {
    const result = [];
    for (let i = 0; i < arr.length; i += size) result.push(arr.slice(i, i + size));
    return result;
  }
  function every(arr, fn) { return arr.every(fn); }
  function some(arr, fn) { return arr.some(fn); }

  // ── Sorting ────────────────────────────────────────────────
  function sort_by(arr, fn) { return [...arr].sort((a, b) => { const va = fn(a), vb = fn(b); return va < vb ? -1 : va > vb ? 1 : 0; }); }
  function sort_desc(arr) { return [...arr].sort((a, b) => b - a); }
  function binary_search(arr, target) {
    let lo = 0, hi = arr.length - 1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      if (arr[mid] === target) return mid;
      if (arr[mid] < target) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
  }

  // ── Random ─────────────────────────────────────────────────
  function random() { return Math.random(); }
  function random_int(a, b) { return Math.floor(Math.random() * (b - a + 1)) + a; }
  function shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }
  function sample(arr, n) { return shuffle(arr).slice(0, n); }
  function choice(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

  // ── Crypto / Encoding ──────────────────────────────────────
  async function hash_fn(msg, algo) {
    if (typeof crypto !== "undefined" && crypto.subtle) {
      const algoMap = { "sha256": "SHA-256", "sha1": "SHA-1", "sha512": "SHA-512" };
      const buffer = new TextEncoder().encode(msg);
      const digest = await crypto.subtle.digest(algoMap[algo] || "SHA-256", buffer);
      return Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, "0")).join("");
    }
    // Fallback: simple hash
    let h = 0;
    for (let i = 0; i < msg.length; i++) { h = ((h << 5) - h + msg.charCodeAt(i)) | 0; }
    return Math.abs(h).toString(16);
  }

  function uuid() {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c => {
      const r = (Math.random() * 16) | 0;
      return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
    });
  }

  function base64_encode(str) { return btoa(str); }
  function base64_decode(str) { return atob(str); }

  // ── Inspection / Utility ────────────────────────────────────
  function inspect(val) {
    const t = type_of(val);
    return `<${t}: ${to_text(val)}>`;
  }

  function merge(...maps) { return Object.assign({}, ...maps); }
  function pick(obj, ...keys) {
    const result = {};
    keys.forEach(k => { if (k in obj) result[k] = obj[k]; });
    return result;
  }
  function omit(obj, ...keys) {
    const result = { ...obj };
    keys.forEach(k => delete result[k]);
    return result;
  }

  function is_null(val) { return val === null || val === undefined; }
  function is_number(val) { return typeof val === "number"; }
  function is_text(val) { return typeof val === "string"; }
  function is_list(val) { return Array.isArray(val); }
  function is_map(val) { return val !== null && typeof val === "object" && !Array.isArray(val); }

  // ── Domain Constructors ────────────────────────────────────
  function createThought(...args) { return new Thought(...args); }
  function createMemory(...args) { return new Memory(...args); }
  function createNode(...args) { return new Node(...args); }
  function createStream(...args) { return new Stream(...args); }

  // ── RAG / Pipeline ─────────────────────────────────────────
  function load_text(path) { return `[simulated content of ${path}]`; }
  function chunk(text, opts) {
    const size = (opts && opts.size) || 200;
    const chunks = [];
    for (let i = 0; i < text.length; i += size) chunks.push(text.slice(i, i + size));
    return chunks;
  }
  function embed(text) {
    const vec = [];
    for (let i = 0; i < 8; i++) vec.push(Math.sin(i + text.length * 0.1));
    return vec;
  }
  function store(vectors) { return { stored: true, count: vectors.length }; }
  function retrieve(query, k) { return [`result for "${query}" (1 of ${k || 3})`]; }
  function cosine_sim(a, b) {
    let dot = 0, na = 0, nb = 0;
    for (let i = 0; i < a.length; i++) { dot += a[i] * b[i]; na += a[i] ** 2; nb += b[i] ** 2; }
    return dot / (Math.sqrt(na) * Math.sqrt(nb));
  }
  function think(prompt) { return `[AI response to: ${prompt}]`; }
  function recall(query) { return `[recalled: ${query}]`; }
  function classify(text) { return "general"; }
  function summarize(text) { return text.slice(0, 100) + (text.length > 100 ? "..." : ""); }
  function display(val) { console.log(to_text(val)); return val; }
  function tap(val) { console.log("[tap]", to_text(val)); return val; }
  function assert_min(val, threshold) {
    if (val < threshold) throw new Error(`Value ${val} below minimum ${threshold}`);
    return val;
  }
  function assert_not_null(val) {
    if (val === null || val === undefined) throw new Error("Value is null");
    return val;
  }

  // ── Module Require (for use statements) ────────────────────
  const BUILTIN_MODULES = {};

  function __mol_require__(name) {
    if (BUILTIN_MODULES[name]) return BUILTIN_MODULES[name];
    throw new Error(`Module not found: ${name}. Only built-in modules are available in browser.`);
  }

  // ═══════════════════════════════════════════════════════════
  //  Exports — Global Registration
  // ═══════════════════════════════════════════════════════════

  const STDLIB = {
    // General
    len, type_of, to_text, to_number, range,
    // Math
    abs, round: round_num, sqrt, max, min, sum, floor, ceil, log,
    sin, cos, tan, pi, e, pow, clamp, lerp,
    // Stats
    mean, median, stdev, variance, percentile,
    // Lists
    sort, reverse, push, pop, keys, values, contains,
    // Strings
    join, split, upper, lower, trim, replace, slice,
    starts_with, ends_with, pad_left, pad_right, repeat,
    char_at, index_of, format,
    // JSON
    to_json, from_json,
    // Time
    clock, wait,
    // Functional
    map: map_fn, filter: filter_fn, reduce: reduce_fn,
    flatten, unique, zip: zip_fn, enumerate: enumerate_fn,
    count, find, find_index, take, drop,
    group_by, chunk_list, every, some,
    // Sorting
    sort_by, sort_desc, binary_search,
    // Random
    random, random_int, shuffle, sample, choice,
    // Crypto
    hash: hash_fn, uuid, base64_encode, base64_decode,
    // Inspection
    inspect, merge, pick, omit,
    is_null, is_number, is_text, is_list, is_map,
    // Domain constructors
    Thought: createThought, Memory: createMemory,
    Node: createNode, Stream: createStream,
    // RAG
    load_text, chunk, embed, store, retrieve, cosine_sim,
    think, recall, classify, summarize, display, tap,
    assert_min, assert_not_null,
    // Print
    print: (...args) => console.log(...args.map(to_text)),
    show: (...args) => console.log(...args.map(to_text)),
    // Internal
    __mol_require__,
  };

  // Build module subsets for `use "math"` etc.
  BUILTIN_MODULES["std"] = { ...STDLIB };
  BUILTIN_MODULES["math"] = {
    abs, round: round_num, sqrt, max, min, sum, floor, ceil, log,
    sin, cos, tan, pi, e, pow, clamp, lerp,
    mean, median, stdev, variance, percentile,
  };
  BUILTIN_MODULES["text"] = {
    upper, lower, trim, split, join, replace, slice,
    starts_with, ends_with, pad_left, pad_right, repeat,
    char_at, index_of, format, len, contains,
  };
  BUILTIN_MODULES["collections"] = {
    map: map_fn, filter: filter_fn, reduce: reduce_fn,
    flatten, unique, zip: zip_fn, enumerate: enumerate_fn,
    count, find, find_index, take, drop,
    group_by, chunk_list, every, some,
    sort, sort_by, sort_desc, reverse, push, pop, keys, values,
  };
  BUILTIN_MODULES["crypto"] = { hash: hash_fn, uuid, base64_encode, base64_decode };
  BUILTIN_MODULES["random"] = { random, random_int, shuffle, sample, choice };
  BUILTIN_MODULES["rag"] = {
    load_text, chunk, embed, store, retrieve, cosine_sim,
    think, recall, classify, summarize, display, tap,
    assert_min, assert_not_null,
  };

  return { STDLIB, BUILTIN_MODULES, __mol_require__, Thought, Memory, Node, Stream };
})();

// Register all stdlib in global scope
if (typeof globalThis !== "undefined") {
  Object.assign(globalThis, MOL_RUNTIME.STDLIB);
}
