import os
from pathlib import Path
from diagrams.main import CodeParser, MermaidDiagramGenerator

# Parse the dep_test.py file
parser = CodeParser()
parser.parse_file(Path("tests/dep_test.py"))

# Generate a Mermaid diagram for B
if "B" in parser.entities:
    generator = MermaidDiagramGenerator(parser.entities)
    diagram = generator.generate("B")
    print("\nMermaid Diagram for B:")
    print(diagram)