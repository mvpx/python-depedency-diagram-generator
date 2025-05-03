"""Tests for the diagrams package."""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from diagrams.main import (
    FileScanner,
    Entity,
    CodeParser,
    ListGenerator,
    MermaidDiagramGenerator,
    generate_diagram,
    main
)


class TestFileScanner:
    """Tests for the FileScanner class."""

    def test_init_default_excludes(self):
        """Test that the default exclude directories and files are set correctly."""
        scanner = FileScanner()
        assert '.git' in scanner.exclude_dirs
        assert '.venv' in scanner.exclude_dirs
        assert 'venv' in scanner.exclude_dirs
        assert '__pycache__' in scanner.exclude_dirs
        assert 'node_modules' in scanner.exclude_dirs
        assert len(scanner.exclude_files) == 0

    def test_init_custom_excludes(self):
        """Test that custom exclude directories and files are set correctly."""
        scanner = FileScanner(exclude_dirs={'custom_dir'}, exclude_files={'custom_file.py'})
        assert 'custom_dir' in scanner.exclude_dirs
        assert 'custom_file.py' in scanner.exclude_files

    def test_scan_directory(self):
        """Test scanning a directory for Python files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some Python files
            with open(os.path.join(temp_dir, 'file1.py'), 'w') as f:
                f.write('# Test file 1')
            with open(os.path.join(temp_dir, 'file2.py'), 'w') as f:
                f.write('# Test file 2')

            # Create a subdirectory with a Python file
            os.makedirs(os.path.join(temp_dir, 'subdir'))
            with open(os.path.join(temp_dir, 'subdir', 'file3.py'), 'w') as f:
                f.write('# Test file 3')

            # Create an excluded directory with a Python file
            os.makedirs(os.path.join(temp_dir, '.git'))
            with open(os.path.join(temp_dir, '.git', 'file4.py'), 'w') as f:
                f.write('# Test file 4')

            # Scan the directory
            scanner = FileScanner()
            python_files = scanner.scan_directory(temp_dir)

            # Check that the correct files were found
            assert len(python_files) == 3
            assert Path(os.path.join(temp_dir, 'file1.py')) in python_files
            assert Path(os.path.join(temp_dir, 'file2.py')) in python_files
            assert Path(os.path.join(temp_dir, 'subdir', 'file3.py')) in python_files

            # Check that the excluded file was not found
            assert Path(os.path.join(temp_dir, '.git', 'file4.py')) not in python_files


class TestEntity:
    """Tests for the Entity class."""

    def test_init(self):
        """Test initializing an Entity."""
        entity = Entity('TestEntity', 'class', Path('test.py'), 10)
        assert entity.name == 'TestEntity'
        assert entity.type == 'class'
        assert entity.file_path == Path('test.py')
        assert entity.line_number == 10
        assert len(entity.dependencies) == 0
        assert len(entity.used_by) == 0

    def test_add_dependency(self):
        """Test adding a dependency to an Entity."""
        entity = Entity('TestEntity', 'class', Path('test.py'), 10)
        entity.add_dependency('Dependency1')
        entity.add_dependency('Dependency2')
        assert 'Dependency1' in entity.dependencies
        assert 'Dependency2' in entity.dependencies
        assert len(entity.dependencies) == 2

    def test_add_used_by(self):
        """Test adding a used_by to an Entity."""
        entity = Entity('TestEntity', 'class', Path('test.py'), 10)
        entity.add_used_by('UsedBy1')
        entity.add_used_by('UsedBy2')
        assert 'UsedBy1' in entity.used_by
        assert 'UsedBy2' in entity.used_by
        assert len(entity.used_by) == 2

    def test_str(self):
        """Test the string representation of an Entity."""
        entity = Entity('TestEntity', 'class', Path('test.py'), 10)
        assert str(entity) == 'class TestEntity (test.py:10)'


class TestCodeParser:
    """Tests for the CodeParser class."""

    def test_init(self):
        """Test initializing a CodeParser."""
        parser = CodeParser()
        assert len(parser.entities) == 0

    @patch('builtins.open', new_callable=mock_open, read_data="""
class TestClass:
    def __init__(self):
        pass

def test_function():
    pass
""")
    def test_parse_file(self, mock_file):
        """Test parsing a Python file."""
        parser = CodeParser()
        parser.parse_file(Path('test.py'))

        assert 'TestClass' in parser.entities
        assert parser.entities['TestClass'].type == 'class'
        assert parser.entities['TestClass'].file_path == Path('test.py')

        assert 'test_function' in parser.entities
        assert parser.entities['test_function'].type == 'function'
        assert parser.entities['test_function'].file_path == Path('test.py')

    @patch('builtins.open', new_callable=mock_open, read_data="""
class BaseClass:
    pass

class DerivedClass(BaseClass):
    pass

def caller_function():
    called_function()

def called_function():
    pass
""")
    def test_parse_file_relationships(self, mock_file):
        """Test parsing relationships between entities in a Python file."""
        parser = CodeParser()
        parser.parse_file(Path('test.py'))

        # Test inheritance relationship
        assert 'BaseClass' in parser.entities
        assert 'DerivedClass' in parser.entities
        assert 'BaseClass' in parser.entities['DerivedClass'].dependencies

        # Function call relationships can't be tested easily with mock data
        # because the AST doesn't have parent information in this context


class TestListGenerator:
    """Tests for the ListGenerator class."""

    def test_generate_entity_not_found(self):
        """Test generating a diagram for a non-existent entity."""
        generator = ListGenerator({})
        diagram = generator.generate('NonExistentEntity')
        assert "Entity 'NonExistentEntity' not found" in diagram

    def test_generate_simple_entity(self):
        """Test generating a diagram for a simple entity with no relationships."""
        entity = Entity('TestEntity', 'class', Path('test.py'), 10)
        generator = ListGenerator({'TestEntity': entity})
        diagram = generator.generate('TestEntity')

        assert "List Diagram for TestEntity" in diagram
        assert "Dependencies:" in diagram
        assert "Used by:" in diagram

    def test_generate_with_dependencies(self):
        """Test generating a diagram for an entity with dependencies."""
        entity1 = Entity('Entity1', 'class', Path('test.py'), 10)
        entity2 = Entity('Entity2', 'class', Path('test.py'), 20)
        entity1.add_dependency('Entity2')

        generator = ListGenerator({'Entity1': entity1, 'Entity2': entity2})
        diagram = generator.generate('Entity1')

        assert "List Diagram for Entity1" in diagram
        assert "Dependencies:" in diagram
        assert "- class Entity2" in diagram

    def test_generate_with_used_by(self):
        """Test generating a diagram for an entity that is used by other entities."""
        entity1 = Entity('Entity1', 'class', Path('test.py'), 10)
        entity2 = Entity('Entity2', 'class', Path('test.py'), 20)
        entity1.add_used_by('Entity2')

        generator = ListGenerator({'Entity1': entity1, 'Entity2': entity2})
        diagram = generator.generate('Entity1')

        assert "List Diagram for Entity1" in diagram
        assert "Used by:" in diagram
        assert "- class Entity2" in diagram


class TestMermaidDiagramGenerator:
    """Tests for the MermaidDiagramGenerator class."""

    def test_generate_entity_not_found(self):
        """Test generating a diagram for a non-existent entity."""
        generator = MermaidDiagramGenerator({})
        diagram = generator.generate('NonExistentEntity')
        assert "Entity 'NonExistentEntity' not found" in diagram

    def test_generate_simple_entity(self):
        """Test generating a diagram for a simple entity with no relationships."""
        entity = Entity('TestEntity', 'class', Path('test.py'), 10)
        generator = MermaidDiagramGenerator({'TestEntity': entity})
        diagram = generator.generate('TestEntity')

        assert "```mermaid" in diagram
        assert "graph TD" in diagram
        assert "TestEntity[[TestEntity]]" in diagram
        assert "```" in diagram

    def test_generate_with_dependencies(self):
        """Test generating a diagram for an entity with dependencies."""
        entity1 = Entity('Entity1', 'class', Path('test.py'), 10)
        entity2 = Entity('Entity2', 'function', Path('test.py'), 20)
        entity1.add_dependency('Entity2')

        generator = MermaidDiagramGenerator({'Entity1': entity1, 'Entity2': entity2})
        diagram = generator.generate('Entity1')

        assert "```mermaid" in diagram
        assert "graph TD" in diagram
        assert "Entity1[[Entity1]]" in diagram
        assert "Entity1 --> Entity2" in diagram
        assert "Entity2(Entity2)" in diagram
        assert "```" in diagram

    def test_generate_with_used_by(self):
        """Test generating a diagram for an entity that is used by other entities."""
        entity1 = Entity('Entity1', 'class', Path('test.py'), 10)
        entity2 = Entity('Entity2', 'function', Path('test.py'), 20)
        entity1.add_used_by('Entity2')

        generator = MermaidDiagramGenerator({'Entity1': entity1, 'Entity2': entity2})
        diagram = generator.generate('Entity1')

        assert "```mermaid" in diagram
        assert "graph TD" in diagram
        assert "Entity1[[Entity1]]" in diagram
        assert "Entity2 --> Entity1" in diagram
        assert "Entity2(Entity2)" in diagram
        assert "```" in diagram


@patch('diagrams.main.FileScanner')
@patch('diagrams.main.CodeParser')
@patch('diagrams.main.ListGenerator')
@patch('builtins.open', new_callable=mock_open)
def test_generate_diagram_ascii(mock_file, mock_list_generator, mock_parser, mock_scanner):
    """Test generating a list diagram."""
    # Setup mocks
    mock_scanner_instance = mock_scanner.return_value
    mock_scanner_instance.scan_directory.return_value = [Path('test.py')]

    mock_parser_instance = mock_parser.return_value
    mock_parser_instance.entities = {'TestEntity': Entity('TestEntity', 'class', Path('test.py'), 10)}

    mock_generator_instance = mock_list_generator.return_value
    mock_generator_instance.generate.return_value = "List Diagram"

    # Call the function
    generate_diagram('test_dir', 'TestEntity', 'ascii', 1, 'output.txt')

    # Verify the calls
    mock_scanner.assert_called_once()
    mock_scanner_instance.scan_directory.assert_called_once_with('test_dir')

    mock_parser.assert_called_once()
    mock_parser_instance.parse_files.assert_called_once_with([Path('test.py')])

    mock_list_generator.assert_called_once_with(mock_parser_instance.entities)
    mock_generator_instance.generate.assert_called_once_with('TestEntity', 1)

    mock_file.assert_called_once_with('output.txt', 'w', encoding='utf-8')
    mock_file().write.assert_called_once_with("List Diagram")


@patch('diagrams.main.FileScanner')
@patch('diagrams.main.CodeParser')
@patch('diagrams.main.MermaidDiagramGenerator')
@patch('builtins.open', new_callable=mock_open)
def test_generate_diagram_mermaid(mock_file, mock_mermaid_generator, mock_parser, mock_scanner):
    """Test generating a Mermaid diagram."""
    # Setup mocks
    mock_scanner_instance = mock_scanner.return_value
    mock_scanner_instance.scan_directory.return_value = [Path('test.py')]

    mock_parser_instance = mock_parser.return_value
    mock_parser_instance.entities = {'TestEntity': Entity('TestEntity', 'class', Path('test.py'), 10)}

    mock_generator_instance = mock_mermaid_generator.return_value
    mock_generator_instance.generate.return_value = "Mermaid Diagram"

    # Call the function
    generate_diagram('test_dir', 'TestEntity', 'mermaid', 1, 'output.txt')

    # Verify the calls
    mock_scanner.assert_called_once()
    mock_scanner_instance.scan_directory.assert_called_once_with('test_dir')

    mock_parser.assert_called_once()
    mock_parser_instance.parse_files.assert_called_once_with([Path('test.py')])

    mock_mermaid_generator.assert_called_once_with(mock_parser_instance.entities)
    mock_generator_instance.generate.assert_called_once_with('TestEntity', 1)

    mock_file.assert_called_once_with('output.txt', 'w', encoding='utf-8')
    mock_file().write.assert_called_once_with("Mermaid Diagram")


@patch('diagrams.main.generate_diagram')
@patch('sys.argv', ['diagrams', 'test_dir', '--entity', 'TestEntity'])
def test_main_default_args(mock_generate_diagram):
    """Test the main function with default arguments."""
    main()
    mock_generate_diagram.assert_called_once_with('test_dir', 'TestEntity', 'ascii', 1, None)


@patch('diagrams.main.generate_diagram')
@patch('sys.argv', ['diagrams', 'test_dir', '--entity', 'TestEntity', '--format', 'mermaid', '--depth', '2', '--output', 'output.txt'])
def test_main_custom_args(mock_generate_diagram):
    """Test the main function with custom arguments."""
    main()
    mock_generate_diagram.assert_called_once_with('test_dir', 'TestEntity', 'mermaid', 2, 'output.txt')


@patch('diagrams.main.generate_diagram', side_effect=Exception("Test error"))
@patch('sys.argv', ['diagrams', 'test_dir', '--entity', 'TestEntity'])
@patch('sys.stderr')
def test_main_error(mock_stderr, mock_generate_diagram):
    """Test the main function when an error occurs."""
    result = main()
    assert result == 1
    mock_generate_diagram.assert_called_once()
    mock_stderr.write.assert_called()
