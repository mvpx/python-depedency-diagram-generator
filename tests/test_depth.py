from pathlib import Path

from analyzer.entity import Entity
from generator.text_generator import TextGenerator
from generator.mermaid_generator import MermaidDiagramGenerator


def test_text_generator_depth():
    """Test that TextGenerator correctly handles depth=4."""
    # Create a chain of entities with dependencies
    entity1 = Entity('Entity1', 'class', Path('test.py'), 10)
    entity2 = Entity('Entity2', 'class', Path('test.py'), 20)
    entity3 = Entity('Entity3', 'class', Path('test.py'), 30)
    entity4 = Entity('Entity4', 'class', Path('test.py'), 40)
    entity5 = Entity('Entity5', 'class', Path('test.py'), 50)
    
    # Set up dependencies: Entity1 -> Entity2 -> Entity3 -> Entity4 -> Entity5
    entity1.add_dependency('Entity2')
    entity2.add_dependency('Entity3')
    entity3.add_dependency('Entity4')
    entity4.add_dependency('Entity5')
    
    # Set up used_by relationships (reverse of dependencies)
    entity2.add_used_by('Entity1')
    entity3.add_used_by('Entity2')
    entity4.add_used_by('Entity3')
    entity5.add_used_by('Entity4')
    
    # Create a generator with all entities
    entities = {
        'Entity1': entity1,
        'Entity2': entity2,
        'Entity3': entity3,
        'Entity4': entity4,
        'Entity5': entity5
    }
    generator = TextGenerator(entities)
    
    # Generate diagram with depth=4
    diagram = generator.generate('Entity1', depth=4)
    
    # Print the diagram
    print(diagram)
    
    # Check that all 4 levels of dependencies are included
    assert "- class Entity2" in diagram
    assert "  - class Entity3" in diagram
    assert "    - class Entity4" in diagram
    assert "      - class Entity5" in diagram
    
    # Check that all 4 levels of used_by are included
    # Note: Entity1 is the main entity, so it doesn't appear in the "Used by" section
    
    print("All assertions passed for TextGenerator!")
    
    # Test MermaidDiagramGenerator as well
    mermaid_generator = MermaidDiagramGenerator(entities)
    mermaid_diagram = mermaid_generator.generate('Entity1', depth=4)
    
    # Print the diagram
    print("\nMermaid Diagram:")
    print(mermaid_diagram)
    
    # Check that all entities are included in the diagram
    assert "Entity1[[Entity1]]" in mermaid_diagram
    assert "Entity2[[Entity2]]" in mermaid_diagram
    assert "Entity3[[Entity3]]" in mermaid_diagram
    assert "Entity4[[Entity4]]" in mermaid_diagram
    assert "Entity5[[Entity5]]" in mermaid_diagram
    
    # Check that all dependencies are included
    assert "Entity1 --> Entity2" in mermaid_diagram
    assert "Entity2 --> Entity3" in mermaid_diagram
    assert "Entity3 --> Entity4" in mermaid_diagram
    assert "Entity4 --> Entity5" in mermaid_diagram
    
    print("All assertions passed for MermaidDiagramGenerator!")

if __name__ == "__main__":
    test_text_generator_depth()