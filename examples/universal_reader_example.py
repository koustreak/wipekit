"""
Universal Data Reader Example
============================

This script demonstrates how to read Parquet, Avro, ORC, CSV, TSV, and JSON files
using pandas in a robust, enterprise-ready manner. It includes:
- Unified interface for multiple formats
- Comprehensive error handling and logging
- Extensible design for future formats
- Type hints and docstrings for maintainability

Dependencies:
-------------
- pandas
- pyarrow (for Parquet, ORC, Avro)
- fastavro (for Avro, optional)

Usage:
------
python universal_reader_example.py <file_path>
"""

import os
import sys
import logging
from typing import Optional
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger("UniversalDataReader")

class UniversalDataReader:
    """
    Enterprise-level universal data reader for multiple file formats.
    """
    def __init__(self):
        pass

    def read(self, file_path: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        Read a file into a pandas DataFrame based on its extension.
        Args:
            file_path (str): Path to the data file
            **kwargs: Additional arguments for pandas read functions
        Returns:
            pd.DataFrame or None
        Raises:
            ValueError: If the file format is unsupported or reading fails
        """
        if not os.path.isfile(file_path):
            logger.error(f"File not found: {file_path}")
            return None

        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.csv':
                logger.info(f"Reading CSV file: {file_path}")
                return pd.read_csv(file_path, **kwargs)
            elif ext == '.tsv':
                logger.info(f"Reading TSV file: {file_path}")
                return pd.read_csv(file_path, sep='\t', **kwargs)
            elif ext == '.json':
                logger.info(f"Reading JSON file: {file_path}")
                return pd.read_json(file_path, **kwargs)
            elif ext == '.parquet':
                logger.info(f"Reading Parquet file: {file_path}")
                return pd.read_parquet(file_path, **kwargs)
            elif ext == '.orc':
                logger.info(f"Reading ORC file: {file_path}")
                return pd.read_orc(file_path, **kwargs)
            elif ext == '.avro':
                logger.info(f"Reading Avro file: {file_path}")
                try:
                    import pyarrow as pa
                    import pyarrow.avro as pavro
                    with pa.memory_map(file_path, 'r') as source:
                        table = pavro.read_table(source)
                        return table.to_pandas()
                except ImportError:
                    logger.error("pyarrow is required for Avro support. Install with: pip install pyarrow")
                    return None
                except Exception as e:
                    logger.error(f"Failed to read Avro file: {e}")
                    return None
            else:
                logger.error(f"Unsupported file extension: {ext}")
                return None
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Universal Data Reader Example")
    parser.add_argument('file', type=str, help='Path to the data file (csv, tsv, json, parquet, orc, avro)')
    args = parser.parse_args()

    reader = UniversalDataReader()
    df = reader.read(args.file)
    if df is not None:
        logger.info(f"Successfully read file: {args.file}")
        print(df.head())
    else:
        logger.error(f"Failed to read file: {args.file}")

if __name__ == '__main__':
    main()
