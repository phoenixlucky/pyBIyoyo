import pandas as pd
import numpy as np
from typing import Optional, List, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    """数据处理器类，负责数据清洗、转换和预处理"""
    
    def __init__(self):
        """初始化数据处理器"""
        self.scalers = {}
        self.encoders = {}
    
    def handle_missing_values(self, df: pd.DataFrame, method: str = "删除含缺失值的行") -> pd.DataFrame:
        """
        处理缺失值
        
        Args:
            df: 输入数据框
            method: 处理方法
            
        Returns:
            pd.DataFrame: 处理后的数据框
        """
        df_processed = df.copy()
        
        if method == "删除含缺失值的行":
            df_processed = df_processed.dropna()
        
        elif method == "用均值填充":
            # 只对数值列使用均值填充
            numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                df_processed[col].fillna(df_processed[col].mean(), inplace=True)
            
            # 对非数值列使用众数填充
            non_numeric_cols = df_processed.select_dtypes(exclude=[np.number]).columns
            for col in non_numeric_cols:
                mode_value = df_processed[col].mode()
                if not mode_value.empty:
                    df_processed[col].fillna(mode_value[0], inplace=True)
        
        elif method == "用中位数填充":
            # 只对数值列使用中位数填充
            numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                df_processed[col].fillna(df_processed[col].median(), inplace=True)
            
            # 对非数值列使用众数填充
            non_numeric_cols = df_processed.select_dtypes(exclude=[np.number]).columns
            for col in non_numeric_cols:
                mode_value = df_processed[col].mode()
                if not mode_value.empty:
                    df_processed[col].fillna(mode_value[0], inplace=True)
        
        elif method == "用众数填充":
            for col in df_processed.columns:
                mode_value = df_processed[col].mode()
                if not mode_value.empty:
                    df_processed[col].fillna(mode_value[0], inplace=True)
        
        return df_processed.reset_index(drop=True)
    
    def remove_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """
        删除重复行
        
        Args:
            df: 输入数据框
            subset: 指定列的子集来判断重复
            
        Returns:
            pd.DataFrame: 去重后的数据框
        """
        return df.drop_duplicates(subset=subset).reset_index(drop=True)
    
    def remove_outliers(self, df: pd.DataFrame, columns: Optional[List[str]] = None, method: str = "iqr") -> pd.DataFrame:
        """
        移除异常值
        
        Args:
            df: 输入数据框
            columns: 要处理的列名列表，如果为None则处理所有数值列
            method: 异常值检测方法 ('iqr', 'zscore')
            
        Returns:
            pd.DataFrame: 移除异常值后的数据框
        """
        df_processed = df.copy()
        
        if columns is None:
            columns = df_processed.select_dtypes(include=[np.number]).columns.tolist()
        
        if method == "iqr":
            for col in columns:
                if col in df_processed.columns:
                    Q1 = df_processed[col].quantile(0.25)
                    Q3 = df_processed[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    df_processed = df_processed[
                        (df_processed[col] >= lower_bound) & 
                        (df_processed[col] <= upper_bound)
                    ]
        
        elif method == "zscore":
            for col in columns:
                if col in df_processed.columns:
                    z_scores = np.abs((df_processed[col] - df_processed[col].mean()) / df_processed[col].std())
                    df_processed = df_processed[z_scores < 3]
        
        return df_processed.reset_index(drop=True)
    
    def normalize_data(self, df: pd.DataFrame, columns: Optional[List[str]] = None, method: str = "standard") -> pd.DataFrame:
        """
        数据标准化/归一化
        
        Args:
            df: 输入数据框
            columns: 要标准化的列名列表
            method: 标准化方法 ('standard', 'minmax')
            
        Returns:
            pd.DataFrame: 标准化后的数据框
        """
        df_processed = df.copy()
        
        if columns is None:
            columns = df_processed.select_dtypes(include=[np.number]).columns.tolist()
        
        if method == "standard":
            scaler = StandardScaler()
        elif method == "minmax":
            scaler = MinMaxScaler()
        else:
            raise ValueError("method must be 'standard' or 'minmax'")
        
        for col in columns:
            if col in df_processed.columns:
                df_processed[col] = scaler.fit_transform(df_processed[[col]])
                self.scalers[col] = scaler
        
        return df_processed
    
    def encode_categorical(self, df: pd.DataFrame, columns: Optional[List[str]] = None, method: str = "label") -> pd.DataFrame:
        """
        分类变量编码
        
        Args:
            df: 输入数据框
            columns: 要编码的列名列表
            method: 编码方法 ('label', 'onehot')
            
        Returns:
            pd.DataFrame: 编码后的数据框
        """
        df_processed = df.copy()
        
        if columns is None:
            columns = df_processed.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if method == "label":
            for col in columns:
                if col in df_processed.columns:
                    le = LabelEncoder()
                    df_processed[col] = le.fit_transform(df_processed[col].astype(str))
                    self.encoders[col] = le
        
        elif method == "onehot":
            df_processed = pd.get_dummies(df_processed, columns=columns, prefix=columns)
        
        return df_processed
    
    def create_bins(self, df: pd.DataFrame, column: str, bins: Union[int, List], labels: Optional[List] = None) -> pd.DataFrame:
        """
        创建分箱
        
        Args:
            df: 输入数据框
            column: 要分箱的列名
            bins: 分箱数量或分箱边界
            labels: 分箱标签
            
        Returns:
            pd.DataFrame: 分箱后的数据框
        """
        df_processed = df.copy()
        
        if column in df_processed.columns:
            df_processed[f"{column}_binned"] = pd.cut(
                df_processed[column], 
                bins=bins, 
                labels=labels, 
                include_lowest=True
            )
        
        return df_processed
    
    def calculate_statistics(self, df: pd.DataFrame) -> dict:
        """
        计算数据统计信息
        
        Args:
            df: 输入数据框
            
        Returns:
            dict: 统计信息字典
        """
        stats = {}
        
        # 基本信息
        stats['basic_info'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
        
        # 数据类型统计
        stats['data_types'] = {
            'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
            'text_columns': len(df.select_dtypes(include=['object']).columns),
            'datetime_columns': len(df.select_dtypes(include=['datetime']).columns),
            'boolean_columns': len(df.select_dtypes(include=['bool']).columns)
        }
        
        # 缺失值统计
        missing_stats = df.isnull().sum()
        stats['missing_values'] = {
            'total_missing': missing_stats.sum(),
            'columns_with_missing': len(missing_stats[missing_stats > 0]),
            'missing_percentage': round((missing_stats.sum() / (len(df) * len(df.columns))) * 100, 2)
        }
        
        # 重复值统计
        stats['duplicates'] = {
            'duplicate_rows': df.duplicated().sum(),
            'duplicate_percentage': round((df.duplicated().sum() / len(df)) * 100, 2)
        }
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            stats['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        return stats
    
    def detect_data_quality_issues(self, df: pd.DataFrame) -> dict:
        """
        检测数据质量问题
        
        Args:
            df: 输入数据框
            
        Returns:
            dict: 数据质量问题报告
        """
        issues = {
            'high_missing_columns': [],
            'high_cardinality_columns': [],
            'potential_outliers': [],
            'constant_columns': [],
            'duplicate_columns': []
        }
        
        # 检测高缺失率列（超过50%）
        missing_rates = df.isnull().sum() / len(df)
        issues['high_missing_columns'] = missing_rates[missing_rates > 0.5].index.tolist()
        
        # 检测高基数分类列（唯一值超过总行数的80%）
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio > 0.8:
                issues['high_cardinality_columns'].append(col)
        
        # 检测常量列（只有一个唯一值）
        for col in df.columns:
            if df[col].nunique() <= 1:
                issues['constant_columns'].append(col)
        
        # 检测重复列
        for i, col1 in enumerate(df.columns):
            for col2 in df.columns[i+1:]:
                if df[col1].equals(df[col2]):
                    issues['duplicate_columns'].append((col1, col2))
        
        return issues
    
    def generate_data_profile(self, df: pd.DataFrame) -> dict:
        """
        生成完整的数据概况报告
        
        Args:
            df: 输入数据框
            
        Returns:
            dict: 数据概况报告
        """
        profile = {
            'statistics': self.calculate_statistics(df),
            'quality_issues': self.detect_data_quality_issues(df),
            'column_profiles': {}
        }
        
        # 为每列生成详细概况
        for col in df.columns:
            col_profile = {
                'dtype': str(df[col].dtype),
                'non_null_count': df[col].count(),
                'null_count': df[col].isnull().sum(),
                'unique_count': df[col].nunique(),
                'memory_usage': df[col].memory_usage(deep=True)
            }
            
            if df[col].dtype in ['int64', 'float64']:
                col_profile.update({
                    'mean': df[col].mean(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'median': df[col].median()
                })
            
            elif df[col].dtype == 'object':
                col_profile.update({
                    'most_frequent': df[col].mode().iloc[0] if not df[col].mode().empty else None,
                    'frequency': df[col].value_counts().iloc[0] if not df[col].value_counts().empty else 0
                })
            
            profile['column_profiles'][col] = col_profile
        
        return profile