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

        lines = [
            "```mermaid",
            "graph TD",
            "    classDef classNode fill:#f9f,stroke:#333,stroke-width:2px,color:#000",
            "    classDef functionNode fill:#9cf,stroke:#333,stroke-width:2px,color:#000",
            "    classDef defaultNode fill:#lightgrey,stroke:#333,stroke-width:2px,color:#000"
        ]
        
        defined_nodes = set()
        
        # Define main entity and ensure it's processed first
        self._define_node_if_not_exists(lines, entity_name, defined_nodes)

        # Add dependencies
        visited_edges = set()
        self._add_dependencies(lines, entity_name, depth, visited_edges, defined_nodes)

        # Add entities that use this entity
        self._add_used_by(lines, entity_name, depth, visited_edges, defined_nodes)

        lines.append("```")
        return "\n".join(lines)

    def _get_node_style_and_shape(self, entity_type: str) -> Tuple[str, str, str]:
        if entity_type == "class":
            return "classNode", "[[", "]]"
        elif entity_type == "function": # Assuming 'function' type
            return "functionNode", "((", "))" # e.g., stadium shape for functions
        # Add more types here if needed
        else: # Default
            return "defaultNode", "(", ")"

    def _define_node_if_not_exists(self, lines: List[str], entity_id: str, defined_nodes: Set[str]):
        if entity_id in defined_nodes or entity_id not in self.entities:
            return

        entity = self.entities[entity_id]
        style_class, shape_start, shape_end = self._get_node_style_and_shape(entity.type)
        
        lines.append(f"    {entity_id}{shape_start}{entity_id}{shape_end}:::{style_class}")
        defined_nodes.add(entity_id)

    def _add_dependencies(self, lines: List[str], entity_name: str, max_depth: int, 
                         visited_edges: Set[Tuple[str, str]], defined_nodes: Set[str]):
        """
        Add dependencies to the diagram.

        Args:
            lines: The list of lines to add to.
            entity_name: The name of the entity to add dependencies for.
            max_depth: The maximum depth of dependencies to include.
            visited_edges: A set of already visited entity pairs (edges) to avoid cycles.
            defined_nodes: A set of entity IDs that have already been defined in the diagram.
        """
        if max_depth <= 0 or entity_name not in self.entities:
            return

        self._define_node_if_not_exists(lines, entity_name, defined_nodes)

        entity = self.entities[entity_name]

        for dep_name in entity.dependencies:
            if dep_name in self.entities:
                self._define_node_if_not_exists(lines, dep_name, defined_nodes)

                if (entity_name, dep_name) not in visited_edges:
                    visited_edges.add((entity_name, dep_name))
                    lines.append(f"    {entity_name} --> {dep_name}")
                    self._add_dependencies(lines, dep_name, max_depth - 1, visited_edges, defined_nodes)

    def _add_used_by(self, lines: List[str], entity_name: str, max_depth: int, 
                    visited_edges: Set[Tuple[str, str]], defined_nodes: Set[str]):
        """
        Add entities that use this entity to the diagram.

        Args:
            lines: The list of lines to add to.
            entity_name: The name of the entity to add used_by for.
            max_depth: The maximum depth of used_by to include.
            visited_edges: A set of already visited entity pairs (edges) to avoid cycles.
            defined_nodes: A set of entity IDs that have already been defined in the diagram.
        """
        if max_depth <= 0 or entity_name not in self.entities:
            return
        
        self._define_node_if_not_exists(lines, entity_name, defined_nodes)

        entity = self.entities[entity_name]

        for user_name in entity.used_by:
            if user_name in self.entities:
                self._define_node_if_not_exists(lines, user_name, defined_nodes)

                if (user_name, entity_name) not in visited_edges:
                    visited_edges.add((user_name, entity_name))
                    lines.append(f"    {user_name} --> {entity_name}")
                    self._add_used_by(lines, user_name, max_depth - 1, visited_edges, defined_nodes)
