from wipekit.read import PostgreSQLManager, PostgreSQLConfig
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    # Configure directly
    config = PostgreSQLConfig(
        host='localhost',
        port=5432,
        database='example_db',
        user='postgres',
        password='your_password',
        min_connections=1,
        max_connections=5
    )

    # Initialize database manager
    db = PostgreSQLManager(config)

    try:
        # Create a sample table
        columns = {
            'id': 'SERIAL PRIMARY KEY',
            'name': 'VARCHAR(100) NOT NULL',
            'email': 'VARCHAR(255) UNIQUE',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        db.create_table('users', columns)

        # Insert sample data
        insert_query = """
            INSERT INTO users (name, email) VALUES %s
        """
        users_data = [
            ('John Doe', 'john@example.com'),
            ('Jane Smith', 'jane@example.com')
        ]
        db.execute_batch(insert_query, users_data)

        # Query the data
        results = db.execute_query(
            "SELECT * FROM users WHERE email LIKE %s",
            ('%@example.com',)
        )
        
        # Print results
        for row in results:
            print(f"User: {row['name']}, Email: {row['email']}")

        # Get table schema
        schema = db.get_table_schema('users')
        print("\nTable Schema:")
        for column in schema:
            print(f"{column['column_name']}: {column['data_type']}")

        # Example 1: Using dictionary configuration with pandas output
        config_dict = {
            "host": "localhost",
            "port": 5432,
            "database": "mydb",
            "user": "user",
            "password": "password",
            "output_format": "pandas"  # or "spark" or "dict"
        }

        # Using context manager (recommended)
        with PostgreSQLManager(config_dict) as pg:
            # Returns pandas DataFrame
            df = pg.execute_query("SELECT * FROM my_table")
            print(f"Data shape: {df.shape}")

        # Example 2: Using configuration object with Spark output
        config_spark = PostgreSQLConfig(
            host="localhost",
            port=5432,
            database="mydb",
            user="user",
            password="password",
            output_format="spark"
        )

        # Direct instantiation
        pg = PostgreSQLManager(config_spark)
        try:
            # Returns Spark DataFrame
            df = pg.execute_query("SELECT * FROM my_table")
            print(f"Number of partitions: {df.rdd.getNumPartitions()}")
        finally:
            pg.close()

        # Example 3: Basic dictionary output
        config_dict["output_format"] = "dict"
        with PostgreSQLManager(config_dict) as pg:
            # Returns list of dictionaries
            results = pg.execute_query("SELECT * FROM my_table")
            for row in results:
                print(row)  # Each row is a dictionary

    except Exception as e:
        logging.error(f"Database error: {str(e)}")
    finally:
        db.close()

if __name__ == '__main__':
    main()