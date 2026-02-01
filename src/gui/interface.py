"""
GUI Interface Module
Provides a graphical user interface using tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from typing import Optional

from src.config import config
from src.modules.folder_scanner import FolderScanner
from src.modules.file_processor import FileProcessor
from src.modules.output_handler import OutputHandler
from src.utils.tracker import ProcessingTracker


class FileProcessorGUI:
    """Main GUI application for file processing."""

    def __init__(self, root: tk.Tk):
        """Initialize the GUI."""
        self.root = root
        self.root.title("File Processing Application")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # Processing components
        self.tracker = ProcessingTracker(log_to_file=True, log_to_console=False)
        self.scanner: Optional[FolderScanner] = None
        self.processor: Optional[FileProcessor] = None
        self.output_handler: Optional[OutputHandler] = None

        # State
        self.selected_path: Optional[str] = None
        self.scanned_folders = []
        self.is_processing = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="File Processing Application",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        # Folder selection section
        self._setup_folder_section(main_frame)

        # Folders list section
        self._setup_folders_list(main_frame)

        # Action buttons
        self._setup_action_buttons(main_frame)

        # Log output section
        self._setup_log_section(main_frame)

        # Status bar
        self._setup_status_bar(main_frame)

    def _setup_folder_section(self, parent: ttk.Frame) -> None:
        """Setup folder selection section."""
        folder_frame = ttk.LabelFrame(parent, text="Select Parent Folder", padding="5")
        folder_frame.grid(row=1, column=0, sticky="ew", pady=5)
        folder_frame.columnconfigure(1, weight=1)

        ttk.Label(folder_frame, text="Path:").grid(row=0, column=0, padx=5)

        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(folder_frame, textvariable=self.path_var)
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=5)

        browse_btn = ttk.Button(folder_frame, text="Browse...", command=self._browse_folder)
        browse_btn.grid(row=0, column=2, padx=5)

        scan_btn = ttk.Button(folder_frame, text="Scan Folders", command=self._scan_folders)
        scan_btn.grid(row=0, column=3, padx=5)

    def _setup_folders_list(self, parent: ttk.Frame) -> None:
        """Setup the folders list view."""
        list_frame = ttk.LabelFrame(parent, text="Folders for Processing", padding="5")
        list_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        # Treeview for folders
        columns = ("name", "files", "path", "guid")
        self.folders_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)

        self.folders_tree.heading("name", text="Folder Name")
        self.folders_tree.heading("files", text="Files")
        self.folders_tree.heading("path", text="Path")
        self.folders_tree.heading("guid", text="GUID")

        self.folders_tree.column("name", width=150)
        self.folders_tree.column("files", width=50)
        self.folders_tree.column("path", width=300)
        self.folders_tree.column("guid", width=250)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.folders_tree.yview)
        self.folders_tree.configure(yscrollcommand=scrollbar.set)

        self.folders_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _setup_action_buttons(self, parent: ttk.Frame) -> None:
        """Setup action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, pady=10)

        self.process_btn = ttk.Button(
            button_frame,
            text="Process Selected Folders",
            command=self._confirm_and_process,
            state="disabled"
        )
        self.process_btn.grid(row=0, column=0, padx=5)

        self.clear_btn = ttk.Button(
            button_frame,
            text="Clear",
            command=self._clear_all
        )
        self.clear_btn.grid(row=0, column=1, padx=5)

        self.export_btn = ttk.Button(
            button_frame,
            text="Export Results",
            command=self._export_results,
            state="disabled"
        )
        self.export_btn.grid(row=0, column=2, padx=5)

    def _setup_log_section(self, parent: ttk.Frame) -> None:
        """Setup log output section."""
        log_frame = ttk.LabelFrame(parent, text="Processing Log", padding="5")
        log_frame.grid(row=4, column=0, sticky="nsew", pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(4, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")

    def _setup_status_bar(self, parent: ttk.Frame) -> None:
        """Setup status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief="sunken")
        status_bar.grid(row=5, column=0, sticky="ew", pady=(5, 0))

    def _browse_folder(self) -> None:
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(
            title="Select Parent Folder for Processing",
            initialdir=config.sample_path if config.sample_path else "/"
        )
        if folder:
            self.path_var.set(folder)
            self.selected_path = folder

    def _scan_folders(self) -> None:
        """Scan the selected folder for processable files."""
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("Warning", "Please select a folder first.")
            return

        self._log("Starting folder scan...")
        self.status_var.set("Scanning...")

        # Clear previous results
        for item in self.folders_tree.get_children():
            self.folders_tree.delete(item)

        try:
            self.scanner = FolderScanner(self.tracker)
            self.scanned_folders = self.scanner.scan(path)

            # Populate tree view
            for folder in self.scanned_folders:
                self.folders_tree.insert("", "end", values=(
                    folder.name,
                    folder.file_count,
                    folder.path,
                    folder.guid
                ))

            self._log(f"Scan complete. Found {len(self.scanned_folders)} folders.")
            self.status_var.set(f"Found {len(self.scanned_folders)} folders with processable files")

            if self.scanned_folders:
                self.process_btn.config(state="normal")
            else:
                messagebox.showinfo("Info", "No folders with processable files found.")

        except Exception as e:
            self._log(f"Scan error: {str(e)}")
            messagebox.showerror("Error", f"Scan failed: {str(e)}")
            self.status_var.set("Scan failed")

    def _confirm_and_process(self) -> None:
        """Confirm with user and start processing."""
        if not self.scanned_folders:
            return

        count = len(self.scanned_folders)
        total_files = sum(f.file_count for f in self.scanned_folders)

        result = messagebox.askyesno(
            "Confirm Processing",
            f"Process {count} folders containing {total_files} files?\n\n"
            "This will extract metadata from all supported files."
        )

        if result:
            self._start_processing()

    def _start_processing(self) -> None:
        """Start file processing in background thread."""
        self.is_processing = True
        self.process_btn.config(state="disabled")
        self.status_var.set("Processing...")

        # Run in background thread
        thread = threading.Thread(target=self._process_files)
        thread.daemon = True
        thread.start()

    def _process_files(self) -> None:
        """Process files (runs in background thread)."""
        try:
            self.processor = FileProcessor(self.tracker)
            self.output_handler = OutputHandler(tracker=self.tracker)

            self._log("Starting file processing...")

            results = self.processor.process_folders(self.scanned_folders)
            summary = self.processor.get_summary()

            # Generate report
            scan_summary = self.scanner.get_summary()
            self.output_handler.generate_report(scan_summary, summary)

            self._log(f"Processing complete: {summary['total_processed']} files processed, "
                     f"{summary['total_errors']} errors")

            # Update UI from main thread
            self.root.after(0, self._processing_complete, summary)

        except Exception as e:
            self._log(f"Processing error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Processing failed: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Processing failed"))

        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.process_btn.config(state="normal"))

    def _processing_complete(self, summary: dict) -> None:
        """Called when processing is complete."""
        self.status_var.set(
            f"Complete: {summary['total_processed']} processed, "
            f"{summary['total_errors']} errors"
        )
        self.export_btn.config(state="normal")

        messagebox.showinfo(
            "Processing Complete",
            f"Processed {summary['total_processed']} files.\n"
            f"Errors: {summary['total_errors']}\n"
            f"Results saved to: {config.output_directory}"
        )

    def _export_results(self) -> None:
        """Export results to additional formats."""
        if not self.processor:
            return

        try:
            filepath = filedialog.asksaveasfilename(
                title="Export Results",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
            )
            if filepath:
                summary = self.processor.get_summary()
                # Create output handler for user's chosen directory
                from pathlib import Path
                export_path = Path(filepath)
                export_handler = OutputHandler(
                    output_dir=str(export_path.parent),
                    tracker=self.tracker
                )
                if filepath.endswith('.csv'):
                    export_handler.save_csv(summary, export_path.name)
                else:
                    export_handler.save_json(summary, export_path.name)
                self._log(f"Exported to: {filepath}")
                messagebox.showinfo("Export", f"Results exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _clear_all(self) -> None:
        """Clear all data and reset UI."""
        self.path_var.set("")
        self.selected_path = None
        self.scanned_folders = []

        for item in self.folders_tree.get_children():
            self.folders_tree.delete(item)

        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

        self.process_btn.config(state="disabled")
        self.export_btn.config(state="disabled")
        self.status_var.set("Ready")

        self.tracker.clear()

    def _log(self, message: str) -> None:
        """Add message to log display."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")


def run_gui() -> None:
    """Launch the GUI application."""
    root = tk.Tk()
    app = FileProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
