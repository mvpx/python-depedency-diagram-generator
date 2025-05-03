# Python Code Relationship Diagram Generator

A tool to generate relationship diagrams for Python code, showing dependencies between classes and functions.

## Overview

This project provides a flexible and extensible way to visualize relationships between entities (classes and functions) in Python codebases. It allows you to select a specific entity and map its dependencies and the entities that use it, with control over the depth of the dependency tree.

## Features

- Scan all Python files in a directory and its subdirectories
- Generate relationship diagrams for specific classes or functions
- Control the depth of dependency mapping
- Ignore third-party libraries
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

```bash
# Generate an ASCII diagram for a specific class
python -m diagrams --entity MyClass --format ascii --depth 2 path/to/project

# Generate a Mermaid diagram for a specific function
python -m diagrams --entity my_function --format mermaid --depth 1 path/to/project

# Generate a PNG image
python -m diagrams --entity MyClass --format png --output diagram.png path/to/project
```

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
