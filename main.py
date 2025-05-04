"""Main module for diagrams.

This module serves as the main entry point for the diagrams tool.
It provides a high-level API that can be used programmatically.
"""
import argparse
import sys

from core import generate_diagram


def main():
    """Run the diagrams tool from the command line."""
    parser = argparse.ArgumentParser(description='Generate relationship diagrams for Python code.')
    parser.add_argument('directory', help='Directory to scan for Python files')
    parser.add_argument('--entity', required=True, help='Entity to generate diagram for')
    parser.add_argument('--format', choices=['text', 'mermaid'], default='text',
                        help='Output format (default: text)')
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
