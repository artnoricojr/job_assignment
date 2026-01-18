# File Processing Application

A Python application for recursively processing files (primarily PDFs) within folder trees. Supports both GUI and CLI interfaces.

## Features

- **Dual Interface**: Choose between graphical (GUI) or command-line (CLI) mode
- **Recursive Scanning**: Automatically traverses folder trees to find processable files
- **GUID Tracking**: Each folder is assigned a unique identifier for tracking
- **Multiple File Types**: Supports PDF, DOC, DOCX, XLS, XLSX, TXT, and CSV files
- **JSON/CSV Output**: Results exported in both formats
- **Exception Handling**: Continues processing even when individual files fail
- **Detailed Logging**: Comprehensive logging with error reports

## Project Structure

```
job_assignment/
├── main.py                    # Entry point with CLI/GUI switch
├── README.md                  # This file
├── Project_Overview.md        # Project requirements
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── folder_scanner.py  # Folder tree traversal
│   │   ├── file_processor.py  # File processing logic
│   │   └── output_handler.py  # JSON/CSV output generation
│   ├── gui/
│   │   ├── __init__.py
│   │   └── interface.py       # Tkinter GUI interface
│   ├── cli/
│   │   ├── __init__.py
│   │   └── terminal.py        # Command-line interface
│   └── utils/
│       ├── __init__.py
│       └── tracker.py         # Logging and exception tracking
└── output/                    # Generated output files (created at runtime)
```

## Installation

1. Ensure Python 3.8+ is installed
2. Clone or download this repository
3. No external dependencies required (uses standard library only)

## Usage

### GUI Mode

Launch the graphical interface:

```bash
python main.py --gui
```

**GUI Workflow:**
1. Click "Browse..." to select a parent folder
2. Click "Scan Folders" to find folders with processable files
3. Review the list of discovered folders
4. Click "Process Selected Folders" to begin processing
5. View results in the log panel
6. Export results using the "Export Results" button

### CLI Mode

Launch the command-line interface:

```bash
python main.py --cli
```

**With a specific path:**

```bash
python main.py --cli --path "C:\path\to\folder"
```

**With custom output directory:**

```bash
python main.py --cli --path "C:\path\to\folder" --output "my_results"
```

**CLI Workflow:**
1. Enter or confirm the folder path
2. Review the list of folders found
3. Confirm to proceed with processing
4. View results summary
5. Check output directory for JSON/CSV files

## Configuration

Edit `src/config.py` to customize:

```python
# Supported file extensions
supported_extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"]

# Maximum folder depth to traverse
max_depth = 10

# Skip hidden files/folders
skip_hidden_folders = True
skip_hidden_files = True

# Output settings
output_directory = "output"
json_output_filename = "processing_results.json"
csv_output_filename = "processing_results.csv"
```

## Output Files

After processing, the following files are generated in the `output/` directory:

### processing_results.json

```json
{
  "generated_at": "2024-01-15T10:30:00",
  "version": "1.0",
  "data": {
    "report_generated": "2024-01-15T10:30:00",
    "scan_summary": {
      "total_folders_found": 5,
      "total_files_found": 25
    },
    "processing_summary": {
      "total_folders_processed": 5,
      "total_files_processed": 23,
      "total_errors": 2,
      "success_rate": 92.0
    },
    "detailed_results": [...]
  }
}
```

### processing_results.csv

| folder_guid | folder_name | folder_path | filename | status | file_type | file_size |
|-------------|-------------|-------------|----------|--------|-----------|-----------|
| abc-123... | Client_A | C:\data\Client_A | doc1.pdf | completed | pdf | 1024 |

### processing.log

Detailed log of all operations, errors, and warnings.

## Error Handling

The application is designed to continue processing even when errors occur:

- Individual file errors are logged but don't stop processing
- Folder access errors are recorded and skipped
- A complete error report is available after processing
- All exceptions are tracked with timestamps and context

## Module Descriptions

### folder_scanner.py
- Recursively scans folder trees
- Identifies folders containing supported file types
- Assigns GUIDs to each folder
- Respects depth limits and hidden file settings

### file_processor.py
- Processes files within identified folders
- Extracts basic metadata (size, dates)
- Tracks processing status per file
- Handles exceptions gracefully

### output_handler.py
- Generates JSON output with full details
- Converts results to CSV format
- Combines scan and processing summaries

### tracker.py
- Centralized logging system
- Tracks errors and warnings separately
- Generates error reports
- Supports both file and console output

## Command-Line Help

```bash
python main.py --help
```

```
usage: main.py [-h] (--gui | --cli) [--path PATH] [--output OUTPUT]

File Processing Application - Process files in folder trees

optional arguments:
  -h, --help       show this help message and exit
  --gui            Launch graphical user interface
  --cli            Launch command line interface
  --path PATH      Parent folder path to process (CLI mode only)
  --output OUTPUT  Output directory for results (default: output)

Examples:
  python main.py --gui                    Launch GUI mode
  python main.py --cli                    Launch CLI mode
  python main.py --cli --path "C:\folder" Process specific folder in CLI mode
```

## Requirements

- Python 3.8 or higher
- tkinter (included with standard Python installation)
- No additional packages required

## Sample Testing

A sample folder tree is configured at: `C:\_sample\tree_test`

You can modify this in `src/config.py`:

```python
sample_path: str = r"C:\_sample\tree_test"
```
