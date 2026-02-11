#!/usr/bin/env python3
"""
MOL Distribution Builder
========================

Builds MOL as a closed-source binary package using multiple strategies:

1. PyInstaller  — Single executable binary (recommended, easiest)
2. Nuitka       — C-compiled binary (fastest, most obfuscated)
3. Cython       — Compiled .so/.pyd extensions (pip-installable)

Users get the `mol` CLI and can run .mol files, but cannot see
the interpreter source code.

Usage:
    python build_dist.py pyinstaller    # Build standalone binary
    python build_dist.py nuitka         # Build with Nuitka (needs gcc)
    python build_dist.py wheel          # Build obfuscated wheel
    python build_dist.py all            # Build everything
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
MOL_DIR = ROOT / "mol"
VERSION = "0.4.0"


def banner(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}\n")


def run(cmd, **kwargs):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=str(ROOT), **kwargs)
    if result.returncode != 0:
        print(f"  ✗ Command failed with exit code {result.returncode}")
        return False
    return True


def build_pyinstaller():
    """Build standalone binary with PyInstaller."""
    banner("Building with PyInstaller")

    # Check if pyinstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("  Installing PyInstaller...")
        run(f"{sys.executable} -m pip install pyinstaller")

    # Create spec for MOL
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# MOL PyInstaller spec — bundles interpreter into single binary

import os

block_cipher = None

a = Analysis(
    ['{MOL_DIR / "cli.py"}'],
    pathex=['{ROOT}'],
    binaries=[],
    datas=[
        ('{MOL_DIR / "grammar.lark"}', 'mol'),
    ],
    hiddenimports=['mol', 'mol.parser', 'mol.interpreter', 'mol.stdlib',
                   'mol.types', 'mol.transpiler', 'mol.cli', 'lark'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['pytest', 'mkdocs', 'playground'],
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='mol',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=True,
    icon=None,
)
'''

    spec_file = ROOT / "mol.spec"
    spec_file.write_text(spec_content)

    # Build
    success = run(f"{sys.executable} -m PyInstaller --clean --noconfirm mol.spec")

    if success:
        binary = DIST / "mol"
        if binary.exists():
            size_mb = binary.stat().st_size / (1024 * 1024)
            print(f"\n  ✓ Binary built: {binary}")
            print(f"  ✓ Size: {size_mb:.1f} MB")
            print(f"\n  Usage:")
            print(f"    ./dist/mol run program.mol")
            print(f"    ./dist/mol version")

    # Cleanup spec
    spec_file.unlink(missing_ok=True)
    return success


def build_nuitka():
    """Build with Nuitka (C compilation — maximum obfuscation)."""
    banner("Building with Nuitka")

    try:
        import nuitka
    except ImportError:
        print("  Installing Nuitka...")
        run(f"{sys.executable} -m pip install nuitka ordered-set")

    success = run(
        f"{sys.executable} -m nuitka "
        f"--onefile "
        f"--standalone "
        f"--output-dir={DIST}/nuitka "
        f"--output-filename=mol "
        f"--include-package=mol "
        f"--include-package=lark "
        f"--include-data-files={MOL_DIR / 'grammar.lark'}=mol/grammar.lark "
        f"--remove-output "
        f"--assume-yes-for-downloads "
        f"--no-pyi-file "
        f"{MOL_DIR / 'cli.py'}"
    )

    if success:
        binary = DIST / "nuitka" / "mol"
        if binary.exists():
            size_mb = binary.stat().st_size / (1024 * 1024)
            print(f"\n  ✓ Nuitka binary: {binary}")
            print(f"  ✓ Size: {size_mb:.1f} MB")
    return success


def build_wheel():
    """Build a standard wheel (pip-installable, bytecode only)."""
    banner("Building pip-installable wheel")

    # Clean old builds
    for d in [BUILD, DIST / "wheel"]:
        if d.exists():
            shutil.rmtree(d)

    # Build wheel
    success = run(f"{sys.executable} -m pip wheel . -w {DIST}/wheel --no-deps")

    if success:
        wheels = list((DIST / "wheel").glob("*.whl"))
        if wheels:
            print(f"\n  ✓ Wheel built: {wheels[0].name}")
            print(f"  ✓ Install: pip install {wheels[0]}")
    return success


def build_all():
    """Build all distribution formats."""
    banner("Building All Distributions")
    results = {}

    results["wheel"] = build_wheel()
    results["pyinstaller"] = build_pyinstaller()
    # Nuitka is optional (requires gcc)
    if shutil.which("gcc"):
        results["nuitka"] = build_nuitka()
    else:
        print("\n  ℹ Skipping Nuitka (gcc not found)")
        results["nuitka"] = None

    banner("Build Summary")
    for name, ok in results.items():
        status = "✓" if ok else ("⊘ skipped" if ok is None else "✗")
        print(f"  {status}  {name}")

    return all(v is not False for v in results.values())


def main():
    parser = argparse.ArgumentParser(
        description="MOL Distribution Builder — Build closed-source packages"
    )
    parser.add_argument(
        "target",
        choices=["pyinstaller", "nuitka", "wheel", "all"],
        help="Build target",
    )
    args = parser.parse_args()

    banner(f"MOL v{VERSION} — Distribution Builder")

    DIST.mkdir(exist_ok=True)

    targets = {
        "pyinstaller": build_pyinstaller,
        "nuitka": build_nuitka,
        "wheel": build_wheel,
        "all": build_all,
    }

    success = targets[args.target]()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
