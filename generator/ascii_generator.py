"""ASCII diagram generator module for diagrams.

This module provides the AsciiDiagramGenerator class, which generates ASCII diagrams
showing entity relationships.
"""

import collections
from typing import List, Set, Tuple, Dict, Deque

from generator.base import DiagramGenerator, Entity


class ASCIIDiagramGenerator(DiagramGenerator):
    """
    A class to generate ASCII diagrams.

    This class generates ASCII diagrams showing entity relationships.
    """

    def __init__(self, entities: Dict[str, Entity]):
        super().__init__(entities)
        self.char_map = {
            'top_left': '+', 'top_right': '+', 'bottom_left': '+', 'bottom_right': '+',
            'horizontal': '-', 'vertical': '|',
            'connector': 'o',
            'arrow_left': '<', 'arrow_right': '>', 'arrow_up': '^', 'arrow_down': 'v'
        }
        self.grid: Dict[Tuple[int, int], str] = {}
        self.min_x: int = 0
        self.min_y: int = 0
        self.max_x: int = 0
        self.max_y: int = 0

    def _draw_box(self, entity_name: str, entity_type: str, x_coord: int, y_coord: int) -> Tuple[int, int]:
        """Draws an ASCII box for an entity on the grid at (x_coord, y_coord).

        Args:
            entity_name: Name of the entity.
            entity_type: Type of the entity.
            x_coord: Top-left x-coordinate of the box.
            y_coord: Top-left y-coordinate of the box.

        Returns:
            A tuple (width, height) of the drawn box.
        """
        content_text = f" {entity_name} ({entity_type}) "
        content_width = len(content_text)
        
        box_width = content_width + 2 # 1 char for left border, 1 for right
        box_height = 3 # Top border, content, bottom border

        # Top border
        self._set_char(x_coord, y_coord, self.char_map['top_left'])
        for i in range(content_width):
            self._set_char(x_coord + 1 + i, y_coord, self.char_map['horizontal'])
        self._set_char(x_coord + content_width + 1, y_coord, self.char_map['top_right'])

        # Middle row (content)
        self._set_char(x_coord, y_coord + 1, self.char_map['vertical'])
        for i, char_content in enumerate(content_text):
            self._set_char(x_coord + 1 + i, y_coord + 1, char_content)
        self._set_char(x_coord + content_width + 1, y_coord + 1, self.char_map['vertical'])

        # Bottom border
        self._set_char(x_coord, y_coord + 2, self.char_map['bottom_left'])
        for i in range(content_width):
            self._set_char(x_coord + 1 + i, y_coord + 2, self.char_map['horizontal'])
        self._set_char(x_coord + content_width + 1, y_coord + 2, self.char_map['bottom_right'])
        
        return box_width, box_height

    def _collect_dependencies_recursive(self, source_entity_name: str, current_depth: int,
                                        all_nodes: Set[str], all_edges: Set[Tuple[str, str]],
                                        visited_paths: Set[Tuple[str, str]]):
        """Recursively collects dependencies for an entity."""
        if current_depth <= 0 or source_entity_name not in self.entities:
            return

        all_nodes.add(source_entity_name)
        entity = self.entities[source_entity_name]

        for dep_name in entity.dependencies:
            if dep_name not in self.entities: # Check if dependency exists in our known entities
                continue
            
            if (source_entity_name, dep_name) in visited_paths:
                continue  # Already processed this path

            visited_paths.add((source_entity_name, dep_name))
            all_nodes.add(dep_name)
            all_edges.add((source_entity_name, dep_name))
            self._collect_dependencies_recursive(dep_name, current_depth - 1, all_nodes, all_edges, visited_paths)

    def _collect_callers_recursive(self, target_entity_name: str, current_depth: int,
                                   all_nodes: Set[str], all_edges: Set[Tuple[str, str]],
                                   visited_paths: Set[Tuple[str, str]]):
        """Recursively collects callers (used_by) for an entity."""
        if current_depth <= 0 or target_entity_name not in self.entities:
            return

        all_nodes.add(target_entity_name)
        entity = self.entities[target_entity_name]

        for caller_name in entity.used_by:
            if caller_name not in self.entities: # Check if caller exists
                continue
            
            if (caller_name, target_entity_name) in visited_paths:
                continue  # Already processed this path
            
            visited_paths.add((caller_name, target_entity_name))
            all_nodes.add(caller_name)
            all_edges.add((caller_name, target_entity_name))
            self._collect_callers_recursive(caller_name, current_depth - 1, all_nodes, all_edges, visited_paths)

    def _set_char(self, x: int, y: int, char: str):
        """Sets a character at the specified position in the grid."""
        self.grid[(x, y)] = char
        # Update bounds. Assumes grid and bounds are reset in generate().
        if len(self.grid) == 1: # First character placed after grid reset
            self.min_x = x
            self.max_x = x + 1
            self.min_y = y
            self.max_y = y + 1
        else:
            self.min_x = min(self.min_x, x)
            self.max_x = max(self.max_x, x + 1)
            self.min_y = min(self.min_y, y)
            self.max_y = max(self.max_y, y + 1)

    def _render_grid(self) -> str:
        """Renders the grid content into a string."""
        if not self.grid:
            return "(Empty Diagram - Grid is empty)"

        output_lines = []
        # Iterate from min_x to max_x-1 and min_y to max_y-1
        for y_coord in range(self.min_y, self.max_y):
            line_chars = []
            for x_coord in range(self.min_x, self.max_x):
                line_chars.append(self.grid.get((x_coord, y_coord), ' ')) # Default to space
            output_lines.append("".join(line_chars))
        return "\n".join(output_lines)

    def generate(self, entity_name: str, depth: int = 1) -> str:
        """
        Generate a unified ASCII diagram for a specific entity, showing dependencies and callers
        using a layered layout.

        Args:
            entity_name: The name of the entity to generate a diagram for.
            depth: The maximum depth of relationships (both dependencies and callers) to include.

        Returns:
            The generated ASCII diagram as a string.
        """
        if entity_name not in self.entities:
            return f"Entity '{entity_name}' not found"

        # Reset grid for new diagram generation
        self.grid = {}
        self.min_x, self.min_y, self.max_x, self.max_y = 0, 0, 0, 0

        all_nodes: Set[str] = set()
        all_edges: Set[Tuple[str, str]] = set()
        visited_paths: Set[Tuple[str, str]] = set()
        
        # Collect all relevant nodes and edges
        # Start with the main entity to ensure it's included if isolated
        all_nodes.add(entity_name)
        self._collect_dependencies_recursive(entity_name, depth, all_nodes, all_edges, visited_paths)
        # Reset visited_paths for caller collection if you want to allow paths through entity_name again
        # For a unified graph, keeping visited_paths might be okay.
        self._collect_callers_recursive(entity_name, depth, all_nodes, all_edges, visited_paths)


        if not all_nodes:
            return f"ASCII Diagram for {entity_name} (depth {depth}):\n{'-' * 40}\n(No entities or relationships found to display)"

        # --- Layout Algorithm: Layered (Sugiyama-like concept) ---
        # 1. Assign levels (layers) to nodes
        #    - Main entity (entity_name) is at level 0.
        #    - Dependencies are at positive levels (1, 2, ...).
        #    - Callers are at negative levels (-1, -2, ...).
        node_levels: Dict[str, int] = {}
        
        # BFS for dependencies (positive levels)
        q_dep: Deque[Tuple[str, int]] = collections.deque()
        if entity_name in all_nodes: # Ensure entity_name is part of the graph to start BFS
            q_dep.append((entity_name, 0))
        
        visited_bfs_dep = {entity_name: 0} # Store node and its level
        node_levels[entity_name] = 0

        while q_dep:
            curr, level = q_dep.popleft()
            if abs(level) >= depth and curr != entity_name : # Check depth limit
                 continue
            for s, t in all_edges:
                if s == curr: # t is a dependency of curr
                    new_level = level + 1
                    if t in all_nodes and (t not in visited_bfs_dep or new_level < visited_bfs_dep[t]):
                        node_levels[t] = new_level
                        visited_bfs_dep[t] = new_level
                        if abs(new_level) < depth or (abs(new_level) == depth and t == entity_name): # Allow full depth
                           q_dep.append((t, new_level))
        
        # BFS for callers (negative levels)
        q_caller: Deque[Tuple[str, int]] = collections.deque()
        if entity_name in all_nodes:
            q_caller.append((entity_name, 0))

        visited_bfs_caller = {entity_name: 0} # Store node and its level
        # node_levels[entity_name] = 0 # Already set

        while q_caller:
            curr, level = q_caller.popleft()
            if abs(level) >= depth and curr != entity_name: # Check depth limit
                continue
            for s, t in all_edges:
                if t == curr: # s is a caller of curr
                    new_level = level - 1
                    if s in all_nodes and (s not in visited_bfs_caller or abs(new_level) < abs(visited_bfs_caller[s])): # Ensure we get the "closest" layer
                        node_levels[s] = new_level
                        visited_bfs_caller[s] = new_level
                        if abs(new_level) < depth or (abs(new_level) == depth and s == entity_name): # Allow full depth
                            q_caller.append((s, new_level))
        
        # Ensure all nodes in all_nodes have a level, default to 0 if somehow missed (e.g. isolated nodes not entity_name)
        for node in all_nodes:
            if node not in node_levels:
                node_levels[node] = 0 # Fallback, though ideally all nodes are reached

        # --- Organize Nodes by Level ---
        levels: Dict[int, List[str]] = collections.defaultdict(list)
        for node, lvl in node_levels.items():
            if node in all_nodes: # Only consider nodes that were collected
                 levels[lvl].append(node)
        for lvl in levels:
            levels[lvl].sort() # Sort nodes within each level for consistent output

        # --- Calculate Positions ---
        entity_positions: Dict[str, Tuple[int, int, int, int]] = {}
        box_dimensions: Dict[str, Tuple[int, int]] = {}
        max_widths_at_level: Dict[int, int] = collections.defaultdict(int)
        
        X_SPACING = 10  # Increased spacing for clarity
        Y_SPACING = 2
        
        # First pass: Calculate all box dimensions and max widths
        for node_name_calc in all_nodes:
            entity_obj = self.entities.get(node_name_calc)
            name_display = entity_obj.name if entity_obj else node_name_calc
            type_display = entity_obj.type if entity_obj else "Unknown"
            
            # Calculate box size (similar to _draw_box but without drawing)
            content_text = f" {name_display} ({type_display}) "
            content_width = len(content_text)
            box_w = content_width + 2
            box_h = 3
            box_dimensions[node_name_calc] = (box_w, box_h)
            
            level_of_node = node_levels.get(node_name_calc, 0) # Default to level 0 if not found
            max_widths_at_level[level_of_node] = max(max_widths_at_level[level_of_node], box_w)

        level_x_coords: Dict[int, int] = {}
        current_x_coord = 1
        sorted_level_indices = sorted(levels.keys())

        for level_idx_calc in sorted_level_indices:
            level_x_coords[level_idx_calc] = current_x_coord
            current_x_coord += max_widths_at_level[level_idx_calc] + X_SPACING
            
        # Second pass: Assign final positions and draw boxes
        for level_idx_draw in sorted_level_indices:
            current_y_coord = 1
            x_pos_for_level = level_x_coords[level_idx_draw]
            for node_name_draw in levels[level_idx_draw]:
                box_w_draw, box_h_draw = box_dimensions[node_name_draw]
                entity_obj_draw = self.entities.get(node_name_draw)

                if entity_obj_draw:
                    self._draw_box(entity_obj_draw.name, entity_obj_draw.type, x_pos_for_level, current_y_coord)
                else: # Draw placeholder for entities not in self.entities
                    placeholder_text = f" {node_name_draw} (details not found) "
                    content_width = len(placeholder_text)
                    # Recalculate box_w_draw for placeholder as it might differ
                    box_w_draw = content_width + 2 
                    # Manual placeholder drawing
                    self._set_char(x_pos_for_level, current_y_coord, self.char_map['top_left'])
                    for i in range(content_width):
                        self._set_char(x_pos_for_level + 1 + i, current_y_coord, self.char_map['horizontal'])
                    self._set_char(x_pos_for_level + content_width + 1, current_y_coord, self.char_map['top_right'])
                    self._set_char(x_pos_for_level, current_y_coord + 1, self.char_map['vertical'])
                    for i, char_content in enumerate(placeholder_text):
                        self._set_char(x_pos_for_level + 1 + i, current_y_coord + 1, char_content)
                    self._set_char(x_pos_for_level + content_width + 1, current_y_coord + 1, self.char_map['vertical'])
                    self._set_char(x_pos_for_level, current_y_coord + 2, self.char_map['bottom_left'])
                    for i in range(content_width):
                        self._set_char(x_pos_for_level + 1 + i, current_y_coord + 2, self.char_map['horizontal'])
                    self._set_char(x_pos_for_level + content_width + 1, current_y_coord + 2, self.char_map['bottom_right'])


                entity_positions[node_name_draw] = (x_pos_for_level, current_y_coord, box_w_draw, box_h_draw)
                current_y_coord += box_h_draw + Y_SPACING
        
        # Draw connections
        for source_node, target_node in sorted(list(all_edges)): # Sort for consistent arrow drawing order
            if source_node in entity_positions and target_node in entity_positions:
                source_pos_dims = entity_positions[source_node]
                target_pos_dims = entity_positions[target_node]
                self._draw_arrow(source_pos_dims, target_pos_dims)

        diagram_header = f"ASCII Diagram for {entity_name} (depth {depth}):"
        diagram_content = self._render_grid()
        return f"{diagram_header}\n{'=' * len(diagram_header)}\n\n{diagram_content}"

    def _draw_horizontal_segment(self, x1: int, y: int, x2: int, check_collision: bool = True):
        """Draws a horizontal line segment, optionally checking for collisions."""
        start_x, end_x = min(x1, x2), max(x1, x2)
        for x_coord in range(start_x, end_x + 1):
            existing_char = self.grid.get((x_coord, y), ' ')
            
            if check_collision and existing_char != ' ':
                if existing_char == self.char_map['vertical']:
                    self._set_char(x_coord, y, self.char_map['top_left'])  # Form '+'
                elif existing_char == self.char_map['horizontal']:
                    pass # Already '-', do nothing
                elif existing_char == self.char_map['top_left']: # Is '+'
                    pass # Already '+', do nothing
                else: # Box char or arrow head
                    continue # Skip drawing this point
            else: # Empty cell
                self._set_char(x_coord, y, self.char_map['horizontal'])

    def _draw_vertical_segment(self, x: int, y1: int, y2: int, check_collision: bool = True):
        """Draws a vertical line segment, optionally checking for collisions."""
        start_y, end_y = min(y1, y2), max(y1, y2)
        for y_coord in range(start_y, end_y + 1):
            existing_char = self.grid.get((x, y_coord), ' ')

            if check_collision and existing_char != ' ':
                if existing_char == self.char_map['horizontal']:
                    self._set_char(x, y_coord, self.char_map['top_left'])  # Form '+'
                elif existing_char == self.char_map['vertical']:
                    pass # Already '|', do nothing
                elif existing_char == self.char_map['top_left']: # Is '+'
                    pass # Already '+', do nothing
                else: # Box char or arrow head
                    continue # Skip drawing this point
            else: # Empty cell
                self._set_char(x, y_coord, self.char_map['vertical'])

    def _draw_arrow(self,
                    source_pos_dims: Tuple[int, int, int, int],
                    target_pos_dims: Tuple[int, int, int, int]):
        """Draws an arrow between two entities, attempting H-V-H or V-H-V routing."""
        sx, sy, sw, sh = source_pos_dims
        tx, ty, tw, th = target_pos_dims

        # Center points for rough direction
        s_center_x, s_center_y = sx + sw / 2, sy + sh / 2
        t_center_x, t_center_y = tx + tw / 2, ty + th / 2

        dx = t_center_x - s_center_x
        dy = t_center_y - s_center_y
        
        # Define exit/entry points on box edges
        # For simplicity, connect to middle of sides.
        s_exit_pts = {
            'right': (sx + sw -1 , sy + sh // 2), 
            'left': (sx, sy + sh // 2),
            'bottom': (sx + sw // 2, sy + sh -1), 
            'top': (sx + sw // 2, sy)
        }
        t_entry_pts = {
            'right': (tx + tw -1, ty + th // 2), 
            'left': (tx, ty + th // 2),
            'bottom': (tx + tw // 2, ty + th-1), 
            'top': (tx + tw // 2, ty) 
        }

        off = 1 # Offset for drawing lines just outside the box

        # Prefer H-V-H for horizontal dominant, V-H-V for vertical dominant
        if abs(dx) >= abs(dy):  # Primarily horizontal connection
            if dx > 0:  # Target is to the right
                start_x, start_y = s_exit_pts['right']
                end_x, end_y = t_entry_pts['left']
                arrow_char = self.char_map['arrow_right']
                mid_x = (start_x + end_x) // 2
                
                self._draw_horizontal_segment(start_x + off, start_y, mid_x, check_collision=True)
                self._set_char(mid_x, start_y, '+')
                self._draw_vertical_segment(mid_x, start_y, end_y, check_collision=True)
                self._set_char(mid_x, end_y, '+')
                self._draw_horizontal_segment(mid_x, end_y, end_x - off, check_collision=True)
                self._set_char(end_x - off, end_y, arrow_char) # Place arrow before box edge

            else:  # Target is to the left
                start_x, start_y = s_exit_pts['left']
                end_x, end_y = t_entry_pts['right']
                arrow_char = self.char_map['arrow_left']
                mid_x = (start_x + end_x) // 2

                self._draw_horizontal_segment(start_x - off, start_y, mid_x, check_collision=True)
                self._set_char(mid_x, start_y, '+')
                self._draw_vertical_segment(mid_x, start_y, end_y, check_collision=True)
                self._set_char(mid_x, end_y, '+')
                self._draw_horizontal_segment(mid_x, end_y, end_x + off, check_collision=True)
                self._set_char(end_x + off, end_y, arrow_char)

        else:  # Primarily vertical connection
            if dy > 0:  # Target is below
                start_x, start_y = s_exit_pts['bottom']
                end_x, end_y = t_entry_pts['top']
                arrow_char = self.char_map['arrow_down']
                mid_y = (start_y + end_y) // 2
                
                self._draw_vertical_segment(start_x, start_y + off, mid_y, check_collision=True)
                self._set_char(start_x, mid_y, '+')
                self._draw_horizontal_segment(start_x, mid_y, end_x, check_collision=True)
                self._set_char(end_x, mid_y, '+')
                self._draw_vertical_segment(end_x, mid_y, end_y - off, check_collision=True)
                self._set_char(end_x, end_y - off, arrow_char)

            else:  # Target is above
                start_x, start_y = s_exit_pts['top']
                end_x, end_y = t_entry_pts['bottom']
                arrow_char = self.char_map['arrow_up']
                mid_y = (start_y + end_y) // 2

                self._draw_vertical_segment(start_x, start_y - off, mid_y, check_collision=True)
                self._set_char(start_x, mid_y, '+')
                self._draw_horizontal_segment(start_x, mid_y, end_x, check_collision=True)
                self._set_char(end_x, mid_y, '+')
                self._draw_vertical_segment(end_x, mid_y, end_y + off, check_collision=True)
                self._set_char(end_x, end_y + off, arrow_char)
