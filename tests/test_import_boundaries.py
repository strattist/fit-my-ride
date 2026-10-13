"""Guard the dependency direction of AD-1 by scanning imports with ``ast``."""

import ast
import sys
from pathlib import Path

import pytest

ROOT = "fit_my_ride"
SRC = Path(__file__).resolve().parent.parent / "src" / ROOT

CORE_ALLOWED = set(sys.stdlib_module_names) | {ROOT}
FORBIDDEN = {
    "web": [f"{ROOT}.ingestion", f"{ROOT}.adapters"],
    "ingestion": [f"{ROOT}.web"],
}


def imported_modules(path: Path, package: str) -> set[str]:
    """Absolute dotted names imported by ``path``; ``package`` resolves relative imports."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = package.split(".")
                base = base[: len(base) - (node.level - 1)]
                prefix = ".".join(base + ([node.module] if node.module else []))
            else:
                prefix = node.module or ""
            names.add(prefix)
            names.update(f"{prefix}.{a.name}" for a in node.names)
    return names


def violations(layer: str, layer_dir: Path) -> list[str]:
    found = []
    for path in sorted(layer_dir.rglob("*.py")):
        rel = path.relative_to(layer_dir.parent).with_suffix("")
        package = ".".join((ROOT, *rel.parts[:-1])) if rel.parts[:-1] else ROOT
        if path.name == "__init__.py":
            package = ".".join((ROOT, *rel.parts[:-1]))
        for name in sorted(imported_modules(path, package)):
            top = name.split(".")[0]
            if layer == "core":
                bad = top not in CORE_ALLOWED or (
                    top == ROOT and not (name == ROOT or name.startswith(f"{ROOT}.core"))
                )
            else:
                bad = any(name == f or name.startswith(f + ".") for f in FORBIDDEN[layer])
            if bad:
                found.append(f"{path.name}: imports {name}")
    return found


@pytest.mark.parametrize("layer", ["core", "web", "ingestion"])
def test_layer_respects_boundaries(layer):
    assert violations(layer, SRC / layer) == []


@pytest.mark.parametrize(
    ("layer", "source"),
    [
        ("core", "import fastapi\n"),
        ("core", "from fit_my_ride.web import app\n"),
        ("core", "from .. import web\n"),
        ("web", "from fit_my_ride.ingestion import llm\n"),
        ("web", "from fit_my_ride import adapters\n"),
        ("ingestion", "import fit_my_ride.web.app\n"),
    ],
)
def test_violations_are_detected(tmp_path, layer, source):
    layer_dir = tmp_path / layer
    layer_dir.mkdir()
    (layer_dir / "bad.py").write_text(source)
    assert violations(layer, layer_dir) != []


def test_clean_core_module_passes(tmp_path):
    layer_dir = tmp_path / "core"
    layer_dir.mkdir()
    (layer_dir / "ok.py").write_text("import json\nfrom fit_my_ride.core import units\n")
    assert violations("core", layer_dir) == []
