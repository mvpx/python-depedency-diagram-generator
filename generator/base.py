"""Base generator module for diagrams.

This module provides the base class for all diagram generators.
"""

from typing import Dict

from analyzer.entity import Entity


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
