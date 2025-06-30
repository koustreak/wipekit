# wipekit - Data anonymization module
# Copyright (c) 2025 Wipekit Authors
# MIT License

from typing import List, Dict, Union, Optional, Any
import pandas as pd
import numpy as np
from collections import Counter
from sklearn.preprocessing import KBinsDiscretizer

from wipekit.logging import get_logger

# Initialize module-level logger
logger = get_logger("wipekit.anonymization.k_anonymity")

class KAnonymity:
    """
    Implements the K-Anonymity data anonymization technique.

    K-Anonymity ensures that each record in a dataset cannot be distinguished from 
    at least k-1 other records with respect to the quasi-identifier attributes. This
    helps protect privacy while maintaining data utility for analysis purposes.
    """

    def __init__(self, k: int = 2):
        """
        Initialize K-Anonymity with the desired k value.

        Args:
            k (int): The k value - each quasi-identifier combination should appear at least k times.
                     Default is 2, which means each combination must appear at least twice.
        """
        if not isinstance(k, int) or k < 2:
            raise ValueError("k must be an integer greater than or equal to 2")
        self.k = k

    def anonymize(self, 
                  df: pd.DataFrame, 
                  quasi_identifiers: List[str],
                  categorical_method: str = 'generalization',
                  numerical_method: str = 'binning',
                  bin_count: int = 5) -> pd.DataFrame:
        """
        Anonymize a DataFrame to satisfy k-anonymity with respect to the quasi-identifiers.

        Args:
            df (pd.DataFrame): The DataFrame to anonymize
            quasi_identifiers (List[str]): List of column names that serve as quasi-identifiers
            categorical_method (str): Method for handling categorical columns ('generalization' or 'suppression')
            numerical_method (str): Method for handling numerical columns ('binning' or 'microaggregation')
            bin_count (int): Number of bins to use for numerical discretization

        Returns:
            pd.DataFrame: Anonymized DataFrame satisfying k-anonymity
        """
        # Validate inputs
        if not isinstance(df, pd.DataFrame):
            logger.error("Invalid input: df is not a pandas DataFrame")
            raise TypeError("df must be a pandas DataFrame")
        if not all(col in df.columns for col in quasi_identifiers):
            logger.error(f"Missing columns in DataFrame: {[col for col in quasi_identifiers if col not in df.columns]}")
            raise ValueError("All quasi-identifiers must be columns in the DataFrame")

        logger.info(f"Starting anonymization with k={self.k}", extra={
            "rows": len(df),
            "quasi_identifiers": quasi_identifiers,
            "categorical_method": categorical_method,
            "numerical_method": numerical_method
        })

        # Create a copy to avoid modifying the original
        anonymized_df = df.copy()

        # Process each quasi-identifier
        for column in quasi_identifiers:
            # Check data type to apply appropriate anonymization
            if pd.api.types.is_numeric_dtype(anonymized_df[column]):
                logger.debug(f"Anonymizing numerical column: {column} using method {numerical_method}")
                anonymized_df = self._anonymize_numerical(
                    anonymized_df, column, method=numerical_method, bin_count=bin_count
                )
            else:
                logger.debug(f"Anonymizing categorical column: {column} using method {categorical_method}")
                anonymized_df = self._anonymize_categorical(
                    anonymized_df, column, method=categorical_method
                )

        # Check if k-anonymity is satisfied
        if not self._verify_k_anonymity(anonymized_df, quasi_identifiers):
            logger.warning(f"K-anonymity not satisfied after initial processing, applying suppression")
            # If not, apply suppression on problematic records
            anonymized_df = self._apply_suppression(anonymized_df, quasi_identifiers)

        logger.info(f"Anonymization complete", extra={
            "original_rows": len(df),
            "anonymized_rows": len(anonymized_df),
            "columns_anonymized": len(quasi_identifiers)
        })

        return anonymized_df

    def _anonymize_numerical(self, 
                             df: pd.DataFrame, 
                             column: str, 
                             method: str = 'binning',
                             bin_count: int = 5) -> pd.DataFrame:
        """
        Anonymize a numerical column using the specified method.

        Args:
            df (pd.DataFrame): The DataFrame containing the column
            column (str): The column name to anonymize
            method (str): Method to use ('binning' or 'microaggregation')
            bin_count (int): Number of bins for discretization

        Returns:
            pd.DataFrame: DataFrame with the anonymized column
        """
        result_df = df.copy()

        if method == 'binning':
            # Use quantile-based discretization
            discretizer = KBinsDiscretizer(n_bins=bin_count, encode='ordinal', strategy='quantile')
            values = df[column].values.reshape(-1, 1)
            binned_values = discretizer.fit_transform(values)

            # Convert bin indices to bin ranges
            bin_edges = discretizer.bin_edges_[0]
            bin_labels = [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(bin_edges)-1)]
            result_df[column] = [bin_labels[int(x[0])] for x in binned_values]

        elif method == 'microaggregation':
            # Group values and replace with group mean
            sorted_values = sorted(df[column].values)
            groups = [sorted_values[i:i+self.k] for i in range(0, len(sorted_values), self.k)]

            # Create a mapping from original values to group means
            value_to_mean = {}
            for group in groups:
                group_mean = sum(group) / len(group)
                for value in group:
                    value_to_mean[value] = group_mean

            result_df[column] = df[column].map(value_to_mean)
        else:
            raise ValueError(f"Unsupported numerical anonymization method: {method}")

        return result_df

    def _anonymize_categorical(self,
                               df: pd.DataFrame,
                               column: str,
                               method: str = 'generalization') -> pd.DataFrame:
        """
        Anonymize a categorical column using the specified method.

        Args:
            df (pd.DataFrame): The DataFrame containing the column
            column (str): The column name to anonymize
            method (str): Method to use ('generalization' or 'suppression')

        Returns:
            pd.DataFrame: DataFrame with the anonymized column
        """
        result_df = df.copy()

        if method == 'generalization':
            # Count frequency of each value
            value_counts = Counter(df[column])

            # Identify values that don't meet k-anonymity
            rare_values = {value for value, count in value_counts.items() if count < self.k}

            # Replace rare values with a general category
            if rare_values:
                result_df[column] = result_df[column].apply(
                    lambda x: 'Other' if x in rare_values else x
                )

        elif method == 'suppression':
            # Count frequency of each value
            value_counts = Counter(df[column])

            # Identify values that don't meet k-anonymity
            rare_values = {value for value, count in value_counts.items() if count < self.k}

            # Replace rare values with a NULL value
            if rare_values:
                result_df[column] = result_df[column].apply(
                    lambda x: None if x in rare_values else x
                )

        else:
            raise ValueError(f"Unsupported categorical anonymization method: {method}")

        return result_df

    def _verify_k_anonymity(self, df: pd.DataFrame, quasi_identifiers: List[str]) -> bool:
        """
        Verify if the DataFrame satisfies k-anonymity for the given quasi-identifiers.

        Args:
            df (pd.DataFrame): The DataFrame to check
            quasi_identifiers (List[str]): List of quasi-identifier columns

        Returns:
            bool: True if k-anonymity is satisfied, False otherwise
        """
        # Count occurrences of each quasi-identifier combination
        combination_counts = df.groupby(quasi_identifiers).size()

        # Check if all combinations appear at least k times
        return combination_counts.min() >= self.k

    def _apply_suppression(self, df: pd.DataFrame, quasi_identifiers: List[str]) -> pd.DataFrame:
        """
        Apply suppression to ensure k-anonymity.

        Args:
            df (pd.DataFrame): The DataFrame to modify
            quasi_identifiers (List[str]): List of quasi-identifier columns

        Returns:
            pd.DataFrame: DataFrame with suppressed records to ensure k-anonymity
        """
        result_df = df.copy()

        # Count occurrences of each quasi-identifier combination
        combination_counts = df.groupby(quasi_identifiers).size().reset_index(name='count')

        # Identify combinations that violate k-anonymity
        violating_combinations = combination_counts[combination_counts['count'] < self.k]

        if len(violating_combinations) > 0:
            # Create a mask for records that violate k-anonymity
            mask = pd.Series(False, index=df.index)

            for _, row in violating_combinations.iterrows():
                # Create a condition to match this specific combination
                condition = pd.Series(True, index=df.index)
                for col in quasi_identifiers:
                    condition &= (df[col] == row[col])

                # Add these records to the mask
                mask |= condition

            # Suppress quasi-identifiers for violating records
            for col in quasi_identifiers:
                result_df.loc[mask, col] = None

        return result_df

    def evaluate_information_loss(self, 
                                original_df: pd.DataFrame, 
                                anonymized_df: pd.DataFrame,
                                quasi_identifiers: List[str]) -> Dict[str, float]:
        """
        Evaluate the information loss due to anonymization.

        Args:
            original_df (pd.DataFrame): Original DataFrame before anonymization
            anonymized_df (pd.DataFrame): Anonymized DataFrame
            quasi_identifiers (List[str]): List of quasi-identifier columns

        Returns:
            Dict[str, float]: Dictionary with information loss metrics
        """
        metrics = {}

        # Calculate suppression rate (percentage of suppressed values)
        for col in quasi_identifiers:
            null_count = anonymized_df[col].isna().sum()
            metrics[f"{col}_suppression_rate"] = null_count / len(anonymized_df) * 100

        # Calculate overall suppression rate
        total_cells = len(anonymized_df) * len(quasi_identifiers)
        total_suppressed = sum(anonymized_df[col].isna().sum() for col in quasi_identifiers)
        metrics["overall_suppression_rate"] = total_suppressed / total_cells * 100

        # Calculate generalization impact for numerical columns
        for col in quasi_identifiers:
            if pd.api.types.is_numeric_dtype(original_df[col]):
                # If binning was applied, calculate average bin size
                if not pd.api.types.is_numeric_dtype(anonymized_df[col]):
                    metrics[f"{col}_avg_generalization"] = (
                        original_df[col].max() - original_df[col].min()
                    ) / anonymized_df[col].nunique()

        # Calculate equivalence class statistics
        ec_sizes = anonymized_df.groupby(quasi_identifiers).size()
        metrics["equivalence_class_count"] = len(ec_sizes)
        metrics["avg_equivalence_class_size"] = ec_sizes.mean()

        return metrics
