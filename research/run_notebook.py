"""Execute educational notebooks in fresh kernels without modifying source files."""

from pathlib import Path

import nbformat
from nbclient import NotebookClient


if __name__ == "__main__":
    notebook_dir = Path(__file__).parent / "notebooks"
    for path in sorted(notebook_dir.glob("*.ipynb")):
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
