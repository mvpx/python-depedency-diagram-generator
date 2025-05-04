from pathlib import Path

from analyzer.parser import CodeParser
from generator.mermaid_generator import MermaidDiagramGenerator

# Parse the dep_test.py file
parser = CodeParser()
parser.parse_file(Path("dep_test.py"))

# Generate a Mermaid diagram for B
if "B" in parser.entities:
    generator = MermaidDiagramGenerator(parser.entities)
    diagram = generator.generate("B")
    print("\nMermaid Diagram for B:")
    print(diagram)