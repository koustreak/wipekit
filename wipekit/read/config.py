from dataclasses import dataclass
from typing import Optional

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
        """Validate configuration parameters"""
        if not isinstance(self.port, int):
            raise ValueError("Port must be an integer")
        
        if self.min_connections > self.max_connections:
            raise ValueError("min_connections cannot be greater than max_connections")
            
        if self.output_format not in ["dict", "pandas", "spark"]:
            raise ValueError("output_format must be one of: dict, pandas, spark")

    @classmethod
    def from_dict(cls, config: dict) -> 'PostgreSQLConfig':
        """
        Create a configuration instance from a dictionary.
        
        Args:
            config (dict): Dictionary containing configuration values
            
        Returns:
            PostgreSQLConfig: Configuration instance with values from dictionary
        """
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