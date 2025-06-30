"""
MySQL Database Manager Module
===========================

This module provides a high-performance MySQL database connection manager with advanced 
features for data processing and analysis workflows. It implements connection pooling,
robust error handling, and flexible data format conversions.

Features:
---------
- Connection pooling for efficient database access
- Multiple output formats (dict, pandas DataFrame, Spark DataFrame)
- Context manager interface for safe connection handling
- Comprehensive error handling and connection cleanup
- Query parameterization for SQL injection prevention
- Type hints and full documentation
- Thread-safe operations

Dependencies:
------------
- Required: mysql-connector-python
- Optional: pandas (for DataFrame output)
- Optional: pyspark (for Spark DataFrame output)

Example:
--------
from wipekit.read import MySQLConfig, MySQLManager

config = MySQLConfig(
    host='localhost',
    database='mydb',
    user='user',
    password='pass',
    output_format='pandas'
)

# Using context manager (recommended)
with MySQLManager(config) as mysql:
    # Returns pandas DataFrame
    df = mysql.execute_query('SELECT * FROM mytable WHERE status = %s', ('active',))
    print(f"Found {len(df)} active records")
"""

from typing import Optional, Dict, Any, List, Union, TYPE_CHECKING
import logging
from dataclasses import dataclass
from contextlib import contextmanager

# Third-party imports
try:
    import mysql.connector
    from mysql.connector import pooling
except ImportError:
    raise ImportError(
        "mysql-connector-python is required. "
        "Install it with: pip install mysql-connector-python"
    )

# Local imports
from .config import MySQLConfig
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

class MySQLManager:
    """
    A professional MySQL connection manager with connection pooling, error handling,
    and DataFrame conversion capabilities.
    """
    
    def __init__(self, config: Union[MySQLConfig, Dict[str, Any]]):
        """
        Initialize the MySQL connection manager.
        
        Args:
            config: Either a MySQLConfig object or a dictionary with configuration values
            
        Raises:
            ConfigurationError: If the configuration is invalid
            ConnectionError: If unable to establish connection pool
        """
        try:
            self.config = (config if isinstance(config, MySQLConfig) 
                         else MySQLConfig.from_dict(config))
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
        Initialize the MySQL connection pool.
        
        Raises:
            ConnectionError: If unable to create the connection pool
        """
        try:
            pool_config = {
                'pool_name': 'wipekit_mysql_pool',
                'pool_size': self.config.max_connections,
                'host': self.config.host,
                'port': self.config.port,
                'database': self.config.database,
                'user': self.config.user,
                'password': self.config.password,
                'charset': 'utf8mb4',
                'use_pure': True,  # Recommended for better compatibility
                'get_warnings': True,
            }
            
            self._pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            logger.info(f"Successfully initialized connection pool to database: {self.config.database}")
            
        except mysql.connector.Error as e:
            raise ConnectionError(f"Failed to initialize connection pool: {str(e)}")

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            mysql.connector.connection.MySQLConnection: Database connection from the pool
            
        Raises:
            ConnectionError: If there is an error with the database connection
        """
        conn = None
        try:
            conn = self._pool.get_connection()
            yield conn
            conn.commit()
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise ConnectionError(f"Database operation failed: {str(e)}")
        finally:
            if conn:
                conn.close()

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
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params)
                
                if not cursor.description:  # No data returned
                    return []
                    
                result = cursor.fetchall()
                
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
                        
            except mysql.connector.Error as e:
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
            except mysql.connector.Error as e:
                raise ConnectionError(f"Batch execution failed: {str(e)}")
            finally:
                cursor.close()

    def close(self) -> None:
        """
        Close the connection pool.
        
        This method should be called when the manager is no longer needed to
        properly clean up resources.
        """
        # MySQL Connector's connection pool handles cleanup automatically
        logger.info("Connection pool resources released")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()