"""
Example: Universal File Reader Usage
====================================

This example demonstrates how to use the FileManager class from wipekit.read.file_reader
for reading various data formats (CSV, TSV, JSON, Parquet, ORC, Avro) in a robust, enterprise-ready way.

Usage:
------
python universal_file_reader_example.py <file_path> [--head N] [--option KEY=VALUE ...]

Options:
  --head N         Number of rows to display (default: 5)
  --option KEY=VALUE  Pass additional pandas read_* kwargs (e.g., --option encoding=utf-8)
"""

import sys
import argparse
from wipekit.read.file_reader import FileManager

def parse_options(option_list):
    opts = {}
    for opt in option_list or []:
        if '=' in opt:
            k, v = opt.split('=', 1)
            opts[k] = v
    return opts

def main():
    parser = argparse.ArgumentParser(description="Universal File Reader Example")
    parser.add_argument('file', type=str, help='Path to the data file (csv, tsv, json, parquet, orc, avro)')
    parser.add_argument('--head', type=int, default=5, help='Number of rows to display')
    parser.add_argument('--option', action='append', help='Additional pandas read_* kwargs as KEY=VALUE')
    args = parser.parse_args()

    options = parse_options(args.option)
    reader = FileManager()
    df = reader.read(args.file, **options)
    if df is not None:
        print(f"Successfully read file: {args.file}")
        print(df.head(args.head))
    else:
        print(f"Failed to read file: {args.file}", file=sys.stderr)

if __name__ == '__main__':
    main()
