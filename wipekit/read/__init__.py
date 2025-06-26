from .postgresql import PostgreSQLManager
from .mysql import MySQLManager
from .oracle import OracleManager
from .config import PostgreSQLConfig, MySQLConfig, OracleConfig

__all__ = [
    'PostgreSQLManager', 'PostgreSQLConfig',
    'MySQLManager', 'MySQLConfig',
    'OracleManager', 'OracleConfig'
]

"""
Example usage:

PostgreSQL:
----------
from wipekit.read import PostgreSQLManager, PostgreSQLConfig

# Configure your database connection
config = PostgreSQLConfig(
    host='localhost',
    port=5432,
    database='your_db',
    user='your_user',
    password='your_password'
)

# Initialize the connection manager
db = PostgreSQLManager(config)

# Execute a query
results = db.execute_query("SELECT * FROM your_table WHERE column = %s", ('value',))

# Close connections when done
db.close()

MySQL:
-----
from wipekit.read import MySQLManager, MySQLConfig

# Configure your database connection
config = MySQLConfig(
    host='localhost',
    port=3306,
    database='your_db',
    user='your_user',
    password='your_password'
)

# Using context manager (recommended)
with MySQLManager(config) as db:
    df = db.execute_query('SELECT * FROM your_table WHERE id = %s', (123,))

Oracle:
-------
from wipekit.read import OracleManager, OracleConfig

# Configure your database connection
config = OracleConfig(
    host='localhost',
    port=1521,
    service_name='ORCL',
    user='scott',
    password='tiger'
)

# Using context manager (recommended)
with OracleManager(config) as db:
    # Oracle uses :1, :2, etc. for bind variables
    df = db.execute_query('SELECT * FROM emp WHERE deptno = :1', (10,))
"""