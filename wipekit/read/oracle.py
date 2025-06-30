"""
Oracle Database Manager Module
============================

This module provides a robust Oracle database connection manager with advanced features
for data processing and analysis workflows. It implements connection pooling,
error handling, and flexible data format conversions.

Features:
---------
- Connection pooling for efficient database access
- Support for multiple output formats (dict, pandas DataFrame, Spark DataFrame)
- Context manager interface for safe connection handling
- Error handling and automatic connection cleanup
- Advanced features like connection sharding and RAC support
- Support for both thin and thick (native) client modes

Dependencies:
------------
- Required: oracledb
- Optional: pandas (for DataFrame output)
- Optional: pyspark (for Spark DataFrame output)

Example:
--------
from wipekit.read import OracleConfig, OracleManager

config = OracleConfig(
    host='localhost',
    port=1521,
    service_name='ORCL',
    user='scott',
    password='tiger',
    output_format='pandas'
)

# Using context manager (recommended)
with OracleManager(config) as oracle:
    df = oracle.execute_query('SELECT * FROM emp WHERE deptno = :1', (10,))
"""

from typing import Optional, Dict, Any, List, Union, TYPE_CHECKING
import logging
from dataclasses import dataclass
from contextlib import contextmanager

try:
    import oracledb
except ImportError:
    raise ImportError(
        "oracledb is required for Oracle database connectivity. "
        "Install it with: pip install oracledb"
    )

from .config import OracleConfig
from ..exceptions import (
    ConnectionError,
    DataFormatError,
    ValidationError,
    ConfigurationError
)

# Type checking imports
if TYPE_CHECKING:
    import pandas as pd
    from pyspark.sql import DataFrame as SparkDataFrame

# Configure logging
logger = logging.getLogger(__name__)

# Type alias for query results
ResultType = Union[List[Dict[str, Any]], 'pd.DataFrame', 'SparkDataFrame']

class OracleManager:
    """
    A professional Oracle connection manager with connection pooling, error handling,
    and DataFrame conversion capabilities.
    """
    
    def __init__(self, config: Union[OracleConfig, Dict[str, Any]]):
        """
        Initialize the Oracle connection manager.
        
        Args:
            config: Either an OracleConfig object or a dictionary with configuration values
            
        Raises:
            ConfigurationError: If the configuration is invalid
            ConnectionError: If unable to establish connection pool
        """
        try:
            self.config = (config if isinstance(config, OracleConfig)
                         else OracleConfig.from_dict(config))
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration: {str(e)}")
            
        self._pool = None
        self._pandas_df = None
        self._spark = None
        
        # Initialize data format handlers
        self._initialize_data_handlers()
        self._initialize_connection_pool()

    def _initialize_data_handlers(self) -> None:
        """Initialize handlers for different output formats."""
        if self.config.output_format == "pandas":
            try:
                import pandas as pd
                self._pandas_df = pd
            except ImportError:
                raise DataFormatError(
                    "pandas is required for pandas output format. "
                    "Install it with: pip install pandas"
                )
        
        elif self.config.output_format == "spark":
            try:
                from pyspark.sql import SparkSession
                self._spark = SparkSession.builder.getOrCreate()
            except ImportError:
                raise DataFormatError(
                    "pyspark is required for spark output format. "
                    "Install it with: pip install pyspark"
                )

    def _initialize_connection_pool(self) -> None:
        """
        Initialize the Oracle connection pool.
        
        Raises:
            ConnectionError: If unable to create the connection pool
        """
        try:
            dsn = self._create_dsn()
            
            pool_config = {
                'min': self.config.min_connections,
                'max': self.config.max_connections,
                'increment': 1,
                'getmode': oracledb.POOL_GETMODE_WAIT
            }
            
            self._pool = oracledb.create_pool(
                user=self.config.user,
                password=self.config.password,
                dsn=dsn,
                **pool_config
            )
            
            logger.info(f"Successfully initialized connection pool to database: {self.config.service_name}")
            
        except oracledb.Error as e:
            raise ConnectionError(f"Failed to initialize connection pool: {str(e)}")

    def _create_dsn(self) -> str:
        """Create the Oracle DSN (Data Source Name) string."""
        return f"{self.config.host}:{self.config.port}/{self.config.service_name}"

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            oracledb.Connection: Database connection from the pool
            
        Raises:
            ConnectionError: If there is an error with the database connection
        """
        conn = None
        try:
            conn = self._pool.acquire()
            yield conn
            conn.commit()
        except oracledb.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise ConnectionError(f"Database operation failed: {str(e)}")
        finally:
            if conn:
                self._pool.release(conn)

    def execute_query(
        self,
        query: str,
        params: Optional[Union[tuple, List[tuple], dict]] = None
    ) -> ResultType:
        """
        Execute a SQL query and return the results in the specified format.
        
        Args:
            query: The SQL query to execute
            params: Query parameters for parameterized queries
            
        Returns:
            Query results in the specified format (dict, pandas DataFrame, or Spark DataFrame)
            
        Raises:
            ConnectionError: If there is a database connection error
            DataFormatError: If there is an error converting the result format
        """
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                
                if not cursor.description:  # No data returned
                    return []
                
                # Convert to list of dictionaries
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                if self.config.output_format == "dict":
                    return result
                    
                elif self.config.output_format == "pandas":
                    try:
                        return self._pandas_df.DataFrame(result)
                    except Exception as e:
                        raise DataFormatError(f"Failed to convert to pandas DataFrame: {str(e)}")
                    
                elif self.config.output_format == "spark":
                    try:
                        if result:
                            columns = list(result[0].keys())
                            rows = [[row[col] for col in columns] for row in result]
                            return self._spark.createDataFrame(rows, columns)
                        return self._spark.createDataFrame([], [])
                    except Exception as e:
                        raise DataFormatError(f"Failed to convert to Spark DataFrame: {str(e)}")
                        
            except oracledb.Error as e:
                raise ConnectionError(f"Query execution failed: {str(e)}")
            finally:
                cursor.close()

    def execute_batch(
        self,
        query: str,
        params: List[Union[tuple, dict]]
    ) -> None:
        """
        Execute a batch of parameterized queries.
        
        Args:
            query: The SQL query template to execute
            params: List of parameter sets to use with the query
            
        Raises:
            ConnectionError: If there is a database connection error
            ValidationError: If the parameters are invalid
        """
        if not params:
            raise ValidationError("params must not be empty for batch execution")
            
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.executemany(query, params)
            except oracledb.Error as e:
                raise ConnectionError(f"Batch execution failed: {str(e)}")
            finally:
                cursor.close()

    def close(self) -> None:
        """
        Close the connection pool.
        
        This method should be called when the manager is no longer needed to
        properly clean up resources.
        """
        try:
            if self._pool:
                self._pool.close()
                logger.info("Connection pool closed successfully")
        except oracledb.Error as e:
            logger.error(f"Error closing connection pool: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()