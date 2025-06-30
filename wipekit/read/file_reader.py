"""
Universal Data Reader Module
===========================

Provides a robust, enterprise-level interface for reading Parquet, Avro, ORC, CSV, TSV, and JSON files
using pandas. Includes unified API, comprehensive error handling, logging, and extensibility.

Dependencies:
-------------
- pandas
- pyarrow (for Parquet, ORC, Avro)
- fastavro (for Avro, optional)

Example:
--------
from wipekit.read.universal_reader import UniversalDataReader
reader = UniversalDataReader()
df = reader.read('data.parquet')
"""

import os
from typing import Optional
from ..exceptions import ValidationError
from ..logging import getLogger, configure_logger

configure_logger()
logger = getLogger("wipekit.read.file_reader")

try:
    import pandas as pd
except ImportError:
    raise ImportError(
        "pandas is required for reading data files. "
        "Install it with: pip install pandas"
    )

class FileManager(object):
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
                Supported kwargs by file type:
                - CSV/TSV: sep, delimiter, header, names, index_col, usecols, dtype, engine, encoding, nrows, skiprows, na_values, parse_dates, etc.
                - JSON: orient, typ, dtype, convert_axes, convert_dates, keep_default_dates, numpy, precise_float, date_unit, encoding, lines, chunksize, compression, etc.
                - Parquet: engine, columns, use_nullable_dtypes, filesystem, filters, etc.
                - ORC: columns, use_nullable_dtypes, filesystem, etc.
                - Avro: columns (if supported by backend), use_nullable_dtypes, etc. (requires pyarrow)
        Returns:
            pd.DataFrame or None
        Raises:
            ValueError: If the file format is unsupported or reading fails
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

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
                    raise 
                except Exception as e:
                    logger.error(f"Failed to read Avro file: {e}")
                    raise
            else:
                raise ValueError(f"Unsupported file extension: {ext}")
        except ValidationError as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise
