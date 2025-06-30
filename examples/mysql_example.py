from wipekit.read import MySQLManager, MySQLConfig
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    # Configure directly
    config = MySQLConfig(
        host='localhost',
        port=3306,
        database='example_db',
        user='root',
        password='your_password',
        min_connections=1,
        max_connections=5
    )

    # Initialize database manager
    db = MySQLManager(config)

    try:
        # Example 1: Basic Query with Parameters
        query = """
            SELECT * FROM employees 
            WHERE department = %s AND salary > %s
        """
        results = db.execute_query(
            query,
            ('Engineering', 50000)
        )
        
        # Print results
        for row in results:
            print(f"Employee: {row['name']}, Salary: {row['salary']}")

        # Example 2: Using dictionary configuration with pandas output
        config_dict = {
            "host": "localhost",
            "port": 3306,
            "database": "example_db",
            "user": "root",
            "password": "your_password",
            "output_format": "pandas"  # or "spark" or "dict"
        }

        # Using context manager (recommended)
        with MySQLManager(config_dict) as mysql:
            # Returns pandas DataFrame
            df = mysql.execute_query("""
                SELECT department, 
                       COUNT(*) as employee_count,
                       AVG(salary) as avg_salary
                FROM employees
                GROUP BY department
            """)
            print("\nDepartment Statistics:")
            print(df)

        # Example 3: Batch Insert
        insert_query = """
            INSERT INTO employees (name, department, salary)
            VALUES (%s, %s, %s)
        """
        employee_data = [
            ('John Doe', 'Engineering', 75000),
            ('Jane Smith', 'Marketing', 65000),
            ('Bob Johnson', 'Engineering', 80000)
        ]
        with MySQLManager(config) as mysql:
            mysql.execute_batch(insert_query, employee_data)
            print("\nBatch insert completed successfully")

        # Example 4: Using Spark DataFrame output
        config_spark = MySQLConfig(
            host="localhost",
            port=3306,
            database="example_db",
            user="root",
            password="your_password",
            output_format="spark"
        )

        with MySQLManager(config_spark) as mysql:
            # Returns Spark DataFrame
            df = mysql.execute_query("""
                SELECT e.*, d.location
                FROM employees e
                JOIN departments d ON e.department = d.name
                WHERE d.location = 'New York'
            """)
            print(f"\nFound {df.count()} employees in New York")
            df.show()

    except Exception as e:
        logging.error(f"Database error: {str(e)}")
    finally:
        db.close()

if __name__ == '__main__':
    main()
