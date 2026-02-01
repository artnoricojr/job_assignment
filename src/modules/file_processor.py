"""
File Processor Module
Processes files within identified folders (primarily PDFs).
"""

import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.config import config
from src.utils.tracker import ProcessingTracker


class ProcessingStatus(Enum):
    """Status of file processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class FileResult:
    """Result of processing a single file."""
    file_guid: str
    filename: str
    filepath: str
    folder_guid: str
    status: ProcessingStatus
    file_type: str
    file_size: int
    processed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_guid": self.file_guid,
            "filename": self.filename,
            "filepath": self.filepath,
            "folder_guid": self.folder_guid,
            "status": self.status.value,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "processed_at": self.processed_at,
            "error_message": self.error_message,
            "metadata": self.metadata
        }


@dataclass
class FolderResult:
    """Result of processing all files in a folder."""
    folder_guid: str
    folder_path: str
    folder_name: str
    total_files: int
    processed_files: int
    error_files: int
    skipped_files: int
    file_results: List[FileResult]
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "folder_guid": self.folder_guid,
            "folder_path": self.folder_path,
            "folder_name": self.folder_name,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "error_files": self.error_files,
            "skipped_files": self.skipped_files,
            "file_results": [f.to_dict() for f in self.file_results],
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


class FileProcessor:
    """Processes files within folders."""

    def __init__(self, tracker: Optional[ProcessingTracker] = None):
        """Initialize the file processor."""
        self.tracker = tracker or ProcessingTracker()
        self.results: List[FolderResult] = []

    def process_folders(self, folders: List[Any]) -> List[FolderResult]:
        """
        Process all files in the given folders.

        Args:
            folders: List of FolderInfo objects from the scanner.

        Returns:
            List of FolderResult objects with processing results.
        """
        self.results = []

        for folder in folders:
            try:
                result = self.process_folder(folder)
                self.results.append(result)
            except Exception as e:
                self.tracker.log_error(f"Failed to process folder: {folder.path}", exception=e)

        return self.results

    def process_folder(self, folder: Any) -> FolderResult:
        """
        Process all files in a single folder.

        Args:
            folder: FolderInfo object from the scanner.

        Returns:
            FolderResult with processing results.
        """
        self.tracker.log_info(f"Processing folder: {folder.name} ({folder.guid})")

        file_results = []
        processed_count = 0
        error_count = 0
        skipped_count = 0

        for filename in folder.files:
            filepath = os.path.join(folder.path, filename)

            try:
                result = self._process_file(filepath, folder.guid)
                file_results.append(result)

                if result.status == ProcessingStatus.COMPLETED:
                    processed_count += 1
                elif result.status == ProcessingStatus.ERROR:
                    error_count += 1
                elif result.status == ProcessingStatus.SKIPPED:
                    skipped_count += 1

            except Exception as e:
                self.tracker.log_error(f"Exception processing file: {filename}", exception=e)
                error_count += 1
                file_results.append(FileResult(
                    file_guid=str(uuid.uuid4()),
                    filename=filename,
                    filepath=filepath,
                    folder_guid=folder.guid,
                    status=ProcessingStatus.ERROR,
                    file_type=self._get_file_type(filepath),
                    file_size=0,
                    error_message=str(e)
                ))

        folder_result = FolderResult(
            folder_guid=folder.guid,
            folder_path=folder.path,
            folder_name=folder.name,
            total_files=len(folder.files),
            processed_files=processed_count,
            error_files=error_count,
            skipped_files=skipped_count,
            file_results=file_results,
            completed_at=datetime.now().isoformat()
        )

        self.tracker.log_info(
            f"Folder complete: {processed_count} processed, "
            f"{error_count} errors, {skipped_count} skipped"
        )

        return folder_result

    def _process_file(self, filepath: str, folder_guid: str) -> FileResult:
        """
        Process a single file.

        Args:
            filepath: Full path to the file.
            folder_guid: GUID of the parent folder.

        Returns:
            FileResult with processing outcome.
        """
        filename = os.path.basename(filepath)
        file_type = self._get_file_type(filepath)

        try:
            file_size = os.path.getsize(filepath)
        except OSError:
            file_size = 0

        self.tracker.log_info(f"Processing file: {filename}")

        try:
            # Extract metadata based on file type
            metadata = self._extract_metadata(filepath, file_type)

            return FileResult(
                file_guid=str(uuid.uuid4()),
                filename=filename,
                filepath=filepath,
                folder_guid=folder_guid,
                status=ProcessingStatus.COMPLETED,
                file_type=file_type,
                file_size=file_size,
                metadata=metadata
            )

        except Exception as e:
            self.tracker.log_error(f"Error processing {filename}: {str(e)}", exception=e)
            return FileResult(
                file_guid=str(uuid.uuid4()),
                filename=filename,
                filepath=filepath,
                folder_guid=folder_guid,
                status=ProcessingStatus.ERROR,
                file_type=file_type,
                file_size=file_size,
                error_message=str(e)
            )

    def _get_file_type(self, filepath: str) -> str:
        """Get the file type/extension."""
        return os.path.splitext(filepath)[1].lower().lstrip('.')

    def _extract_metadata(self, filepath: str, file_type: str) -> Dict[str, Any]:
        """
        Extract metadata from a file.

        Args:
            filepath: Path to the file.
            file_type: File extension/type.

        Returns:
            Dictionary of extracted metadata.
        """
        metadata = {
            "extracted_at": datetime.now().isoformat()
        }

        try:
            stat = os.stat(filepath)
            metadata["created"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
            metadata["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            metadata["accessed"] = datetime.fromtimestamp(stat.st_atime).isoformat()
        except OSError:
            pass

        # PDF-specific metadata extraction placeholder
        if file_type == "pdf":
            metadata["page_count"] = None  # Would require PyPDF2 or similar
            metadata["pdf_version"] = None

        return metadata

    def get_summary(self) -> Dict:
        """Get a summary of all processing results."""
        total_folders = len(self.results)
        total_files = sum(r.total_files for r in self.results)
        total_processed = sum(r.processed_files for r in self.results)
        total_errors = sum(r.error_files for r in self.results)
        total_skipped = sum(r.skipped_files for r in self.results)

        return {
            "total_folders": total_folders,
            "total_files": total_files,
            "total_processed": total_processed,
            "total_errors": total_errors,
            "total_skipped": total_skipped,
            "success_rate": (total_processed / total_files * 100) if total_files > 0 else 0,
            "folder_results": [r.to_dict() for r in self.results]
        }
