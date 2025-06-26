"""
Custom exceptions for the wipekit library.

This module defines a hierarchy of exceptions specific to different data preprocessing
operations and error conditions that may occur in the wipekit library.
"""

class WipekitError(Exception):
    """Base exception class for all wipekit errors."""
    pass


class ConfigurationError(WipekitError):
    """Raised when there is an error in configuration parameters."""
    pass


class ConnectionError(WipekitError):
    """Raised when there is an error establishing or maintaining connections."""
    pass


class DataFormatError(WipekitError):
    """Raised when there is an error converting between data formats."""
    pass


class ValidationError(WipekitError):
    """Raised when data validation fails."""
    pass


class PreprocessingError(WipekitError):
    """Base class for preprocessing-related errors."""
    pass


class ImputationError(PreprocessingError):
    """Raised when there is an error during missing value imputation."""
    pass


class OutlierError(PreprocessingError):
    """Raised when there is an error during outlier detection/treatment."""
    pass


class EncodingError(PreprocessingError):
    """Raised when there is an error during data encoding."""
    pass


class ScalingError(PreprocessingError):
    """Raised when there is an error during data scaling."""
    pass


class FeatureEngineeringError(PreprocessingError):
    """Raised when there is an error during feature engineering."""
    pass


class TimeSeriesError(PreprocessingError):
    """Raised when there is an error processing time series data."""
    pass


class NLPError(PreprocessingError):
    """Raised when there is an error during NLP preprocessing."""
    pass


class GeospatialError(PreprocessingError):
    """Raised when there is an error processing geospatial data."""
    pass


class GraphError(PreprocessingError):
    """Raised when there is an error processing graph data."""
    pass


class DriftError(PreprocessingError):
    """Raised when there is an error during drift detection."""
    pass


class AnonymizationError(PreprocessingError):
    """Raised when there is an error during data anonymization."""
    pass