"""
MOL Package Manager — Install, manage, and publish MOL packages
================================================================

Registry: https://raw.githubusercontent.com/crux-ecosystem/mol-registry/main/index.json
Packages are stored in mol_packages/ in the project root.
Each package has a mol.pkg.json manifest.

Commands:
  mol init                    Create a new mol.pkg.json
  mol install <package>       Install a package from the registry
  mol uninstall <package>     Remove an installed package
  mol list                    List installed packages
  mol search <query>          Search the registry
  mol publish                 Publish to the registry
"""

import json
import os
import shutil
import sys
import hashlib
import zipfile
import tempfile
from pathlib import Path
from typing import Optional
from urllib import request, error


# ── Constants ────────────────────────────────────────────────
REGISTRY_URL = "https://raw.githubusercontent.com/crux-ecosystem/mol-registry/main/index.json"
FALLBACK_REGISTRY_URL = "https://mol-lang.github.io/registry/index.json"
PACKAGES_DIR = "mol_packages"
MANIFEST_FILE = "mol.pkg.json"
LOCK_FILE = "mol.lock.json"

# ── ANSI Colors ──────────────────────────────────────────────
class C:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    DIM = "\033[2m"
    RESET = "\033[0m"


# ── Built-in Packages (shipped with MOL) ────────────────────
BUILTIN_PACKAGES = {
    "std": {
        "name": "std",
        "version": "0.4.0",
        "description": "MOL standard library — all built-in functions",
        "author": "MOL Team",
        "builtin": True,
        "exports": [
            "len", "type_of", "to_text", "to_number", "range", "abs", "round",
            "sqrt", "max", "min", "sum", "sort", "reverse", "push", "pop",
            "keys", "values", "contains", "join", "split", "upper", "lower",
            "trim", "replace", "slice", "clock", "wait", "to_json", "from_json",
            "inspect", "map", "filter", "reduce", "flatten", "unique", "zip",
            "enumerate", "count", "find", "find_index", "take", "drop",
            "group_by", "chunk_list", "every", "some", "floor", "ceil", "log",
            "sin", "cos", "tan", "pi", "e", "pow", "clamp", "lerp", "mean",
            "median", "stdev", "variance", "percentile", "starts_with",
            "ends_with", "pad_left", "pad_right", "repeat", "char_at",
            "index_of", "format", "hash", "uuid", "base64_encode",
            "base64_decode", "sort_by", "sort_desc", "binary_search",
            "random", "random_int", "shuffle", "sample", "choice", "print",
            "merge", "pick", "omit", "is_null", "is_number", "is_text",
            "is_list", "is_map",
        ],
    },
    "math": {
        "name": "math",
        "version": "0.4.0",
        "description": "Math functions — sin, cos, tan, sqrt, constants",
        "author": "MOL Team",
        "builtin": True,
        "exports": [
            "abs", "round", "sqrt", "max", "min", "sum", "floor", "ceil",
            "log", "sin", "cos", "tan", "pi", "e", "pow", "clamp", "lerp",
            "mean", "median", "stdev", "variance", "percentile",
        ],
    },
    "text": {
        "name": "text",
        "version": "0.4.0",
        "description": "Text processing functions",
        "author": "MOL Team",
        "builtin": True,
        "exports": [
            "upper", "lower", "trim", "split", "join", "replace", "slice",
            "starts_with", "ends_with", "pad_left", "pad_right", "repeat",
            "char_at", "index_of", "format", "len", "contains",
        ],
    },
    "collections": {
        "name": "collections",
        "version": "0.4.0",
        "description": "Functional collection operations",
        "author": "MOL Team",
        "builtin": True,
        "exports": [
            "map", "filter", "reduce", "flatten", "unique", "zip",
            "enumerate", "count", "find", "find_index", "take", "drop",
            "group_by", "chunk_list", "every", "some", "sort", "sort_by",
            "sort_desc", "reverse", "push", "pop", "keys", "values",
        ],
    },
    "crypto": {
        "name": "crypto",
        "version": "0.4.0",
        "description": "Hashing and encoding utilities",
        "author": "MOL Team",
        "builtin": True,
        "exports": [
            "hash", "uuid", "base64_encode", "base64_decode",
        ],
    },
    "random": {
        "name": "random",
        "version": "0.4.0",
        "description": "Random number generation and sampling",
        "author": "MOL Team",
        "builtin": True,
        "exports": [
            "random", "random_int", "shuffle", "sample", "choice",
        ],
    },
    "rag": {
        "name": "rag",
        "version": "0.4.0",
        "description": "RAG pipeline utilities — chunk, embed, store, retrieve",
        "author": "MOL Team",
        "builtin": True,
        "exports": [
            "load_text", "chunk", "embed", "store", "retrieve", "cosine_sim",
            "think", "recall", "classify", "summarize", "display", "tap",
            "assert_min", "assert_not_null",
        ],
    },
}


# ── Manifest Management ─────────────────────────────────────

def find_project_root(start: str = ".") -> Path:
    """Walk up from start to find a directory containing mol.pkg.json."""
    path = Path(start).resolve()
    while path != path.parent:
        if (path / MANIFEST_FILE).exists():
            return path
        path = path.parent
    return Path(start).resolve()


def load_manifest(project_root: Path) -> dict:
    """Load mol.pkg.json from the project root."""
    manifest_path = project_root / MANIFEST_FILE
    if not manifest_path.exists():
        return {}
    with open(manifest_path) as f:
        return json.load(f)


def save_manifest(project_root: Path, manifest: dict):
    """Save mol.pkg.json to the project root."""
    manifest_path = project_root / MANIFEST_FILE
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def save_lockfile(project_root: Path, lock: dict):
    """Save mol.lock.json."""
    lock_path = project_root / LOCK_FILE
    with open(lock_path, "w") as f:
        json.dump(lock, f, indent=2)
        f.write("\n")


def load_lockfile(project_root: Path) -> dict:
    """Load mol.lock.json."""
    lock_path = project_root / LOCK_FILE
    if not lock_path.exists():
        return {"packages": {}}
    with open(lock_path) as f:
        return json.load(f)


# ── Registry Client ─────────────────────────────────────────

def fetch_registry() -> dict:
    """Fetch the package registry index."""
    for url in [REGISTRY_URL, FALLBACK_REGISTRY_URL]:
        try:
            req = request.Request(url, headers={"User-Agent": "mol-pkg/0.4.0"})
            with request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            continue

    # Return a local built-in registry if network is unavailable
    return {
        "packages": {
            name: {
                "name": info["name"],
                "version": info["version"],
                "description": info["description"],
                "author": info["author"],
                "latest": info["version"],
                "builtin": True,
            }
            for name, info in BUILTIN_PACKAGES.items()
        }
    }


def fetch_package(name: str, version: str = "latest") -> Optional[dict]:
    """Fetch package metadata from registry."""
    registry = fetch_registry()
    packages = registry.get("packages", {})

    if name in packages:
        return packages[name]

    # Check built-ins
    if name in BUILTIN_PACKAGES:
        return BUILTIN_PACKAGES[name]

    return None


def download_package(url: str, dest: Path) -> bool:
    """Download and extract a package archive."""
    try:
        req = request.Request(url, headers={"User-Agent": "mol-pkg/0.4.0"})
        with request.urlopen(req, timeout=30) as resp:
            data = resp.read()

        # Write to temp file and extract
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        with zipfile.ZipFile(tmp_path, "r") as zf:
            zf.extractall(dest)

        os.unlink(tmp_path)
        return True
    except Exception as exc:
        print(f"{C.RED}  Download failed: {exc}{C.RESET}")
        return False


# ── Package Resolution ───────────────────────────────────────

def resolve_package(name: str, version: str = "latest", project_root: Path = None) -> Path:
    """Resolve a package to its local path. Install if needed."""
    if project_root is None:
        project_root = find_project_root()

    pkg_dir = project_root / PACKAGES_DIR / name

    # Built-in packages don't need installation
    if name in BUILTIN_PACKAGES:
        return None  # Signal that this is a builtin

    if pkg_dir.exists():
        return pkg_dir

    return None


def get_package_exports(name: str, project_root: Path = None) -> dict:
    """
    Get exported symbols from a package.
    Returns a dict of {symbol_name: callable_or_value}.
    """
    from mol.stdlib import STDLIB

    # Built-in packages map to stdlib subsets
    if name in BUILTIN_PACKAGES:
        exports = {}
        for symbol_name in BUILTIN_PACKAGES[name]["exports"]:
            if symbol_name in STDLIB:
                exports[symbol_name] = STDLIB[symbol_name]
        return exports

    # User-installed packages
    if project_root is None:
        project_root = find_project_root()

    pkg_dir = project_root / PACKAGES_DIR / name
    if not pkg_dir.exists():
        return {}

    # Look for main entry point
    pkg_manifest = pkg_dir / MANIFEST_FILE
    if pkg_manifest.exists():
        with open(pkg_manifest) as f:
            meta = json.load(f)
        main_file = meta.get("main", "main.mol")
    else:
        main_file = "main.mol"

    main_path = pkg_dir / main_file
    if not main_path.exists():
        return {}

    # Parse and execute the package to get its exports
    from mol.parser import parse
    from mol.interpreter import Interpreter

    with open(main_path) as f:
        source = f.read()

    ast = parse(source)
    interp = Interpreter(trace=False)
    interp.run(ast)

    # Extract all user-defined symbols from the package's global env
    exports = {}
    for key, val in interp.global_env._store.items():
        # Skip stdlib functions that were injected
        if key not in STDLIB:
            exports[key] = val

    return exports


def load_mol_file(filepath: str, project_root: Path = None) -> dict:
    """
    Load a .mol file and return its exported symbols.
    Used for local file imports: use "path/to/file.mol"
    """
    from mol.parser import parse
    from mol.interpreter import Interpreter
    from mol.stdlib import STDLIB

    if project_root is None:
        project_root = find_project_root()

    # Resolve relative paths from project root
    full_path = Path(filepath)
    if not full_path.is_absolute():
        full_path = project_root / filepath

    if not full_path.exists():
        # Try with .mol extension
        if not filepath.endswith(".mol"):
            full_path = project_root / (filepath + ".mol")

    if not full_path.exists():
        raise FileNotFoundError(f"Cannot find module: {filepath}")

    with open(full_path) as f:
        source = f.read()

    ast = parse(source)
    interp = Interpreter(trace=False)
    interp.run(ast)

    # Collect user-defined exports
    exports = {}
    for key, val in interp.global_env._store.items():
        if key not in STDLIB:
            exports[key] = val

    return exports


# ── CLI Commands ─────────────────────────────────────────────

def cmd_init(args=None):
    """Create a new mol.pkg.json in the current directory."""
    root = Path(".").resolve()
    manifest_path = root / MANIFEST_FILE

    if manifest_path.exists():
        print(f"{C.YELLOW}mol.pkg.json already exists{C.RESET}")
        return

    name = root.name.lower().replace(" ", "-")
    manifest = {
        "name": name,
        "version": "0.1.0",
        "description": "",
        "author": "",
        "main": "main.mol",
        "license": "MIT",
        "dependencies": {},
        "keywords": [],
    }

    save_manifest(root, manifest)
    print(f"{C.GREEN}Created {MANIFEST_FILE}{C.RESET}")
    print(f'{C.DIM}  Edit "name", "description", "author" in {MANIFEST_FILE}{C.RESET}')


def cmd_install(args):
    """Install a package."""
    if not args or not args.package:
        print(f"{C.RED}Usage: mol install <package>{C.RESET}")
        return

    pkg_name = args.package
    version = getattr(args, "version", "latest") or "latest"
    root = find_project_root()

    print(f"{C.CYAN}Installing {pkg_name}...{C.RESET}")

    # Check if it's a built-in package
    if pkg_name in BUILTIN_PACKAGES:
        info = BUILTIN_PACKAGES[pkg_name]
        print(f"  {C.GREEN}✓{C.RESET} {pkg_name}@{info['version']} {C.DIM}(built-in, {len(info['exports'])} exports){C.RESET}")

        # Add to manifest dependencies
        manifest = load_manifest(root)
        if not manifest:
            manifest = {"dependencies": {}}
        if "dependencies" not in manifest:
            manifest["dependencies"] = {}
        manifest["dependencies"][pkg_name] = f"^{info['version']}"
        save_manifest(root, manifest)

        # Update lockfile
        lock = load_lockfile(root)
        lock["packages"][pkg_name] = {
            "version": info["version"],
            "builtin": True,
            "resolved": "builtin",
        }
        save_lockfile(root, lock)

        print(f"\n{C.GREEN}Installed 1 package{C.RESET}")
        _print_use_hint(pkg_name)
        return

    # Try registry
    pkg_info = fetch_package(pkg_name, version)
    if not pkg_info:
        print(f"{C.RED}Package not found: {pkg_name}{C.RESET}")
        print(f"{C.DIM}Available built-in packages: {', '.join(BUILTIN_PACKAGES.keys())}{C.RESET}")
        return

    # Download from registry
    download_url = pkg_info.get("download_url") or pkg_info.get("url")
    if download_url:
        pkg_dir = root / PACKAGES_DIR / pkg_name
        pkg_dir.mkdir(parents=True, exist_ok=True)

        if download_package(download_url, pkg_dir):
            print(f"  {C.GREEN}✓{C.RESET} {pkg_name}@{pkg_info.get('version', version)}")

            # Update manifest
            manifest = load_manifest(root)
            if not manifest:
                manifest = {"dependencies": {}}
            if "dependencies" not in manifest:
                manifest["dependencies"] = {}
            manifest["dependencies"][pkg_name] = f"^{pkg_info.get('version', version)}"
            save_manifest(root, manifest)

            # Update lockfile
            lock = load_lockfile(root)
            lock["packages"][pkg_name] = {
                "version": pkg_info.get("version", version),
                "resolved": download_url,
                "integrity": hashlib.sha256(open(pkg_dir / MANIFEST_FILE, "rb").read()).hexdigest() if (pkg_dir / MANIFEST_FILE).exists() else "",
            }
            save_lockfile(root, lock)

            print(f"\n{C.GREEN}Installed 1 package{C.RESET}")
            _print_use_hint(pkg_name)
        else:
            print(f"{C.RED}Failed to install {pkg_name}{C.RESET}")
    elif pkg_info.get("builtin"):
        # Built-in package from registry
        print(f"  {C.GREEN}✓{C.RESET} {pkg_name}@{pkg_info.get('version')} {C.DIM}(built-in){C.RESET}")
        print(f"\n{C.GREEN}Installed 1 package{C.RESET}")
        _print_use_hint(pkg_name)
    else:
        # Install from GitHub repository
        github_url = pkg_info.get("repository")
        if github_url:
            print(f"  {C.DIM}Cloning from {github_url}...{C.RESET}")
            pkg_dir = root / PACKAGES_DIR / pkg_name
            pkg_dir.mkdir(parents=True, exist_ok=True)

            import subprocess
            result = subprocess.run(
                ["git", "clone", "--depth", "1", github_url, str(pkg_dir)],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print(f"  {C.GREEN}✓{C.RESET} {pkg_name}@{pkg_info.get('version', 'latest')}")
                print(f"\n{C.GREEN}Installed 1 package{C.RESET}")
                _print_use_hint(pkg_name)
            else:
                print(f"{C.RED}Clone failed: {result.stderr}{C.RESET}")
        else:
            print(f"{C.RED}No download URL for {pkg_name}{C.RESET}")


def cmd_uninstall(args):
    """Uninstall a package."""
    if not args or not args.package:
        print(f"{C.RED}Usage: mol uninstall <package>{C.RESET}")
        return

    pkg_name = args.package
    root = find_project_root()

    # Remove from mol_packages/
    pkg_dir = root / PACKAGES_DIR / pkg_name
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
        print(f"  {C.GREEN}✓{C.RESET} Removed {pkg_name}")
    elif pkg_name in BUILTIN_PACKAGES:
        print(f"  {C.YELLOW}⚠{C.RESET} {pkg_name} is a built-in package — removing from dependencies only")
    else:
        print(f"  {C.YELLOW}⚠{C.RESET} Package {pkg_name} was not installed")

    # Remove from manifest
    manifest = load_manifest(root)
    if manifest and "dependencies" in manifest:
        if pkg_name in manifest["dependencies"]:
            del manifest["dependencies"][pkg_name]
            save_manifest(root, manifest)

    # Remove from lockfile
    lock = load_lockfile(root)
    if pkg_name in lock.get("packages", {}):
        del lock["packages"][pkg_name]
        save_lockfile(root, lock)

    print(f"{C.GREEN}Uninstalled {pkg_name}{C.RESET}")


def cmd_list(args=None):
    """List installed packages."""
    root = find_project_root()
    manifest = load_manifest(root)
    lock = load_lockfile(root)

    deps = manifest.get("dependencies", {}) if manifest else {}
    installed_pkgs = lock.get("packages", {})

    if not deps and not installed_pkgs:
        print(f"{C.DIM}No packages installed.{C.RESET}")
        print(f"{C.DIM}Run 'mol install <package>' to get started.{C.RESET}")
        print(f"\n{C.BOLD}Available built-in packages:{C.RESET}")
        for name, info in BUILTIN_PACKAGES.items():
            print(f"  {C.CYAN}{name}{C.RESET} — {info['description']} ({len(info['exports'])} exports)")
        return

    print(f"\n{C.BOLD}Installed Packages:{C.RESET}")
    print(f"{'─' * 60}")

    for name, version_spec in deps.items():
        locked = installed_pkgs.get(name, {})
        version = locked.get("version", version_spec)
        source = "built-in" if locked.get("builtin") or name in BUILTIN_PACKAGES else "registry"
        print(f"  {C.CYAN}{name:<20}{C.RESET} {version:<10} {C.DIM}({source}){C.RESET}")

    # Show mol_packages/ contents
    pkg_dir = root / PACKAGES_DIR
    if pkg_dir.exists():
        for entry in pkg_dir.iterdir():
            if entry.is_dir() and entry.name not in deps:
                print(f"  {C.YELLOW}{entry.name:<20}{C.RESET} {'local':<10} {C.DIM}(not in manifest){C.RESET}")

    print()


def cmd_search(args):
    """Search for packages."""
    if not args or not args.query:
        print(f"{C.RED}Usage: mol search <query>{C.RESET}")
        return

    query = args.query.lower()
    print(f"\n{C.BOLD}Searching for '{query}'...{C.RESET}\n")

    # Search built-in packages
    found = False
    for name, info in BUILTIN_PACKAGES.items():
        if query in name or query in info["description"].lower():
            print(f"  {C.CYAN}{name}{C.RESET}@{info['version']}")
            print(f"  {C.DIM}{info['description']}{C.RESET}")
            print(f"  {C.DIM}Exports: {', '.join(info['exports'][:8])}{'...' if len(info['exports']) > 8 else ''}{C.RESET}")
            print()
            found = True

    # Search online registry
    try:
        registry = fetch_registry()
        for name, info in registry.get("packages", {}).items():
            if name in BUILTIN_PACKAGES:
                continue  # Already shown
            desc = info.get("description", "")
            if query in name.lower() or query in desc.lower():
                print(f"  {C.CYAN}{name}{C.RESET}@{info.get('version', 'latest')}")
                print(f"  {C.DIM}{desc}{C.RESET}")
                print()
                found = True
    except Exception:
        pass

    if not found:
        print(f"  {C.DIM}No packages found for '{query}'{C.RESET}")
        print(f"  {C.DIM}Available built-in: {', '.join(BUILTIN_PACKAGES.keys())}{C.RESET}")


def cmd_publish(args=None):
    """Publish a package to the registry."""
    root = find_project_root()
    manifest = load_manifest(root)

    if not manifest:
        print(f"{C.RED}No mol.pkg.json found. Run 'mol init' first.{C.RESET}")
        return

    name = manifest.get("name")
    version = manifest.get("version")
    if not name or not version:
        print(f"{C.RED}Package must have 'name' and 'version' in mol.pkg.json{C.RESET}")
        return

    print(f"{C.CYAN}Publishing {name}@{version}...{C.RESET}")

    # Create package archive
    archive_name = f"{name}-{version}.zip"
    archive_path = root / "dist" / archive_name
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        main_file = manifest.get("main", "main.mol")
        # Add manifest
        zf.write(root / MANIFEST_FILE, MANIFEST_FILE)
        # Add main file
        if (root / main_file).exists():
            zf.write(root / main_file, main_file)
        # Add all .mol files
        for mol_file in root.glob("**/*.mol"):
            if PACKAGES_DIR not in str(mol_file) and ".venv" not in str(mol_file):
                rel_path = mol_file.relative_to(root)
                zf.write(mol_file, str(rel_path))

    size_kb = archive_path.stat().st_size / 1024
    sha = hashlib.sha256(archive_path.read_bytes()).hexdigest()

    print(f"  {C.GREEN}✓{C.RESET} Created {archive_name} ({size_kb:.1f} KB)")
    print(f"  {C.DIM}SHA256: {sha}{C.RESET}")
    print()
    print(f"{C.YELLOW}To publish to the MOL registry:{C.RESET}")
    print(f"  1. Push your package to GitHub")
    print(f"  2. Open a PR to mol-registry adding your package to index.json")
    print(f"  3. Or host the archive at a public URL and register it")
    print()
    print(f"{C.DIM}Archive saved to: dist/{archive_name}{C.RESET}")


# ── Helpers ──────────────────────────────────────────────────

def _print_use_hint(pkg_name: str):
    """Print usage hint after install."""
    if pkg_name in BUILTIN_PACKAGES:
        exports = BUILTIN_PACKAGES[pkg_name]["exports"][:4]
        print(f"\n{C.DIM}Usage in .mol files:{C.RESET}")
        print(f'  {C.CYAN}use "{pkg_name}"{C.RESET}                    -- import all exports')
        print(f'  {C.CYAN}use "{pkg_name}" : {", ".join(exports)}{C.RESET}  -- import specific')
    else:
        print(f"\n{C.DIM}Usage in .mol files:{C.RESET}")
        print(f'  {C.CYAN}use "{pkg_name}"{C.RESET}')
