"""Main module for diagrams.

This module serves as the main entry point for the diagrams tool.
It provides a high-level API that can be used programmatically.
"""
import argparse
import sys
from typing import Dict

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import radiolist_dialog

from analyzer.parser import CodeParser
from analyzer.scanner import FileScanner
from constants import GeneratorType
from core import generate_diagram


class EntityCompleter(Completer):
    """Completer for entity names with file information."""

    def __init__(self, entities: Dict[str, 'Entity']):
        self.entities = entities
        self.entity_names = list(entities.keys())

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for entity_name in self.entity_names:
            if word.lower() in entity_name.lower():
                entity = self.entities[entity_name]
                display_text = HTML(f'<b>{entity_name}</b> ({entity.type} in <i>{entity.file_path.name}</i>)')
                yield Completion(
                    entity_name,
                    start_position=-len(word),
                    display=display_text,
                    display_meta=f"{entity.file_path}"
                )


class FormatCompleter(Completer):
    """Completer for format selection."""

    def __init__(self, formats):
        self.formats = formats

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for format_type in self.formats:
            if word.lower() in format_type.lower():
                display_text = HTML(f'<b>{format_type}</b>')
                yield Completion(
                    format_type,
                    start_position=-len(word),
                    display=display_text
                )


def interactive_mode():
    """Run the diagrams tool in interactive mode."""

    # Ask for directory
    directory = prompt("Enter directory to scan for Python files: ", default=".")

    # Scan for Python files
    scanner = FileScanner()
    python_files = scanner.scan_directory(directory)

    # Parse the files
    parser = CodeParser()
    parser.parse_files(python_files)

    if not parser.entities:
        print("No entities found in the specified directory.")
        return 1

    # Ask for entity with autocomplete
    entity_completer = EntityCompleter(parser.entities)
    entity = prompt(
        "Select entity to generate diagram for: ",
        completer=entity_completer,
    )

    if not entity or entity not in parser.entities:
        print(f"Entity '{entity}' not found.")
        return 1

    # Ask for format with a simple selection
    format_choices = GeneratorType.get_options()
    # Create a list of options with indices
    options = [f"{i+1}. {format_choice}" for i, format_choice in enumerate(format_choices)]
    print("\nAvailable output formats:")
    print("\n".join(options))
    
    while True:
        selection = prompt("Select format (enter number): ")
        try:
            index = int(selection) - 1
            if 0 <= index < len(format_choices):
                format_type = format_choices[index]
                break
            else:
                print(f"Please enter a number between 1 and {len(format_choices)}")
        except ValueError:
            # Also allow direct format name entry
            if selection in format_choices:
                format_type = selection
                break
            print("Please enter a valid number or format name")

    # Ask for depth
    depth_str = prompt("Enter maximum depth of dependencies (default: 4): ", default="4")
    try:
        depth = int(depth_str)
    except ValueError:
        print(f"Invalid depth: {depth_str}")
        return 1

    # Ask for output file
    output = prompt("Enter output file path (leave empty for stdout): ", default="")
    if not output:
        output = None

    # Generate the diagram
    try:
        generate_diagram(directory, entity, format_type, depth, output)
        print(f"Diagram generated successfully{' and saved to ' + output if output else ''}.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def main():
    """Run the diagrams tool from the command line."""
    parser = argparse.ArgumentParser(description='Generate relationship diagrams for Python code.')
    parser.add_argument('directory', nargs='?', help='Directory to scan for Python files')
    parser.add_argument('--entity', help='Entity to generate diagram for')
    parser.add_argument('--format', choices=['text', 'mermaid', 'ascii'], default='text',
                        help='Output format (default: text)')
    parser.add_argument('--depth', type=int, default=4,
                        help='Maximum depth of dependencies to include (default: 4)')
    parser.add_argument('--output', help='Output file path (default: stdout)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')

    args = parser.parse_args()

    # Run in interactive mode if requested or if no directory is provided
    if args.interactive or not args.directory:
        return interactive_mode()

    # Traditional CLI mode
    if not args.entity:
        parser.error("the following arguments are required: --entity")

    try:
        generate_diagram(args.directory, args.entity, args.format, args.depth, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
