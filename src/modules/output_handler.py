"""
Output Handler Module
Handles JSON and CSV output generation.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.config import config
from src.utils.tracker import ProcessingTracker


class OutputHandler:
    """Handles output generation in various formats."""

    def __init__(self, output_dir: str = None, tracker: Optional[ProcessingTracker] = None):
        """Initialize the output handler."""
        self.output_dir = Path(output_dir or config.output_directory)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tracker = tracker or ProcessingTracker()

    def save_json(self, data: Dict, filename: str = None) -> str:
        """
        Save data to a JSON file.

        Args:
            data: Dictionary to save.
            filename: Optional custom filename.

        Returns:
            Path to the saved file.
        """
        filename = filename or config.json_output_filename
        filepath = self.output_dir / filename

        try:
            output_data = {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0",
                "data": data
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            self.tracker.log_info(f"JSON saved to: {filepath}")
            return str(filepath)

        except Exception as e:
            self.tracker.log_error(f"Failed to save JSON: {filepath}", exception=e)
            raise

    def save_csv(self, data: Dict, filename: str = None) -> str:
        """
        Convert and save data to a CSV file.

        Args:
            data: Dictionary containing folder_results with file_results.
            filename: Optional custom filename.

        Returns:
            Path to the saved file.
        """
        filename = filename or config.csv_output_filename
        filepath = self.output_dir / filename

        try:
            rows = self._flatten_results(data)

            if not rows:
                self.tracker.log_warning("No data to write to CSV")
                return str(filepath)

            # Get all unique keys for headers
            headers = list(rows[0].keys()) if rows else []

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)

            self.tracker.log_info(f"CSV saved to: {filepath}")
            return str(filepath)

        except Exception as e:
            self.tracker.log_error(f"Failed to save CSV: {filepath}", exception=e)
            raise

    def _flatten_results(self, data: Dict) -> List[Dict]:
        """
        Flatten nested results into rows for CSV.

        Args:
            data: Nested dictionary with folder and file results.

        Returns:
            List of flattened dictionaries for CSV rows.
        """
        rows = []

        folder_results = data.get("folder_results", [])

        for folder in folder_results:
            folder_info = {
                "folder_guid": folder.get("folder_guid", ""),
                "folder_name": folder.get("folder_name", ""),
                "folder_path": folder.get("folder_path", ""),
            }

            file_results = folder.get("file_results", [])

            if not file_results:
                # Add folder entry even if no files
                rows.append({
                    **folder_info,
                    "filename": "",
                    "filepath": "",
                    "status": "",
                    "file_type": "",
                    "file_size": "",
                    "processed_at": "",
                    "error_message": ""
                })
            else:
                for file_result in file_results:
                    rows.append({
                        **folder_info,
                        "filename": file_result.get("filename", ""),
                        "filepath": file_result.get("filepath", ""),
                        "status": file_result.get("status", ""),
                        "file_type": file_result.get("file_type", ""),
                        "file_size": file_result.get("file_size", ""),
                        "processed_at": file_result.get("processed_at", ""),
                        "error_message": file_result.get("error_message", "")
                    })

        return rows

    def generate_report(self, scan_summary: Dict, processing_summary: Dict) -> str:
        """
        Generate a combined report with scan and processing results.

        Args:
            scan_summary: Summary from folder scanner.
            processing_summary: Summary from file processor.

        Returns:
            Path to the report file.
        """
        report = {
            "report_generated": datetime.now().isoformat(),
            "scan_summary": {
                "total_folders_found": scan_summary.get("total_folders", 0),
                "total_files_found": scan_summary.get("total_files", 0),
            },
            "processing_summary": {
                "total_folders_processed": processing_summary.get("total_folders", 0),
                "total_files_processed": processing_summary.get("total_processed", 0),
                "total_errors": processing_summary.get("total_errors", 0),
                "total_skipped": processing_summary.get("total_skipped", 0),
                "success_rate": processing_summary.get("success_rate", 0),
            },
            "detailed_results": processing_summary.get("folder_results", [])
        }

        # Save both formats
        json_path = self.save_json(report)
        csv_path = self.save_csv(processing_summary)

        self.tracker.log_info(f"Report generated: JSON={json_path}, CSV={csv_path}")

        return json_path

    def load_json(self, filename: str = None) -> Dict:
        """
        Load data from a JSON file.

        Args:
            filename: Optional custom filename.

        Returns:
            Loaded dictionary data.
        """
        filename = filename or config.json_output_filename
        filepath = self.output_dir / filename

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.tracker.log_error(f"Failed to load JSON: {filepath}", exception=e)
            raise
