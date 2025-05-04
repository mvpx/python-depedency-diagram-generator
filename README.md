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
  - Image files (PNG, SVG)

## Setup

1. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```
   uv pip install -e .
   ```

   For interactive mode with autocomplete:
   ```
   uv pip install -e ".[interactive]"
   ```

3. Run tests:
   ```
   python -m pytest
   ```

## Implementation Plan

### 1. Code Analysis Module

This module will be responsible for parsing Python code and extracting relationships between entities.

Components:
- **File Scanner**: Recursively scan directories for Python files
- **Code Parser**: Parse Python code to extract classes, functions, and their relationships
- **Relationship Analyzer**: Build a graph of relationships between entities

### 2. Entity Graph Module

This module will manage the graph representation of entities and their relationships.

Components:
- **Entity Node**: Represent a class or function
- **Relationship Edge**: Represent a relationship between two entities
- **Graph Manager**: Build and query the graph of entities

### 3. Diagram Generator Module

This module will generate diagrams in various formats based on the entity graph.

Components:
- **Base Generator**: Abstract class defining the interface for all generators
- **ASCII Generator**: Generate ASCII text diagrams
- **Mermaid Generator**: Generate Mermaid markdown diagrams
- **Image Generator**: Generate image files (PNG, SVG)

### 4. CLI Interface

A command-line interface to interact with the tool.

Features:
- Specify target directory
- Select entity to diagram
- Set dependency depth
- Choose output format
- Configure output location

## Usage Examples

### Command-line Arguments

```bash
# Generate an ASCII diagram for a specific class
python -m diagrams --entity MyClass --format text --depth 2 path/to/project

# Generate a Mermaid diagram for a specific function
python -m diagrams --entity my_function --format mermaid --depth 4 path/to/project

# Generate a diagram and save to a file
python -m diagrams --entity MyClass --format text --output diagram.txt path/to/project
```

### Interactive Mode

```bash
# Start in interactive mode
python -m diagrams -i

# Or simply run without arguments
python -m diagrams
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

## Development Roadmap

1. Implement the Code Analysis Module
2. Implement the Entity Graph Module
3. Implement the Diagram Generator Module with ASCII output
4. Add Mermaid diagram support
5. Add image output support
6. Implement the CLI interface
7. Add comprehensive tests
8. Create documentation and examples
