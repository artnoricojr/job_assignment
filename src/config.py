"""
Configuration settings for the File Processing Application.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """Application configuration settings."""

    # Supported file extensions for processing
    supported_extensions: List[str] = field(default_factory=lambda: [
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"
    ])

    # Primary file type to process
    primary_extension: str = ".pdf"

    # Output settings
    output_directory: str = "output"
    json_output_filename: str = "processing_results.json"
    csv_output_filename: str = "processing_results.csv"
    log_filename: str = "processing.log"

    # Processing settings
    max_depth: int = 10  # Maximum folder depth to traverse
    skip_hidden_folders: bool = True
    skip_hidden_files: bool = True

    # Sample path for testing
    sample_path: str = r"C:\_sample\tree_test"

    def get_output_path(self, filename: str) -> Path:
        """Get full path for an output file."""
        output_dir = Path(self.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / filename

    def is_supported_file(self, filepath: str) -> bool:
        """Check if a file has a supported extension."""
        ext = os.path.splitext(filepath)[1].lower()
        return ext in self.supported_extensions

    def is_primary_file(self, filepath: str) -> bool:
        """Check if a file is the primary type (PDF)."""
        ext = os.path.splitext(filepath)[1].lower()
        return ext == self.primary_extension


# Global configuration instance
config = Config()
