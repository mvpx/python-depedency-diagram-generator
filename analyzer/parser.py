"""Parser module for diagrams.

This module provides functionality to parse Python code and extract entities and their relationships.
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Any

from analyzer.entity import Entity


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
                # Check if this is a method in a class
                parent_is_class = False
                parent_class = None
                try:
                    parent_is_class = isinstance(node.parent, ast.ClassDef)
                    if parent_is_class:
                        parent_class = node.parent
                except AttributeError:
                    # If parent attribute doesn't exist, assume it's not a method
                    pass

                if parent_is_class and node.name == '__init__':
                    # This is a constructor, check for type hints in parameters
                    for arg in node.args.args[1:]:  # Skip 'self'
                        if arg.annotation and isinstance(arg.annotation, ast.Name):
                            # Add dependency from the class to the type hint
                            if parent_class.name in self.entities and arg.annotation.id in self.entities:
                                self.entities[parent_class.name].add_dependency(arg.annotation.id)
                                self.entities[arg.annotation.id].add_used_by(parent_class.name)

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
            If a FunctionDef is found that is a method of a class, returns the ClassDef.
        """
        parent = getattr(node, 'parent', None)
        while parent:
            if isinstance(parent, ast.ClassDef):
                return parent
            elif isinstance(parent, ast.FunctionDef):
                # Check if this function is a method of a class
                method_parent = getattr(parent, 'parent', None)
                if method_parent and isinstance(method_parent, ast.ClassDef):
                    return method_parent
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
