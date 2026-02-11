#!/usr/bin/env python3
"""
MOL CLI — Command-Line Interface for the MOL Language
======================================================

Usage:
  mol run <file.mol>           Run a MOL program
  mol parse <file.mol>         Show the AST (debug)
  mol transpile <file.mol>     Transpile to Python or JS
  mol repl                     Interactive REPL
  mol version                  Show version
"""

import sys
import os
import argparse

# Add the project root to path if needed
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mol import __version__
from mol.parser import parse
from mol.interpreter import Interpreter, MOLRuntimeError, MOLGuardError
from mol.stdlib import MOLSecurityError, MOLTypeError
from mol.transpiler import PythonTranspiler, JavaScriptTranspiler


# ── ANSI Colors ──────────────────────────────────────────────
class C:
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"
    DIM = "\033[2m"


BANNER = f"""{C.CYAN}{C.BOLD}
  ╔══════════════════════════════════════════╗
  ║   ███╗   ███╗  ██████╗  ██╗             ║
  ║   ████╗ ████║ ██╔═══██╗ ██║             ║
  ║   ██╔████╔██║ ██║   ██║ ██║             ║
  ║   ██║╚██╔╝██║ ██║   ██║ ██║             ║
  ║   ██║ ╚═╝ ██║ ╚██████╔╝ ███████╗       ║
  ║   ╚═╝     ╚═╝  ╚═════╝  ╚══════╝       ║
  ║                                          ║
  ║   The IntraMind Programming Language     ║
  ║   v{__version__:<37s}║
  ╚══════════════════════════════════════════╝
{C.RESET}"""


def run_file(filepath: str, show_output=True, trace=True):
    """Run a .mol file."""
    if not os.path.exists(filepath):
        print(f"{C.RED}Error: File not found: {filepath}{C.RESET}")
        sys.exit(1)

    with open(filepath, "r") as f:
        source = f.read()

    try:
        ast = parse(source)
        interp = Interpreter(trace=trace)
        interp.run(ast)
    except MOLGuardError as e:
        print(f"\n{C.RED}\U0001f6e1 Guard Error:{C.RESET} {e}")
        sys.exit(1)
    except MOLSecurityError as e:
        print(f"\n{C.RED}🔒 Security Error:{C.RESET} {e}")
        sys.exit(1)
    except MOLTypeError as e:
        print(f"\n{C.RED}🚫 Type Error:{C.RESET} {e}")
        sys.exit(1)
    except MOLRuntimeError as e:
        print(f"\n{C.RED}💥 Runtime Error:{C.RESET} {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{C.RED}❌ Parse/Compile Error:{C.RESET} {e}")
        sys.exit(1)


def show_ast(filepath: str):
    """Parse and display the AST of a .mol file."""
    if not os.path.exists(filepath):
        print(f"{C.RED}Error: File not found: {filepath}{C.RESET}")
        sys.exit(1)

    with open(filepath, "r") as f:
        source = f.read()

    try:
        ast = parse(source)
        _print_ast(ast, 0)
    except Exception as e:
        print(f"{C.RED}Parse Error:{C.RESET} {e}")
        sys.exit(1)


def _print_ast(node, depth):
    indent = "  " * depth
    if isinstance(node, list):
        for item in node:
            _print_ast(item, depth)
        return
    name = type(node).__name__
    fields = {k: v for k, v in node.__dict__.items() if k not in ('line', 'column')}

    simple_fields = {}
    complex_fields = {}
    for k, v in fields.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            simple_fields[k] = v
        else:
            complex_fields[k] = v

    attrs = " ".join(f"{C.YELLOW}{k}{C.RESET}={C.GREEN}{repr(v)}{C.RESET}" for k, v in simple_fields.items())
    print(f"{indent}{C.CYAN}{name}{C.RESET} {attrs}")

    for k, v in complex_fields.items():
        print(f"{indent}  {C.DIM}{k}:{C.RESET}")
        if isinstance(v, list):
            for item in v:
                if hasattr(item, '__dict__'):
                    _print_ast(item, depth + 2)
                elif isinstance(item, tuple):
                    print(f"{indent}    {C.MAGENTA}{item}{C.RESET}")
                else:
                    print(f"{indent}    {item}")
        elif hasattr(v, '__dict__'):
            _print_ast(v, depth + 2)
        else:
            print(f"{indent}    {v}")


def transpile_file(filepath: str, target: str = "python"):
    """Transpile a .mol file to Python or JavaScript."""
    if not os.path.exists(filepath):
        print(f"{C.RED}Error: File not found: {filepath}{C.RESET}")
        sys.exit(1)

    with open(filepath, "r") as f:
        source = f.read()

    try:
        ast = parse(source)
        if target == "javascript" or target == "js":
            transpiler = JavaScriptTranspiler()
        else:
            transpiler = PythonTranspiler()
        output = transpiler.transpile(ast)
        print(output)
    except Exception as e:
        print(f"{C.RED}Transpile Error:{C.RESET} {e}")
        sys.exit(1)


def repl():
    """Interactive MOL REPL."""
    print(BANNER)
    print(f"  {C.DIM}Type MOL code below. Use 'exit' or Ctrl+C to quit.{C.RESET}")
    print(f"  {C.DIM}Multi-line: end a line with '\\' to continue.{C.RESET}")
    print()

    interp = Interpreter()
    buffer = ""

    while True:
        try:
            prompt = f"{C.GREEN}mol>{C.RESET} " if not buffer else f"{C.YELLOW}...>{C.RESET} "
            line = input(prompt)

            if line.strip() == "exit":
                print(f"\n{C.CYAN}Goodbye from MOL! 👋{C.RESET}")
                break

            if line.endswith("\\"):
                buffer += line[:-1] + "\n"
                continue

            source = buffer + line
            buffer = ""

            if not source.strip():
                continue

            try:
                ast = parse(source)
                result = interp.run(ast)
                if result is not None:
                    print(f"{C.DIM}→ {interp._to_string(result)}{C.RESET}")
            except MOLSecurityError as e:
                print(f"{C.RED}🔒 {e}{C.RESET}")
            except MOLGuardError as e:
                print(f"{C.RED}🛡 {e}{C.RESET}")
            except MOLTypeError as e:
                print(f"{C.RED}🚫 {e}{C.RESET}")
            except MOLRuntimeError as e:
                print(f"{C.RED}💥 {e}{C.RESET}")
            except Exception as e:
                print(f"{C.RED}❌ {e}{C.RESET}")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{C.CYAN}Goodbye from MOL! 👋{C.RESET}")
            break


def main():
    parser = argparse.ArgumentParser(
        prog="mol",
        description="MOL — The IntraMind Programming Language",
    )
    sub = parser.add_subparsers(dest="command")

    # mol run
    run_p = sub.add_parser("run", help="Run a .mol program")
    run_p.add_argument("file", help="Path to .mol file")
    run_p.add_argument(
        "--trace", dest="trace", action="store_true", default=True,
        help="Enable pipeline tracing (default)",
    )
    run_p.add_argument(
        "--no-trace", dest="trace", action="store_false",
        help="Disable pipeline tracing",
    )

    # mol parse
    parse_p = sub.add_parser("parse", help="Show AST of a .mol file")
    parse_p.add_argument("file", help="Path to .mol file")

    # mol transpile
    trans_p = sub.add_parser("transpile", help="Transpile to Python or JS")
    trans_p.add_argument("file", help="Path to .mol file")
    trans_p.add_argument(
        "--target", "-t",
        choices=["python", "javascript", "js"],
        default="python",
        help="Target language (default: python)",
    )

    # mol repl
    sub.add_parser("repl", help="Interactive REPL")

    # mol version
    sub.add_parser("version", help="Show version")

    # mol lsp
    sub.add_parser("lsp", help="Start Language Server (stdio)")

    # mol init
    sub.add_parser("init", help="Create a new mol.pkg.json")

    # mol install
    install_p = sub.add_parser("install", help="Install a package")
    install_p.add_argument("package", help="Package name")
    install_p.add_argument("--version", "-v", default="latest", help="Version")

    # mol uninstall
    uninstall_p = sub.add_parser("uninstall", help="Uninstall a package")
    uninstall_p.add_argument("package", help="Package name")

    # mol list
    sub.add_parser("list", help="List installed packages")

    # mol search
    search_p = sub.add_parser("search", help="Search for packages")
    search_p.add_argument("query", help="Search query")

    # mol publish
    sub.add_parser("publish", help="Publish package to registry")

    # mol build
    build_p = sub.add_parser("build", help="Compile MOL to JS/WASM bundle")
    build_p.add_argument("file", help="Path to .mol file")
    build_p.add_argument(
        "--target", "-t",
        choices=["js", "browser", "node"],
        default="browser",
        help="Build target (default: browser)",
    )
    build_p.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path",
    )
    build_p.add_argument(
        "--minify", action="store_true",
        help="Minify the output",
    )

    args = parser.parse_args()

    if args.command == "run":
        run_file(args.file, trace=args.trace)
    elif args.command == "parse":
        show_ast(args.file)
    elif args.command == "transpile":
        transpile_file(args.file, args.target)
    elif args.command == "repl":
        repl()
    elif args.command == "version":
        print(f"MOL v{__version__}")
    elif args.command == "lsp":
        from mol.lsp_server import main as lsp_main
        lsp_main()
    elif args.command == "init":
        from mol.package_manager import cmd_init
        cmd_init()
    elif args.command == "install":
        from mol.package_manager import cmd_install
        cmd_install(args)
    elif args.command == "uninstall":
        from mol.package_manager import cmd_uninstall
        cmd_uninstall(args)
    elif args.command == "list":
        from mol.package_manager import cmd_list
        cmd_list()
    elif args.command == "search":
        from mol.package_manager import cmd_search
        cmd_search(args)
    elif args.command == "publish":
        from mol.package_manager import cmd_publish
        cmd_publish()
    elif args.command == "build":
        from mol.wasm_builder import cmd_build
        cmd_build(args)
    else:
        print(BANNER)
        parser.print_help()


if __name__ == "__main__":
    main()
