"""Scanner module for diagrams.

This module provides functionality to scan directories for Python files.
"""

import os
from pathlib import Path
from typing import List, Set


class FileScanner:
    """
    A class to scan directories for Python files.

    This class provides methods to recursively scan directories and find all Python files.
    It can exclude specified directories and files.
    """

    def __init__(self, exclude_dirs: Set[str] = None, exclude_files: Set[str] = None):
        """
        Initialize the FileScanner.

        Args:
            exclude_dirs: A set of directory names to exclude from scanning.
            exclude_files: A set of file names to exclude from scanning.
        """
        self.exclude_dirs = exclude_dirs or {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}
        self.exclude_files = exclude_files or set()

    def scan_directory(self, directory: str) -> List[Path]:
        """
        Recursively scan a directory for Python files.

        Args:
            directory: The directory to scan.

        Returns:
            A list of Path objects representing the Python files found.
        """
        python_files = []

        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if file.endswith('.py') and file not in self.exclude_files:
                    python_files.append(Path(os.path.join(root, file)))

        return python_files
