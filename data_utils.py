import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import io

def analyze_dataframe(df: pd.DataFrame) -> Dict:
    """Analyze DataFrame and return comprehensive statistics"""
    analysis = {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'dtypes': dict(df.dtypes.astype(str)),
        'missing_values': df.isnull().sum().to_dict(),
        'numeric_stats': {},
        'categorical_stats': {}
    }
    
    # Analyze numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        analysis['numeric_stats'][col] = {
            'mean': float(df[col].mean()) if not df[col].isna().all() else None,
            'std': float(df[col].std()) if not df[col].isna().all() else None,
            'min': float(df[col].min()) if not df[col].isna().all() else None,
            'max': float(df[col].max()) if not df[col].isna().all() else None,
            'unique_count': int(df[col].nunique())
        }
    
    # Analyze categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'string']).columns
    for col in categorical_cols:
        value_counts = df[col].value_counts().head(10)
        analysis['categorical_stats'][col] = {
            'unique_count': int(df[col].nunique()),
            'most_common': value_counts.to_dict(),
            'sample_values': df[col].dropna().head(5).tolist()
        }
    
    return analysis

def append_rows_to_dataframe(original_df: pd.DataFrame, new_rows: List[Dict]) -> pd.DataFrame:
    """Append new rows to DataFrame"""
    if not new_rows:
        return original_df
    
    # Create DataFrame from new rows
    new_df = pd.DataFrame(new_rows)
    
    # Ensure column order matches
    new_df = new_df.reindex(columns=original_df.columns)
    
    # Append and return
    result_df = pd.concat([original_df, new_df], ignore_index=True)
    return result_df

def create_download_link(df: pd.DataFrame, filename: str = "enhanced_data.csv") -> Tuple[str, str]:
    """Create downloadable CSV data"""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    return csv_data, filename

def detect_potential_biases(original_df: pd.DataFrame, comparison_df: pd.DataFrame) -> List[str]:
    """Detect potential biases between original and new data"""
    biases = []
    
    # Check for categorical column distributions
    categorical_cols = original_df.select_dtypes(include=['object', 'string']).columns
    
    for col in categorical_cols:
        if col in comparison_df.columns:
            orig_values = set(original_df[col].dropna().unique())
            new_values = set(comparison_df[col].dropna().unique())
            
            # Check for new categories
            novel_values = new_values - orig_values
            if novel_values:
                biases.append(f"New categories in '{col}': {list(novel_values)}")
    
    # Check numeric distributions
    numeric_cols = original_df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        if col in comparison_df.columns and not comparison_df[col].isna().all():
            orig_mean = original_df[col].mean()
            new_mean = comparison_df[col].mean()
            
            if abs(orig_mean - new_mean) > orig_mean * 0.2:  # 20% difference
                biases.append(f"Significant mean shift in '{col}': {orig_mean:.2f} → {new_mean:.2f}")
    
    return biases

def shuffle_dataframe_sample(df: pd.DataFrame, n_samples: int = 5) -> pd.DataFrame:
    """Return a shuffled sample of the DataFrame"""
    if len(df) <= n_samples:
        return df.sample(frac=1).reset_index(drop=True)
    else:
        return df.sample(n=n_samples).reset_index(drop=True)
