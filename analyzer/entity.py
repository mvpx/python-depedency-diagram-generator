"""Entity module for diagrams.

This module provides the Entity class, representing a code entity (class or function).
"""

from pathlib import Path
from typing import Set


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
