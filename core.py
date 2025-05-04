from typing import Optional

from analyzer.parser import CodeParser
from analyzer.scanner import FileScanner
from constants import GeneratorType
from generator.text_generator import TextGenerator
from generator.mermaid_generator import MermaidDiagramGenerator


def generate_diagram(directory: str, entity: str, format_type: str = 'text',
                    depth: int = 1, output: Optional[str] = None):
    """
    Generate a diagram for a specific entity.

    Args:
        directory: The directory to scan for Python files.
        entity: The name of the entity to generate a diagram for.
        format_type: The format of the diagram ('text' or 'mermaid').
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
    if format_type == GeneratorType.Text:
        generator = TextGenerator(parser.entities)
    elif format_type == GeneratorType.Mermaid:
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