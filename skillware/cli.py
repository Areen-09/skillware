import argparse
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from rich.table import Table
from rich.console import Console
from rich.text import Text
from rich import box

import importlib.metadata

from skillware.core.loader import SkillLoader
from skillware.version_policy import emit_upgrade_advisory, get_installed_version

TABLE_STYLE = "bold #C7CEEA"  # lavender  - headers
CATEGORY_STYLE = "bold #FFDAC1"  # peach     - category column
ID_STYLE = "#B5EAD7"  # mint      - skill ID column
BORDER_STYLE = "#C7CEEA"  # lavender  - table border

SPLASH_STYLE = "#C7CEEA"  # lavender  - skillware splash color
MENU_STYLE = "#FFDAC1"  # peach     - menu category


def _get_skill_roots(skills_root_override: Optional[Path] = None) -> List[Path]:
    """Return the list of roots to search for skills, mirrors SkillLoader resolution order."""
    if skills_root_override is not None:
        if skills_root_override.exists():
            return [skills_root_override]
        return []

    roots = []
    seen = set()

    for root in (
        SkillLoader._env_skill_roots()
        + SkillLoader._cwd_skill_roots()
        + [SkillLoader._bundled_skills_root()]
    ):
        resolved = root.resolve()
        if resolved not in seen and resolved.exists():
            seen.add(resolved)
            roots.append(resolved)

    return roots


def _short_description(data: Dict[str, Any], max_len: int = 80) -> str:
    """Return short_description if present, else first sentence of description truncated."""
    short = data.get("short_description", "").strip()
    if short:
        return short[:max_len] + ("…" if len(short) > max_len else "")

    desc = data.get("description", "").strip()

    seps = [".", "!", "?"]

    for sep in seps:
        idx = desc.find(sep)
        if idx != -1:
            desc = desc[: idx + 1]
            break

    return desc[:max_len] + ("…" if len(desc) > max_len else "")


def _discover_skills(
    skills_root_override: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Walk all skill roots and return a list of dicts with each skill's metadata."""
    roots = _get_skill_roots(skills_root_override)

    skills = []
    seen_ids = set()

    for root in roots:
        for manifest_path in root.glob("*/*/manifest.yaml"):

            if not SkillLoader._is_skill_dir(manifest_path.parent):
                continue

            with open(manifest_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            skill_id = f"{manifest_path.parent.parent.name}/{manifest_path.parent.name}"

            # skip duplicates found in multiple roots
            if skill_id in seen_ids:
                continue
            seen_ids.add(skill_id)

            issuer = data.get("issuer") or {}

            skills.append(
                {
                    "id": skill_id,
                    "category": manifest_path.parent.parent.name,
                    "name": manifest_path.parent.name,
                    "version": data.get("version", "?").strip(),
                    "description": _short_description(data),
                    "requirements": ", ".join(data.get("requirements") or []).strip(),
                    "issuer": issuer.get("github") or issuer.get("name") or "",
                }
            )

    return skills


def cmd_list(
    skills_root_override: Optional[Path] = None,
    category_filter: Optional[str] = None,
    issuer_filter: Optional[str] = None,
    console=None,
) -> None:
    """Print a formatted table of all available skills."""
    if console is None:
        console = Console()

    skills = _discover_skills(skills_root_override)

    if category_filter:
        skills = [s for s in skills if s["category"] == category_filter]

    if issuer_filter:
        skills = [s for s in skills if s["issuer"] == issuer_filter]

    if not skills:
        console.print("No skills found.")
        return

    table = Table(
        box=box.SIMPLE_HEAVY,
        border_style=BORDER_STYLE,
        header_style=TABLE_STYLE,
        expand=True,
    )

    table.add_column("ID", style=ID_STYLE, no_wrap=True, ratio=2)
    table.add_column("VERSION", style="dim", no_wrap=True, ratio=1)
    table.add_column("CATEGORY", style=CATEGORY_STYLE, no_wrap=True, ratio=1)
    table.add_column("ISSUER", style="dim", no_wrap=True, ratio=1)
    table.add_column("DESCRIPTION", ratio=3)
    table.add_column("REQUIREMENTS", style="dim", ratio=2)

    for skill in skills:
        table.add_row(
            skill["id"],
            skill["version"],
            skill["category"],
            skill["issuer"],
            skill["description"],
            skill["requirements"],
        )

    console.print(table)


def _print_menu(console, menu) -> None:
    for num, name, desc in menu:
        console.print(f"    [{num}] {name:<20}— {desc}", style=MENU_STYLE)

    console.print()


def cmd_help(console=None) -> None:
    """Print rich-formatted help to the console."""
    if console is None:
        console = Console()

    console.print(Text("Usage", style=f"bold {TABLE_STYLE}"))
    console.print("  skillware                     — open interactive menu")
    console.print("  skillware list                — list all installed skills")
    console.print("  skillware list --category <n> — filter by category")
    console.print("  skillware list --issuer <h>   — filter by issuer")
    console.print("  skillware list --skills-root  — override skills directory")
    console.print("  skillware --version           — print installed version")
    console.print()

    console.print(Text("Commands", style=f"bold {TABLE_STYLE}"))
    console.print("  list      available now", style=ID_STYLE)
    console.print("  paths     coming in #81", style="dim")
    console.print("  test      coming in #83", style="dim")
    console.print()

    console.print(Text("Interactive mode", style=f"bold {TABLE_STYLE}"))
    console.print(
        "  skillware                     — open interactive menu", style="dim"
    )
    console.print("  1-4 or command name           — select a menu option", style="dim")
    console.print("  q or Ctrl+C                   — exit", style="dim")
    console.print()

    console.print(Text("Examples", style=f"bold {TABLE_STYLE}"))
    console.print("  skillware list --category compliance", style=MENU_STYLE)
    console.print("  skillware list --issuer rosspeili", style=MENU_STYLE)
    console.print("  skillware list --skills-root /path/to/skills", style=MENU_STYLE)
    console.print()

    console.print(Text("Install", style=f"bold {TABLE_STYLE}"))
    console.print("  pip install skillware", style="dim")
    console.print()

    console.print(Text("Docs", style=f"bold {TABLE_STYLE}"))
    console.print(
        "  https://github.com/arpahls/skillware/blob/main/docs/usage/cli.md",
        style=f"dim {SPLASH_STYLE}",
    )


def cmd_interactive(console=None, parser=None) -> None:
    """Launch ASCII splash screen and interactive menu."""
    if console is None:
        console = Console()

    try:
        version = importlib.metadata.version("skillware")
    except importlib.metadata.PackageNotFoundError:
        version = "dev"

    splash = r"""
  ███████╗██╗  ██╗██╗██╗     ██╗    ██╗ █████╗ ██████╗ ███████╗
  ██╔════╝██║ ██╔╝██║██║     ██║    ██║██╔══██╗██╔══██╗██╔════╝
  ███████╗█████╔╝ ██║██║     ██║ █╗ ██║███████║██████╔╝█████╗
  ╚════██║██╔═██╗ ██║██║     ██║███╗██║██╔══██║██╔══██╗██╔══╝
  ███████║██║  ██╗██║███████╗╚███╔███╔╝██║  ██║██║  ██║███████╗
  ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝"""

    console.print(Text(splash, style=SPLASH_STYLE))
    console.print(
        Text(
            f"  Skill Management Framework — v{version}",
            style=f"dim {SPLASH_STYLE}",
        )
    )

    console.print(
        Text(
            "  https://skillware.site  ·  https://github.com/arpahls/skillware\n",
            style=f"dim {SPLASH_STYLE}",
        )
    )

    menu = [
        ("1", "list", "discover and display all locally installed skills"),
        ("2", "paths (soon, #81)", "show and repair skill directory resolution paths"),
        ("3", "test (soon, #83)", "run test_skill.py for one or all skills"),
        ("4", "help", "usage guide for any command"),
    ]

    commands = {
        "1": "list",
        "list": "list",
        "2": "paths",
        "paths": "paths",
        "3": "test",
        "test": "test",
        "4": "help",
        "help": "help",
    }

    _print_menu(console, menu)

    while True:
        try:
            choice = input("  > ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print("\n  Bye.", style="dim")
            return

        if choice == "q":
            console.print("  Bye.", style="dim")
            return

        command = commands.get(choice)

        if command == "list":
            cmd_list(console=console)
        elif command in ("paths", "test"):
            console.print(
                f"  '{command}' is not yet implemented. Coming in a future release.",
                style="dim",
            )
        elif command == "help":
            cmd_help(console=console)
        else:
            console.print(f"  Unknown command: '{choice}'", style="dim #FF9AA2")

        console.print()
        _print_menu(console, menu)


def main() -> None:
    """CLI entry point."""
    emit_upgrade_advisory()

    parser = argparse.ArgumentParser(prog="skillware", add_help=False)

    parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        help="Show this help message and exit.",
    )

    _ver = get_installed_version()
    _version_str = str(_ver) if _ver else "dev"

    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"skillware {_version_str}",
    )

    subparsers = parser.add_subparsers(dest="command")
    list_parser = subparsers.add_parser("list", help="List all available skills.")
    list_parser.add_argument(
        "--skills-root",
        type=Path,
        default=None,
        help="Override the skills directory path.",
    )
    list_parser.add_argument(
        "--category",
        default=None,
        help="Filter skills by category.",
    )
    list_parser.add_argument(
        "--issuer",
        default=None,
        help="Filter skills by issuer GitHub handle or name.",
    )

    args = parser.parse_args()

    if args.help and args.command is None:
        cmd_help(Console())
        return

    if args.command == "list":
        cmd_list(
            skills_root_override=args.skills_root,
            category_filter=args.category,
            issuer_filter=args.issuer,
        )
    else:
        cmd_interactive(parser=parser)


if __name__ == "__main__":
    main()
