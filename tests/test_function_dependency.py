from pathlib import Path

from analyzer.parser import CodeParser
from generator.text_generator import TextGenerator

# Parse the dep_test.py file
parser = CodeParser()
parser.parse_file(Path(__file__).parent / "dep_test.py")

# Check if the dependency between class B and function test_func is correctly identified
if "B" in parser.entities:
    print("Class B found")
    b_entity = parser.entities["B"]
    print(f"Dependencies of B: {b_entity.dependencies}")
    if "test_func" in b_entity.dependencies:
        print("Dependency on test_func found")
    else:
        print("Dependency on test_func NOT found")
else:
    print("Class B not found")

# Check if test_func is correctly identified
if "test_func" in parser.entities:
    print("Function test_func found")
    test_func_entity = parser.entities["test_func"]
    print(f"Used by: {test_func_entity.used_by}")
    if "B" in test_func_entity.used_by:
        print("Used by B found")
    else:
        print("Used by B NOT found")
else:
    print("Function test_func not found")

# Generate a list diagram for B
if "B" in parser.entities:
    generator = TextGenerator(parser.entities)
    diagram = generator.generate("B")
    print("\nList Diagram for B:")
    print(diagram)
