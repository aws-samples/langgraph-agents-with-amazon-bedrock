#!/usr/bin/env python3
"""Normalize workshop notebooks before committing.

JupyterLab rewrites the embedded ``kernelspec`` and bumps
``language_info.version`` whenever a participant runs a notebook with the
local kernel picked from the kernel list (e.g. ``.venv`` / ``python3``).
That drift is noisy in diffs and hides real edits. The README also asks
participants to register a kernel called ``agents-dev-env`` (step 5), so
the embedded metadata should match that name regardless of which kernel
ran the notebook.

This script walks every ``Lab_*/Lab_*.ipynb`` and:

- clears ``outputs`` and ``execution_count`` on all code cells
- pins ``kernelspec`` to ``agents-dev-env``
- pins ``language_info.version`` to ``3.10.14`` (Jupyter rewrites this on
  save anyway, but a stable value keeps diffs clean)

Usage::

    python scripts/normalize_notebooks.py

Run before committing notebook changes. Exit code 0 always; the script
prints which files were normalized and which were already clean.
"""
from __future__ import annotations

import sys
from pathlib import Path

import nbformat

REPO_ROOT = Path(__file__).resolve().parent.parent

KERNELSPEC = {
    "display_name": "agents-dev-env",
    "language": "python",
    "name": "agents-dev-env",
}
LANGUAGE_VERSION = "3.10.14"


def normalize(path: Path) -> bool:
    """Normalize one notebook in place. Return True if the file changed."""
    nb = nbformat.read(path, as_version=4)
    changed = False

    metadata = nb.setdefault("metadata", {})

    if metadata.get("kernelspec") != KERNELSPEC:
        metadata["kernelspec"] = dict(KERNELSPEC)
        changed = True

    language_info = metadata.setdefault("language_info", {})
    if language_info.get("version") != LANGUAGE_VERSION:
        language_info["version"] = LANGUAGE_VERSION
        changed = True

    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        if cell.get("outputs") or cell.get("execution_count") is not None:
            cell["outputs"] = []
            cell["execution_count"] = None
            changed = True

    if changed:
        nbformat.write(nb, path)
    return changed


def main() -> int:
    notebooks = sorted(REPO_ROOT.glob("Lab_*/Lab_*.ipynb"))
    if not notebooks:
        print("No notebooks found under Lab_*/.", file=sys.stderr)
        return 1

    for nb_path in notebooks:
        rel = nb_path.relative_to(REPO_ROOT)
        if normalize(nb_path):
            print(f"normalized: {rel}")
        else:
            print(f"clean:      {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
