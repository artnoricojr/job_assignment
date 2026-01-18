#!/usr/bin/env python3
"""
File Processing Application
Main entry point with CLI/GUI mode selection.
"""

import argparse
import sys
from src.cli.terminal import run_cli
from src.gui.interface import run_gui


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="File Processing Application - Process files in folder trees",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --gui                    Launch GUI mode
  python main.py --cli                    Launch CLI mode
  python main.py --cli --path "C:\\folder" Process specific folder in CLI mode
        """
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--gui",
        action="store_true",
        help="Launch graphical user interface"
    )
    mode_group.add_argument(
        "--cli",
        action="store_true",
        help="Launch command line interface"
    )

    parser.add_argument(
        "--path",
        type=str,
        help="Parent folder path to process (CLI mode only)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output directory for results (default: output)"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    if args.gui:
        print("Launching GUI mode...")
        run_gui()
    elif args.cli:
        print("Launching CLI mode...")
        run_cli(initial_path=args.path, output_dir=args.output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
