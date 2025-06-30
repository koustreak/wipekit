"""
Configuration Module for Database Connections in WipeKit
=====================================================

This module provides configuration classes for managing database connections across
different database management systems (PostgreSQL, MySQL, Oracle). Each configuration
class implements validation, default values, and dictionary-based instantiation.

Configuration Classes:
    - PostgreSQLConfig: Configuration for PostgreSQL database connections
    - MySQLConfig: Configuration for MySQL database connections
    - OracleConfig: Configuration for Oracle database connections

Common Features:
    - Connection pool management (min/max connections)
    - Multiple output formats (dict, pandas, spark)
    - Comprehensive parameter validation
    - Dictionary-based instantiation
    - Default values for common parameters

Example:
    >>> config = PostgreSQLConfig(
    ...     host='localhost',
    ...     port=5432,
    ...     database='mydb',
    ...     user='admin',
    ...     password='secret'
    ... )
    >>> # Or using dictionary
    >>> config_dict = {
    ...     'host': 'localhost',
    ...     'database': 'mydb',
    ...     'user': 'admin',
    ...     'password': 'secret'
    ... }
    >>> config = PostgreSQLConfig.from_dict(config_dict)
"""

from dataclasses import dataclass
from ..exceptions import ConfigurationError

@dataclass
class PostgreSQLConfig:
    """Configuration class for PostgreSQL database connections."""
    
    host: str
    port: int
    database: str
    user: str
    password: str
    min_connections: int = 1
    max_connections: int = 10
    output_format: str = "dict"  # Options: "dict", "pandas", "spark"
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        """
        Validate configuration parameters
        
        Raises:
            ConfigurationError: If any configuration parameter is invalid
        """
        if not isinstance(self.port, int):
            raise ConfigurationError("Port must be an integer")
        
        if self.min_connections > self.max_connections:
            raise ConfigurationError("min_connections cannot be greater than max_connections")
            
        if self.output_format not in ["dict", "pandas", "spark"]:
            raise ConfigurationError("output_format must be one of: dict, pandas, spark")

    @classmethod
    def from_dict(cls, config: dict) -> 'PostgreSQLConfig':
        """
        Create a configuration instance from a dictionary.
        
        Args:
            config (dict): Dictionary containing configuration values
            
        Returns:
            PostgreSQLConfig: Configuration instance with values from dictionary
            
        Raises:
            ConfigurationError: If required configuration values are missing or invalid
        """
        try:
            return cls(
                host=config.get('host', 'localhost'),
                port=int(config.get('port', 5432)),
                database=config['database'],
                user=config['user'],
                password=config['password'],
                min_connections=int(config.get('min_connections', 1)),
                max_connections=int(config.get('max_connections', 10)),
                output_format=config.get('output_format', 'dict')
            )
        except KeyError as e:
            raise ConfigurationError(f"Missing required configuration value: {str(e)}")
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration value: {str(e)}")

@dataclass
class MySQLConfig:
    """Configuration class for MySQL database connections."""
    
    host: str
    port: int = 3306
    database: str = None
    user: str = None
    password: str = None
    min_connections: int = 1
    max_connections: int = 10
    output_format: str = "dict"  # Options: "dict", "pandas", "spark"
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        """
        Validate configuration parameters for database connection.

        Performs comprehensive validation of all configuration parameters to ensure
        they meet the requirements for establishing a successful database connection:
        - Verifies data types (e.g., port must be an integer)
        - Validates connection pool settings (min <= max connections)
        - Ensures required credentials are provided
        - Checks that output format is supported
        - Validates database-specific parameters

        This method is automatically called during object initialization via __post_init__
        to ensure configuration validity before any connection attempt is made.

        Raises:
            ConfigurationError: If any configuration parameter is invalid or missing
        """
        if not isinstance(self.port, int):
            raise ConfigurationError("Port must be an integer")
        
        if self.min_connections > self.max_connections:
            raise ConfigurationError("min_connections cannot be greater than max_connections")
            
        if self.output_format not in ["dict", "pandas", "spark"]:
            raise ConfigurationError("output_format must be one of: dict, pandas, spark")
            
        if not self.database:
            raise ConfigurationError("database name is required")
            
        if not self.user:
            raise ConfigurationError("user name is required")
            
        if not self.password:
            raise ConfigurationError("password is required")

    @classmethod
    def from_dict(cls, config: dict) -> 'MySQLConfig':
        """
        Create a configuration instance from a dictionary.
        
        Args:
            config (dict): Dictionary containing configuration values
            
        Returns:
            MySQLConfig: Configuration instance with values from dictionary
            
        Raises:
            ConfigurationError: If required configuration values are missing or invalid
        """
        try:
            return cls(
                host=config.get('host', 'localhost'),
                port=int(config.get('port', 3306)),
                database=config['database'],
                user=config['user'],
                password=config['password'],
                min_connections=int(config.get('min_connections', 1)),
                max_connections=int(config.get('max_connections', 10)),
                output_format=config.get('output_format', 'dict')
            )
        except KeyError as e:
            raise ConfigurationError(f"Missing required configuration value: {str(e)}")
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration value: {str(e)}")

@dataclass
class OracleConfig:
    """Configuration class for Oracle database connections."""
    
    host: str
    port: int = 1521  # Default Oracle port
    service_name: str = None
    user: str = None
    password: str = None
    min_connections: int = 1
    max_connections: int = 10
    output_format: str = "dict"  # Options: "dict", "pandas", "spark"
    
    def __post_init__(self):
        self.validate()
    
    def validate(self) -> None:
        """
        Validate configuration parameters
        
        Raises:
            ConfigurationError: If any configuration parameter is invalid
        """
        if not isinstance(self.port, int):
            raise ConfigurationError("Port must be an integer")
        
        if self.min_connections > self.max_connections:
            raise ConfigurationError("min_connections cannot be greater than max_connections")
            
        if self.output_format not in ["dict", "pandas", "spark"]:
            raise ConfigurationError("output_format must be one of: dict, pandas, spark")
            
        if not self.service_name:
            raise ConfigurationError("service_name is required")
            
        if not self.user:
            raise ConfigurationError("user name is required")
            
        if not self.password:
            raise ConfigurationError("password is required")

    @classmethod
    def from_dict(cls, config: dict) -> 'OracleConfig':
        """
        Create a configuration instance from a dictionary.
        
        Args:
            config (dict): Dictionary containing configuration values
            
        Returns:
            OracleConfig: Configuration instance with values from dictionary
            
        Raises:
            ConfigurationError: If required configuration values are missing or invalid
        """
        try:
            return cls(
                host=config.get('host', 'localhost'),
                port=int(config.get('port', 1521)),
                service_name=config['service_name'],
                user=config['user'],
                password=config['password'],
                min_connections=int(config.get('min_connections', 1)),
                max_connections=int(config.get('max_connections', 10)),
                output_format=config.get('output_format', 'dict')
            )
        except KeyError as e:
            raise ConfigurationError(f"Missing required configuration value: {str(e)}")
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration value: {str(e)}")