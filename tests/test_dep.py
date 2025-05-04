from main import generate_diagram

def test_dep_diagram():
    """Test generating diagrams for dep_test.py."""
    # Try to generate a diagram for class A
    print("Generating diagram for class A:")
    generate_diagram("tests", "A", format_type="text", depth=4)
    
    print("\nGenerating Mermaid diagram for class A:")
    generate_diagram("tests", "A", format_type="mermaid", depth=4)

if __name__ == "__main__":
    test_dep_diagram()