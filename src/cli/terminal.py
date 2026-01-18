"""
CLI Terminal Module
Provides a command-line interface for file processing.
"""

import os
import sys
from typing import Optional

from src.config import config
from src.modules.folder_scanner import FolderScanner
from src.modules.file_processor import FileProcessor
from src.modules.output_handler import OutputHandler
from src.utils.tracker import ProcessingTracker


class TerminalInterface:
    """Command-line interface for file processing."""

    def __init__(self, output_dir: str = None):
        """Initialize the CLI."""
        self.tracker = ProcessingTracker(log_to_file=True, log_to_console=True)
        self.scanner = FolderScanner(self.tracker)
        self.processor = FileProcessor(self.tracker)
        self.output_handler = OutputHandler(output_dir=output_dir, tracker=self.tracker)

    def run(self, initial_path: Optional[str] = None) -> int:
        """
        Run the CLI workflow.

        Args:
            initial_path: Optional path to process immediately.

        Returns:
            Exit code (0 for success, 1 for error).
        """
        self._print_header()

        try:
            # Get folder path
            if initial_path:
                folder_path = initial_path
            else:
                folder_path = self._prompt_for_path()

            if not folder_path:
                print("No path provided. Exiting.")
                return 1

            # Scan folders
            print(f"\nScanning: {folder_path}")
            print("-" * 60)

            folders = self.scanner.scan(folder_path)

            if not folders:
                print("No folders with processable files found.")
                return 0

            # Display found folders
            print(self.scanner.display_folders())

            # Confirm processing
            if not self._confirm_processing(len(folders)):
                print("Processing cancelled.")
                return 0

            # Process files
            print("\nProcessing files...")
            print("-" * 60)

            results = self.processor.process_folders(folders)
            summary = self.processor.get_summary()

            # Generate output
            scan_summary = self.scanner.get_summary()
            report_path = self.output_handler.generate_report(scan_summary, summary)

            # Display results
            self._display_results(summary, report_path)

            # Display any errors
            if self.tracker.get_error_count() > 0:
                print("\n" + self.tracker.get_errors_report())

            return 0

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            return 1
        except Exception as e:
            print(f"\nFatal error: {str(e)}")
            self.tracker.log_critical("Fatal error", exception=e)
            return 1

    def _print_header(self) -> None:
        """Print application header."""
        print("=" * 60)
        print("FILE PROCESSING APPLICATION")
        print("=" * 60)
        print(f"Supported file types: {', '.join(config.supported_extensions)}")
        print(f"Output directory: {config.output_directory}")
        print("=" * 60)

    def _prompt_for_path(self) -> Optional[str]:
        """Prompt user for folder path."""
        print(f"\nSample path: {config.sample_path}")
        print("\nEnter the parent folder path to process")
        print("(or press Enter to use sample path, 'q' to quit):")

        user_input = input("> ").strip()

        if user_input.lower() == 'q':
            return None
        elif not user_input:
            return config.sample_path
        else:
            return user_input

    def _confirm_processing(self, folder_count: int) -> bool:
        """Ask user to confirm processing."""
        print(f"\nReady to process {folder_count} folder(s).")
        print("Continue? (y/n):")

        response = input("> ").strip().lower()
        return response in ('y', 'yes')

    def _display_results(self, summary: dict, report_path: str) -> None:
        """Display processing results."""
        print("\n" + "=" * 60)
        print("PROCESSING RESULTS")
        print("=" * 60)
        print(f"Total folders processed: {summary['total_folders']}")
        print(f"Total files processed:   {summary['total_processed']}")
        print(f"Total errors:            {summary['total_errors']}")
        print(f"Total skipped:           {summary['total_skipped']}")
        print(f"Success rate:            {summary['success_rate']:.1f}%")
        print("-" * 60)
        print(f"Results saved to: {report_path}")
        print("=" * 60)


def run_cli(initial_path: Optional[str] = None, output_dir: str = None) -> int:
    """
    Entry point for CLI mode.

    Args:
        initial_path: Optional folder path to process.
        output_dir: Optional output directory.

    Returns:
        Exit code.
    """
    cli = TerminalInterface(output_dir=output_dir)
    return cli.run(initial_path)


if __name__ == "__main__":
    sys.exit(run_cli())
