"""
Folder Scanner Module
Recursively scans folder trees to identify folders containing processable files.
"""

import os
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

from src.config import config
from src.utils.tracker import ProcessingTracker


@dataclass
class FolderInfo:
    """Information about a folder to be processed."""
    guid: str
    path: str
    name: str
    file_count: int
    files: List[str]
    parent_path: str
    depth: int
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "guid": self.guid,
            "path": self.path,
            "name": self.name,
            "file_count": self.file_count,
            "files": self.files,
            "parent_path": self.parent_path,
            "depth": self.depth,
            "discovered_at": self.discovered_at
        }


class FolderScanner:
    """Scans folder trees to identify folders for processing."""

    def __init__(self, tracker: Optional[ProcessingTracker] = None):
        """Initialize the folder scanner."""
        self.tracker = tracker or ProcessingTracker()
        self.scanned_folders: List[FolderInfo] = []

    def scan(self, root_path: str) -> List[FolderInfo]:
        """
        Scan the folder tree starting from root_path.

        Args:
            root_path: The parent folder to start scanning from.

        Returns:
            List of FolderInfo objects for folders containing processable files.
        """
        self.scanned_folders = []
        root = Path(root_path)

        if not root.exists():
            self.tracker.log_error(f"Root path does not exist: {root_path}")
            raise FileNotFoundError(f"Root path does not exist: {root_path}")

        if not root.is_dir():
            self.tracker.log_error(f"Root path is not a directory: {root_path}")
            raise NotADirectoryError(f"Root path is not a directory: {root_path}")

        self.tracker.log_info(f"Starting scan of: {root_path}")
        self._scan_recursive(root, depth=0)
        self.tracker.log_info(f"Scan complete. Found {len(self.scanned_folders)} folders with processable files.")

        return self.scanned_folders

    def _scan_recursive(self, folder: Path, depth: int) -> None:
        """Recursively scan folders."""
        if depth > config.max_depth:
            self.tracker.log_warning(f"Max depth ({config.max_depth}) reached at: {folder}")
            return

        try:
            # Skip hidden folders if configured
            if config.skip_hidden_folders and folder.name.startswith('.'):
                return

            # Get processable files in this folder
            processable_files = self._get_processable_files(folder)

            if processable_files:
                folder_info = FolderInfo(
                    guid=str(uuid.uuid4()),
                    path=str(folder),
                    name=folder.name,
                    file_count=len(processable_files),
                    files=processable_files,
                    parent_path=str(folder.parent),
                    depth=depth
                )
                self.scanned_folders.append(folder_info)
                self.tracker.log_info(f"Found folder: {folder.name} with {len(processable_files)} files")

            # Recurse into subdirectories
            for item in folder.iterdir():
                if item.is_dir():
                    self._scan_recursive(item, depth + 1)

        except PermissionError as e:
            self.tracker.log_error(f"Permission denied accessing: {folder}", exception=e)
        except Exception as e:
            self.tracker.log_error(f"Error scanning folder: {folder}", exception=e)

    def _get_processable_files(self, folder: Path) -> List[str]:
        """Get list of processable files in a folder."""
        processable_files = []

        try:
            for item in folder.iterdir():
                if item.is_file():
                    # Skip hidden files if configured
                    if config.skip_hidden_files and item.name.startswith('.'):
                        continue

                    if config.is_supported_file(str(item)):
                        processable_files.append(item.name)

        except PermissionError:
            pass

        return processable_files

    def get_summary(self) -> Dict:
        """Get a summary of the scan results."""
        total_files = sum(f.file_count for f in self.scanned_folders)
        return {
            "total_folders": len(self.scanned_folders),
            "total_files": total_files,
            "folders": [f.to_dict() for f in self.scanned_folders]
        }

    def display_folders(self) -> str:
        """Generate a formatted display of scanned folders."""
        if not self.scanned_folders:
            return "No folders with processable files found."

        lines = ["=" * 60]
        lines.append("FOLDERS FOR PROCESSING")
        lines.append("=" * 60)

        for i, folder in enumerate(self.scanned_folders, 1):
            lines.append(f"\n{i}. {folder.name}")
            lines.append(f"   Path: {folder.path}")
            lines.append(f"   GUID: {folder.guid}")
            lines.append(f"   Files: {folder.file_count}")
            lines.append(f"   File list: {', '.join(folder.files[:5])}")
            if len(folder.files) > 5:
                lines.append(f"   ... and {len(folder.files) - 5} more")

        lines.append("\n" + "=" * 60)
        lines.append(f"Total: {len(self.scanned_folders)} folders")
        lines.append("=" * 60)

        return "\n".join(lines)
