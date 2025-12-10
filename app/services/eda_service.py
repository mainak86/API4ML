# app/services/eda_service.py
"""EDA service for dataset analysis."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from scipy import stats

from app.schemas import (
    ColumnStats, DatasetOverview, HistogramData, BoxPlotData,
    BarChartData, CorrelationMatrix, MissingDataMatrix,
    ScatterPlotData, ChartDataCollection
)


class EDAService:
    """Service for performing exploratory data analysis."""
    
    @staticmethod
    def load_dataset(file_path: Path) -> pd.DataFrame:
        """Load dataset based on file extension."""
        extension = file_path.suffix.lower()
        
        if extension == '.csv':
            return pd.read_csv(file_path)
        elif extension in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        elif extension == '.json':
            return pd.read_json(file_path)
        elif extension == '.parquet':
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    @staticmethod
    def remove_columns_and_save(
        file_path: Path,
        columns_to_remove: List[str],
        output_dir: Path
    ) -> Tuple[str, pd.DataFrame, List[str], List[str]]:
        """
        Remove specified columns from dataset and save as new file.
        
        Args:
            file_path: Path to original dataset
            columns_to_remove: List of column names to remove
            output_dir: Directory to save the new file
            
        Returns:
            Tuple of (new_filename, dataframe, removed_columns, remaining_columns)
            
        Raises:
            ValueError: If columns don't exist in dataset
        """
        # Load dataset
        df = EDAService.load_dataset(file_path)
        
        # Get original columns
        original_columns = df.columns.tolist()
        
        # Validate columns exist
        invalid_columns = [col for col in columns_to_remove if col not in original_columns]
        if invalid_columns:
            raise ValueError(f"Columns not found in dataset: {invalid_columns}")
        
        # Remove columns
        df_cleaned = df.drop(columns=columns_to_remove, errors='ignore')
        
        # Get remaining columns
        remaining_columns = df_cleaned.columns.tolist()
        actually_removed = [col for col in columns_to_remove if col in original_columns]
        
        # Generate new filename with _eda suffix
        original_filename = file_path.stem  # filename without extension
        extension = file_path.suffix  # .csv, .xlsx, etc.
        new_filename = f"{original_filename}_eda{extension}"
        
        # Save new file
        output_path = output_dir / new_filename
        
        if extension == '.csv':
            df_cleaned.to_csv(output_path, index=False)
        elif extension in ['.xlsx', '.xls']:
            df_cleaned.to_excel(output_path, index=False)
        elif extension == '.json':
            df_cleaned.to_json(output_path, orient='records', indent=2)
        elif extension == '.parquet':
            df_cleaned.to_parquet(output_path, index=False)
        
        return new_filename, df_cleaned, actually_removed, remaining_columns
    
    def get_column_info(file_path: Path) -> Dict:
        """Get information about all columns in the dataset."""
        df = EDAService.load_dataset(file_path)
        
        column_info = []
        for col in df.columns:
            info = {
                'column_name': col,
                'data_type': str(df[col].dtype),
                'unique_count': int(df[col].nunique()),
                'missing_count': int(df[col].isnull().sum()),
                'missing_percentage': float(df[col].isnull().sum() / len(df) * 100),
                'is_numeric': bool(pd.api.types.is_numeric_dtype(df[col])),
                'sample_values': df[col].dropna().head(3).tolist()
            }
            column_info.append(info)
        
        return {
            'total_columns': len(df.columns),
            'total_rows': len(df),
            'columns': column_info
        }

    @staticmethod
    def get_overview(df: pd.DataFrame, filename: str) -> DatasetOverview:
        """Get dataset overview."""
        dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        return DatasetOverview(
            filename=filename,
            total_rows=len(df),
            total_columns=len(df.columns),
            memory_usage_mb=df.memory_usage(deep=True).sum() / 1024**2,
            duplicate_rows=df.duplicated().sum(),
            columns=df.columns.tolist(),
            dtypes=dtypes
        )
    
    @staticmethod
    def analyze_column(df: pd.DataFrame, col: str) -> ColumnStats:
        """Analyze individual column."""
        series = df[col]
        dtype = str(series.dtype)
        
        stats_obj = ColumnStats(
            column_name=col,
            data_type=dtype,
            missing_count=int(series.isna().sum()),
            missing_percentage=float(series.isna().sum() / len(series) * 100),
            unique_count=int(series.nunique())
        )
        
        # Numerical column stats
        if pd.api.types.is_numeric_dtype(series):
            stats_obj.mean = float(series.mean()) if not series.isna().all() else None
            stats_obj.median = float(series.median()) if not series.isna().all() else None
            stats_obj.std = float(series.std()) if not series.isna().all() else None
            stats_obj.min = float(series.min()) if not series.isna().all() else None
            stats_obj.max = float(series.max()) if not series.isna().all() else None
            stats_obj.q25 = float(series.quantile(0.25)) if not series.isna().all() else None
            stats_obj.q75 = float(series.quantile(0.75)) if not series.isna().all() else None
        
        # Categorical column stats
        else:
            value_counts = series.value_counts().head(10)
            stats_obj.top_values = {str(k): int(v) for k, v in value_counts.items()}
            stats_obj.mode = str(series.mode()[0]) if len(series.mode()) > 0 else None
        
        return stats_obj
    
    @staticmethod
    def get_column_stats(df: pd.DataFrame) -> List[ColumnStats]:
        """Get stats for all columns."""
        return [EDAService.analyze_column(df, col) for col in df.columns]
    
    @staticmethod
    def get_histogram_data(df: pd.DataFrame, max_columns: int = 10) -> List[HistogramData]:
        """Generate histogram data for numerical columns."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns[:max_columns]
        histograms = []
        
        for col in numerical_cols:
            series = df[col].dropna()
            
            if len(series) == 0:
                continue
            
            # Calculate optimal number of bins
            n_bins = min(int(np.ceil(np.log2(len(series)) + 1)), 50)
            
            # Create histogram
            counts, bin_edges = np.histogram(series, bins=n_bins)
            
            histograms.append(HistogramData(
                column=col,
                bins=bin_edges.tolist(),
                counts=counts.tolist(),
                mean=float(series.mean()),
                median=float(series.median()),
                std=float(series.std())
            ))
        
        return histograms
    
    @staticmethod
    def get_box_plot_data(df: pd.DataFrame, max_columns: int = 10) -> List[BoxPlotData]:
        """Generate box plot data for numerical columns."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns[:max_columns]
        box_plots = []
        
        for col in numerical_cols:
            series = df[col].dropna()
            
            if len(series) == 0:
                continue
            
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            
            box_plots.append(BoxPlotData(
                column=col,
                min=float(series.min()),
                q1=float(q1),
                median=float(series.median()),
                q3=float(q3),
                max=float(series.max()),
                outliers=outliers.tolist()[:100]
            ))
        
        return box_plots
    
    @staticmethod
    def get_bar_chart_data(df: pd.DataFrame, max_columns: int = 8) -> List[BarChartData]:
        """Generate bar chart data for categorical columns."""
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        cat_cols_to_plot = [
            col for col in categorical_cols 
            if 2 <= df[col].nunique() <= 20
        ][:max_columns]
        
        bar_charts = []
        
        for col in cat_cols_to_plot:
            value_counts = df[col].value_counts().head(15)
            total = value_counts.sum()
            
            bar_charts.append(BarChartData(
                column=col,
                categories=value_counts.index.tolist(),
                counts=value_counts.values.tolist(),
                percentages=[(count / total * 100) for count in value_counts.values]
            ))
        
        return bar_charts
    
    @staticmethod
    def get_correlation_matrix(df: pd.DataFrame) -> Optional[CorrelationMatrix]:
        """Calculate correlation matrix for numerical columns."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return None
        
        corr_matrix = df[numerical_cols].corr()
        
        high_corr = []
        for i, col1 in enumerate(corr_matrix.columns):
            for col2 in corr_matrix.columns[i+1:]:
                corr_value = corr_matrix.loc[col1, col2]
                if abs(corr_value) > 0.7:
                    high_corr.append({
                        "column1": col1,
                        "column2": col2,
                        "correlation": float(corr_value)
                    })
        
        return CorrelationMatrix(
            columns=corr_matrix.columns.tolist(),
            matrix=corr_matrix.values.tolist(),
            high_correlations=high_corr
        )
    
    @staticmethod
    def get_missing_data_matrix(df: pd.DataFrame) -> MissingDataMatrix:
        """Get missing data information."""
        missing = df.isna().sum()
        
        return MissingDataMatrix(
            columns=missing.index.tolist(),
            missing_counts=missing.values.tolist(),
            missing_percentages=[(count / len(df) * 100) for count in missing.values],
            total_rows=len(df)
        )
    
    @staticmethod
    def get_scatter_plot_data(df: pd.DataFrame, max_pairs: int = 5) -> List[ScatterPlotData]:
        """Generate scatter plot data for numerical column pairs."""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numerical_cols) < 2:
            return []
        
        scatter_plots = []
        corr_matrix = df[numerical_cols].corr()
        
        pairs = []
        for i, col1 in enumerate(corr_matrix.columns):
            for col2 in corr_matrix.columns[i+1:]:
                corr_value = abs(corr_matrix.loc[col1, col2])
                if not np.isnan(corr_value):
                    pairs.append((col1, col2, corr_value))
        
        pairs.sort(key=lambda x: x[2], reverse=True)
        top_pairs = pairs[:max_pairs]
        
        for col1, col2, corr in top_pairs:
            sample_size = min(1000, len(df))
            sample_df = df[[col1, col2]].dropna().sample(n=min(sample_size, len(df[[col1, col2]].dropna())))
            
            data_points = [
                {"x": float(row[col1]), "y": float(row[col2])}
                for _, row in sample_df.iterrows()
            ]
            
            scatter_plots.append(ScatterPlotData(
                x_column=col1,
                y_column=col2,
                data_points=data_points,
                correlation=float(corr)
            ))
        
        return scatter_plots
    
    @staticmethod
    def get_all_chart_data(df: pd.DataFrame) -> ChartDataCollection:
        """Get all chart data."""
        return ChartDataCollection(
            histograms=EDAService.get_histogram_data(df),
            box_plots=EDAService.get_box_plot_data(df),
            bar_charts=EDAService.get_bar_chart_data(df),
            correlation_matrix=EDAService.get_correlation_matrix(df),
            missing_data=EDAService.get_missing_data_matrix(df),
            scatter_plots=EDAService.get_scatter_plot_data(df)
        )
    
    @staticmethod
    def generate_insights(df: pd.DataFrame) -> List[str]:
        """Generate automated insights."""
        insights = []
        
        # Missing data insights
        missing = df.isna().sum()
        high_missing = missing[missing > len(df) * 0.5]
        if len(high_missing) > 0:
            insights.append(
                f"⚠️ {len(high_missing)} column(s) have more than 50% missing data: {', '.join(high_missing.index.tolist())}"
            )
        
        # Duplicate rows
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            insights.append(f"🔄 Found {dup_count} duplicate rows ({dup_count/len(df)*100:.1f}%)")
        
        # High cardinality columns
        for col in df.columns:
            if df[col].nunique() == len(df):
                insights.append(f"🔑 '{col}' appears to be a unique identifier")
        
        # Imbalanced categorical columns
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() < 10:
                value_counts = df[col].value_counts()
                max_ratio = value_counts.iloc[0] / len(df)
                if max_ratio > 0.8:
                    insights.append(
                        f"⚖️ '{col}' is highly imbalanced: {value_counts.index[0]} represents {max_ratio*100:.1f}%"
                    )
        
        # Numerical outliers
        for col in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > 0:
                insights.append(f"📊 '{col}' has {outliers} potential outliers ({outliers/len(df)*100:.1f}%)")
        
        # Constant columns
        constant_cols = [col for col in df.columns if df[col].nunique() == 1]
        if constant_cols:
            insights.append(f"⚡ {len(constant_cols)} column(s) have constant values: {', '.join(constant_cols)}")
        
        return insights