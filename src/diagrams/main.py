"""Main module for diagrams.

This module provides functionality to generate relationship diagrams for Python code.
It can scan Python files, analyze relationships between classes and functions,
and generate diagrams in various formats.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Tuple


class FileScanner:
    """
    A class to scan directories for Python files.

    This class provides methods to recursively scan directories and find all Python files.
    It can exclude specified directories and files.
    """

    def __init__(self, exclude_dirs: Set[str] = None, exclude_files: Set[str] = None):
        """
        Initialize the FileScanner.

        Args:
            exclude_dirs: A set of directory names to exclude from scanning.
            exclude_files: A set of file names to exclude from scanning.
        """
        self.exclude_dirs = exclude_dirs or {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}
        self.exclude_files = exclude_files or set()

    def scan_directory(self, directory: str) -> List[Path]:
        """
        Recursively scan a directory for Python files.

        Args:
            directory: The directory to scan.

        Returns:
            A list of Path objects representing the Python files found.
        """
        python_files = []

        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if file.endswith('.py') and file not in self.exclude_files:
                    python_files.append(Path(os.path.join(root, file)))

        return python_files


class Entity:
    """
    A class representing a code entity (class or function).

    This class stores information about a code entity, including its name,
    type, file path, and relationships with other entities.
    """

    def __init__(self, name: str, entity_type: str, file_path: Path, line_number: int):
        """
        Initialize an Entity.

        Args:
            name: The name of the entity.
            entity_type: The type of the entity ('class' or 'function').
            file_path: The path to the file containing the entity.
            line_number: The line number where the entity is defined.
        """
        self.name = name
        self.type = entity_type
        self.file_path = file_path
        self.line_number = line_number
        self.dependencies: Set[str] = set()
        self.used_by: Set[str] = set()

    def add_dependency(self, entity_name: str):
        """
        Add a dependency to this entity.

        Args:
            entity_name: The name of the entity this entity depends on.
        """
        self.dependencies.add(entity_name)

    def add_used_by(self, entity_name: str):
        """
        Add an entity that uses this entity.

        Args:
            entity_name: The name of the entity that uses this entity.
        """
        self.used_by.add(entity_name)

    def __str__(self) -> str:
        """Return a string representation of the entity."""
        return f"{self.type} {self.name} ({self.file_path}:{self.line_number})"


class CodeParser:
    """
    A class to parse Python code and extract entities and their relationships.

    This class uses the ast module to parse Python code and extract classes,
    functions, and their relationships.
    """

    def __init__(self):
        """Initialize the CodeParser."""
        self.entities: Dict[str, Entity] = {}

    def parse_file(self, file_path: Path):
        """
        Parse a Python file and extract entities and their relationships.

        Args:
            file_path: The path to the file to parse.
        """
        import ast

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=str(file_path))
            except SyntaxError:
                print(f"Syntax error in {file_path}, skipping")
                return

        # Add parent references to AST nodes
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node

        # Extract classes and functions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                entity = Entity(node.name, 'class', file_path, node.lineno)
                self.entities[node.name] = entity

                # Extract base classes as dependencies
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        entity.add_dependency(base.id)

            elif isinstance(node, ast.FunctionDef):
                # Skip methods (they are part of classes)
                parent_is_class = False
                try:
                    parent_is_class = isinstance(node.parent, ast.ClassDef)
                except AttributeError:
                    # If parent attribute doesn't exist, assume it's not a method
                    pass

                if not parent_is_class:
                    entity = Entity(node.name, 'function', file_path, node.lineno)
                    self.entities[node.name] = entity

        # Extract relationships
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    # Function call
                    if node.func.id in self.entities:
                        # Find the parent entity
                        parent = self._find_parent_entity(node)
                        if parent and parent.name in self.entities:
                            self.entities[parent.name].add_dependency(node.func.id)
                            self.entities[node.func.id].add_used_by(parent.name)

    def _find_parent_entity(self, node: Any) -> Optional[Any]:
        """
        Find the parent entity (class or function) of a node.

        Args:
            node: The AST node to find the parent for.

        Returns:
            The parent ClassDef or FunctionDef node, or None if not found.
        """
        import ast

        parent = getattr(node, 'parent', None)
        while parent:
            if isinstance(parent, (ast.ClassDef, ast.FunctionDef)):
                return parent
            parent = getattr(parent, 'parent', None)

        return None

    def parse_files(self, file_paths: List[Path]):
        """
        Parse multiple Python files.

        Args:
            file_paths: A list of paths to the files to parse.
        """
        for file_path in file_paths:
            self.parse_file(file_path)


class DiagramGenerator:
    """
    Base class for diagram generators.

    This class defines the interface for all diagram generators.
    """

    def __init__(self, entities: Dict[str, Entity]):
        """
        Initialize the DiagramGenerator.

        Args:
            entities: A dictionary of entities to include in the diagram.
        """
        self.entities = entities

    def generate(self, entity_name: str, depth: int = 1) -> str:
        """
        Generate a diagram for a specific entity.

        Args:
            entity_name: The name of the entity to generate a diagram for.
            depth: The maximum depth of dependencies to include.

        Returns:
            The generated diagram as a string.
        """
        raise NotImplementedError("Subclasses must implement generate()")


class ASCIIDiagramGenerator(DiagramGenerator):
    """
    A class to generate ASCII diagrams.

    This class generates simple ASCII diagrams showing entity relationships.
    """

    def generate(self, entity_name: str, depth: int = 1) -> str:
        """
        Generate an ASCII diagram for a specific entity.

        Args:
            entity_name: The name of the entity to generate a diagram for.
            depth: The maximum depth of dependencies to include.

        Returns:
            The generated ASCII diagram as a string.
        """
        if entity_name not in self.entities:
            return f"Entity '{entity_name}' not found"

        lines = [f"ASCII Diagram for {entity_name}", "=" * 40]

        # Add dependencies
        lines.append("\nDependencies:")
        self._add_dependencies(lines, entity_name, depth, 0, set())

        # Add entities that use this entity
        lines.append("\nUsed by:")
        self._add_used_by(lines, entity_name, depth, 0, set())

        return "\n".join(lines)

    def _add_dependencies(self, lines: List[str], entity_name: str, max_depth: int, 
                         current_depth: int, visited: Set[str]):
        """
        Add dependencies to the diagram.

        Args:
            lines: The list of lines to add to.
            entity_name: The name of the entity to add dependencies for.
            max_depth: The maximum depth of dependencies to include.
            current_depth: The current depth in the dependency tree.
            visited: A set of already visited entities to avoid cycles.
        """
        if entity_name in visited or current_depth > max_depth:
            return

        visited.add(entity_name)

        if entity_name not in self.entities:
            return

        entity = self.entities[entity_name]
        indent = "  " * current_depth

        for dep in entity.dependencies:
            if dep in self.entities:
                dep_entity = self.entities[dep]
                lines.append(f"{indent}- {dep_entity.type} {dep}")
                self._add_dependencies(lines, dep, max_depth, current_depth + 1, visited.copy())

    def _add_used_by(self, lines: List[str], entity_name: str, max_depth: int, 
                    current_depth: int, visited: Set[str]):
        """
        Add entities that use this entity to the diagram.

        Args:
            lines: The list of lines to add to.
            entity_name: The name of the entity to add used_by for.
            max_depth: The maximum depth of used_by to include.
            current_depth: The current depth in the used_by tree.
            visited: A set of already visited entities to avoid cycles.
        """
        if entity_name in visited or current_depth > max_depth:
            return

        visited.add(entity_name)

        if entity_name not in self.entities:
            return

        entity = self.entities[entity_name]
        indent = "  " * current_depth

        for used_by in entity.used_by:
            if used_by in self.entities:
                used_by_entity = self.entities[used_by]
                lines.append(f"{indent}- {used_by_entity.type} {used_by}")
                self._add_used_by(lines, used_by, max_depth, current_depth + 1, visited.copy())


class MermaidDiagramGenerator(DiagramGenerator):
    """
    A class to generate Mermaid diagrams.

    This class generates Mermaid markdown diagrams showing entity relationships.
    """

    def generate(self, entity_name: str, depth: int = 1) -> str:
        """
        Generate a Mermaid diagram for a specific entity.

        Args:
            entity_name: The name of the entity to generate a diagram for.
            depth: The maximum depth of dependencies to include.

        Returns:
            The generated Mermaid diagram as a string.
        """
        if entity_name not in self.entities:
            return f"Entity '{entity_name}' not found"

        lines = ["```mermaid", "graph TD"]

        # Add the main entity
        entity = self.entities[entity_name]
        shape = "[[" if entity.type == "class" else "("
        shape_end = "]]" if entity.type == "class" else ")"
        lines.append(f"    {entity_name}{shape}{entity_name}{shape_end}")

        # Add dependencies
        visited = set()
        self._add_dependencies(lines, entity_name, depth, visited)

        # Add entities that use this entity
        self._add_used_by(lines, entity_name, depth, visited)

        lines.append("```")

        return "\n".join(lines)

    def _add_dependencies(self, lines: List[str], entity_name: str, max_depth: int, 
                         visited: Set[Tuple[str, str]]):
        """
        Add dependencies to the diagram.

        Args:
            lines: The list of lines to add to.
            entity_name: The name of the entity to add dependencies for.
            max_depth: The maximum depth of dependencies to include.
            visited: A set of already visited entity pairs to avoid cycles.
        """
        if max_depth <= 0 or entity_name not in self.entities:
            return

        entity = self.entities[entity_name]

        for dep in entity.dependencies:
            if dep in self.entities and (entity_name, dep) not in visited:
                visited.add((entity_name, dep))

                dep_entity = self.entities[dep]
                shape = "[[" if dep_entity.type == "class" else "("
                shape_end = "]]" if dep_entity.type == "class" else ")"

                lines.append(f"    {entity_name} --> {dep}")
                lines.append(f"    {dep}{shape}{dep}{shape_end}")

                self._add_dependencies(lines, dep, max_depth - 1, visited)

    def _add_used_by(self, lines: List[str], entity_name: str, max_depth: int, 
                    visited: Set[Tuple[str, str]]):
        """
        Add entities that use this entity to the diagram.

        Args:
            lines: The list of lines to add to.
            entity_name: The name of the entity to add used_by for.
            max_depth: The maximum depth of used_by to include.
            visited: A set of already visited entity pairs to avoid cycles.
        """
        if max_depth <= 0 or entity_name not in self.entities:
            return

        entity = self.entities[entity_name]

        for used_by in entity.used_by:
            if used_by in self.entities and (used_by, entity_name) not in visited:
                visited.add((used_by, entity_name))

                used_by_entity = self.entities[used_by]
                shape = "[[" if used_by_entity.type == "class" else "("
                shape_end = "]]" if used_by_entity.type == "class" else ")"

                lines.append(f"    {used_by} --> {entity_name}")
                lines.append(f"    {used_by}{shape}{used_by}{shape_end}")

                self._add_used_by(lines, used_by, max_depth - 1, visited)


def generate_diagram(directory: str, entity: str, format_type: str = 'ascii', 
                    depth: int = 1, output: Optional[str] = None):
    """
    Generate a diagram for a specific entity.

    Args:
        directory: The directory to scan for Python files.
        entity: The name of the entity to generate a diagram for.
        format_type: The format of the diagram ('ascii' or 'mermaid').
        depth: The maximum depth of dependencies to include.
        output: The output file path (if None, prints to stdout).
    """
    # Scan for Python files
    scanner = FileScanner()
    python_files = scanner.scan_directory(directory)

    # Parse the files
    parser = CodeParser()
    parser.parse_files(python_files)

    # Generate the diagram
    if format_type == 'ascii':
        generator = ASCIIDiagramGenerator(parser.entities)
    elif format_type == 'mermaid':
        generator = MermaidDiagramGenerator(parser.entities)
    else:
        raise ValueError(f"Unsupported format: {format_type}")

    diagram = generator.generate(entity, depth)

    # Output the diagram
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(diagram)
    else:
        print(diagram)


def main():
    """Run the diagrams tool from the command line."""
    parser = argparse.ArgumentParser(description='Generate relationship diagrams for Python code.')
    parser.add_argument('directory', help='Directory to scan for Python files')
    parser.add_argument('--entity', required=True, help='Entity to generate diagram for')
    parser.add_argument('--format', choices=['ascii', 'mermaid'], default='ascii',
                        help='Output format (default: ascii)')
    parser.add_argument('--depth', type=int, default=1,
                        help='Maximum depth of dependencies to include (default: 1)')
    parser.add_argument('--output', help='Output file path (default: stdout)')

    args = parser.parse_args()

    try:
        generate_diagram(args.directory, args.entity, args.format, args.depth, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
