from typing import Optional, Dict, Any, List, Union, TYPE_CHECKING
import logging
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor, execute_values
from contextlib import contextmanager
from .config import PostgreSQLConfig

# Type checking imports
if TYPE_CHECKING:
    import pandas as pd
    from pyspark.sql import DataFrame as SparkDataFrame

logger = logging.getLogger(__name__)

# Define return type alias for clarity
ResultType = Union[List[Dict[str, Any]], 'pd.DataFrame', 'SparkDataFrame']

class PostgreSQLManager:
    """
    A professional PostgreSQL connection manager with connection pooling, error handling,
    and DataFrame conversion capabilities.
    """
    
    def __init__(self, config: Union[PostgreSQLConfig, Dict[str, Any]]):
        """Initialize the PostgreSQL connection manager."""
        self.config = (config if isinstance(config, PostgreSQLConfig) 
                      else PostgreSQLConfig.from_dict(config))
        self._pool: Optional[SimpleConnectionPool] = None
        self._pandas_df = None
        self._spark = None
        
        # Lazy import of optional dependencies
        if self.config.output_format == "pandas":
            try:
                import pandas as pd
                self._pandas_df = pd
            except ImportError:
                raise ImportError(
                    "pandas is required for pandas output format. "
                    "Install it with: pip install pandas"
                )
        
        elif self.config.output_format == "spark":
            try:
                from pyspark.sql import SparkSession
                self._spark = SparkSession.builder.getOrCreate()
            except ImportError:
                raise ImportError(
                    "pyspark is required for spark output format. "
                    "Install it with: pip install pyspark"
                )
        
        self.initialize_pool()

    def initialize_pool(self) -> None:
        """Initialize the connection pool with the configured parameters."""
        try:
            self._pool = SimpleConnectionPool(
                minconn=self.config.min_connections,
                maxconn=self.config.max_connections,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                cursor_factory=RealDictCursor
            )
            logger.info(f"Successfully initialized connection pool to database: {self.config.database}")
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            psycopg2.extensions.connection: Database connection from the pool
        """
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
            conn.commit()
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                self._pool.putconn(conn)

    def execute_query(self, query: str, params: Optional[tuple] = None) -> ResultType:
        """Execute a SQL query and return the results in the specified format."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if not cur.description:  # No data returned
                    return []
                    
                result = cur.fetchall()
                
                if self.config.output_format == "dict":
                    return result
                    
                elif self.config.output_format == "pandas":
                    return self._pandas_df.DataFrame(result)
                    
                elif self.config.output_format == "spark":
                    if result:
                        columns = list(result[0].keys())
                        rows = [[row[col] for col in columns] for row in result]
                        return self._spark.createDataFrame(rows, columns)
                    return self._spark.createDataFrame([], [])

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name (str): Name of the table to check
            
        Returns:
            bool: True if table exists, False otherwise
        """
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """
        result = self.execute_query(query, (table_name,))
        return result[0]['exists'] if result else False

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get the schema information for a table.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            List[Dict[str, Any]]: Column information for the table
        """
        query = """
            SELECT column_name, data_type, character_maximum_length,
                   is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """
        return self.execute_query(query, (table_name,))

    def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        """
        Create a new table in the database.
        
        Args:
            table_name (str): Name of the table to create
            columns (Dict[str, str]): Dictionary of column names and their SQL types
        """
        columns_sql = ", ".join(f"{name} {dtype}" for name, dtype in columns.items())
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});"
        self.execute_query(query)

    def close(self) -> None:
        """Close all database connections in the pool."""
        if self._pool:
            self._pool.closeall()
            logger.info("Closed all database connections")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()