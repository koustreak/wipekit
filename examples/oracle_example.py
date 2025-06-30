from wipekit.read import OracleManager, OracleConfig
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def main():
    # Configure directly
    config = OracleConfig(
        host='localhost',
        port=1521,
        service_name='ORCL',
        user='scott',
        password='tiger',
        min_connections=1,
        max_connections=5
    )

    # Initialize database manager
    db = OracleManager(config)

    try:
        # Example 1: Basic Query with Bind Variables
        # Note: Oracle uses :1, :2, etc. for bind variables
        query = """
            SELECT * FROM emp 
            WHERE deptno = :1 AND sal > :2
        """
        results = db.execute_query(
            query,
            (10, 2000)  # department 10, salary > 2000
        )
        
        # Print results
        for row in results:
            print(f"Employee: {row['ENAME']}, Salary: {row['SAL']}")

        # Example 2: Using dictionary configuration with pandas output
        config_dict = {
            "host": "localhost",
            "port": 1521,
            "service_name": "ORCL",
            "user": "scott",
            "password": "tiger",
            "output_format": "pandas"  # or "spark" or "dict"
        }

        # Using context manager (recommended)
        with OracleManager(config_dict) as oracle:
            # Returns pandas DataFrame
            df = oracle.execute_query("""
                SELECT d.dname, 
                       COUNT(*) as emp_count,
                       AVG(e.sal) as avg_salary
                FROM emp e
                JOIN dept d ON e.deptno = d.deptno
                GROUP BY d.dname
            """)
            print("\nDepartment Statistics:")
            print(df)

        # Example 3: Batch Insert
        insert_query = """
            INSERT INTO emp (empno, ename, job, sal, deptno)
            VALUES (:1, :2, :3, :4, :5)
        """
        employee_data = [
            (7991, 'JOHN', 'ANALYST', 3000, 20),
            (7992, 'JANE', 'MANAGER', 3500, 30),
            (7993, 'BOB', 'ANALYST', 3200, 20)
        ]
        with OracleManager(config) as oracle:
            oracle.execute_batch(insert_query, employee_data)
            print("\nBatch insert completed successfully")

        # Example 4: Using Spark DataFrame output
        config_spark = OracleConfig(
            host="localhost",
            port=1521,
            service_name="ORCL",
            user="scott",
            password="tiger",
            output_format="spark"
        )

        with OracleManager(config_spark) as oracle:
            # Returns Spark DataFrame
            df = oracle.execute_query("""
                SELECT e.*, d.dname, d.loc
                FROM emp e
                JOIN dept d ON e.deptno = d.deptno
                WHERE d.loc = :1
            """, ('NEW YORK',))
            print(f"\nFound {df.count()} employees in New York")
            df.show()

        # Example 5: Using PL/SQL blocks
        with OracleManager(config) as oracle:
            # Execute a PL/SQL block
            plsql = """
                BEGIN
                    -- Update salaries with 10% increase for a department
                    UPDATE emp
                    SET sal = sal * 1.1
                    WHERE deptno = :1;
                    
                    -- Calculate and return the average salary
                    SELECT AVG(sal) INTO :2
                    FROM emp
                    WHERE deptno = :1;
                END;
            """
            dept_no = 20
            result = oracle.execute_query(plsql, (dept_no,))
            print(f"\nUpdated salaries for department {dept_no}")
            print(f"New average salary: {result}")

    except Exception as e:
        logging.error(f"Database error: {str(e)}")
    finally:
        db.close()

if __name__ == '__main__':
    main()
