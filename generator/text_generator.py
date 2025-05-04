from typing import List, Set

from generator.base import DiagramGenerator


class TextGenerator(DiagramGenerator):
    """
    A class to generate text diagrams.

    This class generates simple text diagrams showing entity relationships.
    """

    def generate(self, entity_name: str, depth: int = 1) -> str:
        """
        Generate a text diagram for a specific entity.

        Args:
            entity_name: The name of the entity to generate a diagram for.
            depth: The maximum depth of dependencies to include.

        Returns:
            The generated text diagram as a string.
        """
        if entity_name not in self.entities:
            return f"Entity '{entity_name}' not found"

        lines = [f"Text Diagram for {entity_name}", "=" * 40]

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
        if entity_name in visited or current_depth >= max_depth:
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
        if entity_name in visited or current_depth >= max_depth:
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
