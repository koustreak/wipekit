from .postgresql import PostgreSQLManager
from .config import PostgreSQLConfig

__all__ = ['PostgreSQLManager', 'PostgreSQLConfig']

"""
Example usage:

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

# Batch insert
data = [
    ('value1', 123),
    ('value2', 456)
]
db.execute_batch(
    "INSERT INTO your_table (text_column, number_column) VALUES %s",
    data
)

# Get table schema
schema = db.get_table_schema('your_table')

# Create a new table
columns = {
    'id': 'SERIAL PRIMARY KEY',
    'name': 'VARCHAR(100)',
    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
}
db.create_table('new_table', columns)

# Close connections when done
db.close()
"""