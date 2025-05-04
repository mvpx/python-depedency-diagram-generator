# Python Code Relationship Diagram Generator

A tool to generate relationship diagrams for Python code, showing dependencies between classes and functions.

## Overview

This project provides a flexible and extensible way to visualize relationships between entities (classes and functions) in Python codebases. It allows you to select a specific entity and map its dependencies and the entities that use it, with control over the depth of the dependency tree.

## Features

- Scan all Python files in a directory and its subdirectories
- Generate relationship diagrams for specific classes or functions
- Control the depth of dependency mapping
- Ignore third-party libraries
- Interactive CLI mode with autocomplete for entity selection
- Support multiple output formats:
  - ASCII diagrams
  - Mermaid diagrams

## Setup

1. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```
   uv pip install -e .
   ```

3. Run tests:
   ```
   python -m pytest
   ```

## Usage Examples

### Command-line Arguments

```bash
# Generate an ASCII diagram for a specific class
python main.py --entity MyClass --format text --depth 2 path/to/project

# Generate a Mermaid diagram for a specific function
python main.py --entity my_function --format mermaid --depth 4 path/to/project

# Generate a diagram and save to a file
python main.py --entity MyClass --format text --output diagram.txt path/to/project
```

### Interactive Mode

```bash
# Start in interactive mode
python main.py
```

In interactive mode:
1. You'll be prompted to enter the directory to scan
2. You'll see a list of available entities with autocomplete as you type
3. You can select the output format (text or mermaid)
4. You can specify the depth (default is 4)
5. You can specify an output file (or leave empty to print to stdout)

## Project Structure

- `src/diagrams/`: Main package code
  - `analyzer/`: Code analysis module
  - `graph/`: Entity graph module
  - `generator/`: Diagram generator module
  - `cli.py`: Command-line interface
  - `main.py`: Main entry point
- `tests/`: Test files
- `pyproject.toml`: Project configuration

