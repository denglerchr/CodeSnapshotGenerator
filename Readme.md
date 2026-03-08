# Code Snapshot Generator

Code Snapshot Generator is a specialized Python tool designed to create clean, single-file Markdown summaries of your code projects. It is built specifically to prepare context-optimized code snapshots for Large Language Models (LLMs), allowing them to understand your architecture without exceeding token limits.

## ✨ Features

* **Smart Code Collapsing:** Uses Abstract Syntax Trees (AST) via `tree-sitter` to accurately identify and collapse function bodies in **Python**, **Go**, **Julia**, **JavaScript**, and **C#**, replacing them with lightweight comments.
* **Docstring Preservation:** Intelligently preserves Python docstrings when collapsing functions so LLMs retain the contextual explanation of the code.
* **ASCII Directory Tree:** Automatically generates a visual, bird's-eye view of your included project structure at the top of the Markdown file.
* **Robust Filtering:** Highly configurable inclusion and exclusion rules using a simple TOML file.
* **Universal Language Support:** Includes a comprehensive language map for correct Markdown code block decorators across 25+ file types (e.g., `.ts`, `.rs`, `.cpp`, `Dockerfile`).

## 🛠️ Prerequisites

* **Python 3.11+** (Requires the built-in `tomllib` module)
* **Tree-sitter and Grammars:** The tool uses official Tree-sitter bindings for accurate code parsing.

### Installation

The easiest way to install the required dependencies is using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt

```

*(This will install the core `tree-sitter` library along with the grammars for Python, Go, Julia, JavaScript, and C#).*

## ⚙️ Configuration

The tool is driven by a `.toml` configuration file. You can define exact files to include or traverse entire folders with specific include/exclude rules.

### Example `myproject.toml`

```toml
# Explicitly include specific files
[[Files]]
    Paths = [
        "C:/absolute/path/to/project/main.go",
        "C:/absolute/path/to/project/models.go"
    ]
    CollapseFunctions = true

# Traverse a folder with rules
[[Folders]]
    Paths = ["C:/absolute/path/to/project/internal"]
    Include = ".go,.md" # Only include these extensions
    Exclude = "config,tests" # Exact match subpaths to ignore completely
    CollapseFunctions = true

```

* **`Paths`**: A list of absolute paths to files or folders.
* **`Include`**: Comma-separated file extensions. Use an empty string `""` to include extensionless files (like `Dockerfile`).
* **`Exclude`**: Comma-separated folder names to skip during traversal.
* **`CollapseFunctions`**: If `true`, the tool will parse `.py`, `.go`, `.jl`, `.js`, and `.cs` files and remove the internal logic of functions.

## 🚀 Usage

Run the program by passing your configuration file as an argument:

```bash
python main.py path/to/myproject.toml

```

Upon success, the tool will generate a file named `myproject.md` in the same directory as your configuration file.
