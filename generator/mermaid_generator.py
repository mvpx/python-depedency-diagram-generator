"""Mermaid generator module for diagrams.

This module provides the MermaidDiagramGenerator class, which generates Mermaid markdown diagrams
showing entity relationships.
"""

from typing import List, Set, Tuple

from generator.base import DiagramGenerator


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
