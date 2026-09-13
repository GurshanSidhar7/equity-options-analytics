"""Execute Day 1 in a fresh kernel without writing outputs into the source notebook."""

from pathlib import Path

import nbformat
from nbclient import NotebookClient


if __name__ == "__main__":
    path = Path(__file__).parent / "notebooks" / "01_option_basics.ipynb"
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    NotebookClient(
        notebook,
        timeout=60,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
    ).execute()
    count = sum(cell.cell_type == "code" for cell in notebook.cells)
    print(f"PASS: {path.name} — {count} code cells executed, including all assertions.")
