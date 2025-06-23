import pandas as pd
import streamlit as st
from typing import Optional, Union
import io

class DataLoader:
    """数据加载器类，负责从各种数据源加载数据"""
    
    def __init__(self):
        """初始化数据加载器"""
        pass
    
    def load_excel(self, file_path: Union[str, io.BytesIO], sheet_name: str = 0) -> pd.DataFrame:
        """
        加载Excel文件数据
        
        Args:
            file_path: Excel文件路径或文件对象
            sheet_name: 工作表名称或索引
            
        Returns:
            pd.DataFrame: 加载的数据
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # 数据清理：去除完全空白的行和列
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # 重置索引
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            raise Exception(f"Excel文件加载失败: {str(e)}")
    
    def load_csv(self, file_path: Union[str, io.BytesIO], encoding: str = 'utf-8') -> pd.DataFrame:
        """
        加载CSV文件数据
        
        Args:
            file_path: CSV文件路径或文件对象
            encoding: 文件编码格式
            
        Returns:
            pd.DataFrame: 加载的数据
        """
        try:
            # 尝试不同的分隔符
            separators = [',', ';', '\t', '|']
            
            for sep in separators:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, sep=sep)
                    
                    # 如果只有一列，可能分隔符不对，继续尝试
                    if len(df.columns) > 1:
                        break
                except:
                    continue
            else:
                # 如果所有分隔符都失败，使用默认逗号分隔符
                df = pd.read_csv(file_path, encoding=encoding)
            
            # 数据清理：去除完全空白的行和列
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # 重置索引
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            raise Exception(f"CSV文件加载失败: {str(e)}")
    
    def get_excel_sheets(self, file_path: Union[str, io.BytesIO]) -> list:
        """
        获取Excel文件中的所有工作表名称
        
        Args:
            file_path: Excel文件路径或文件对象
            
        Returns:
            list: 工作表名称列表
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            raise Exception(f"获取Excel工作表失败: {str(e)}")
    
    def validate_data(self, df: pd.DataFrame) -> dict:
        """
        验证数据质量
        
        Args:
            df: 要验证的数据框
            
        Returns:
            dict: 数据质量报告
        """
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'numeric_columns': len(df.select_dtypes(include=['number']).columns),
            'text_columns': len(df.select_dtypes(include=['object']).columns),
            'datetime_columns': len(df.select_dtypes(include=['datetime']).columns),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
        
        return report
    
    def auto_detect_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        自动检测并转换数据类型
        
        Args:
            df: 输入数据框
            
        Returns:
            pd.DataFrame: 类型转换后的数据框
        """
        df_converted = df.copy()
        
        for col in df_converted.columns:
            # 尝试转换为数值类型
            if df_converted[col].dtype == 'object':
                # 尝试转换为数值
                try:
                    df_converted[col] = pd.to_numeric(df_converted[col], errors='ignore')
                except:
                    pass
                
                # 尝试转换为日期时间
                if df_converted[col].dtype == 'object':
                    try:
                        df_converted[col] = pd.to_datetime(df_converted[col], errors='ignore')
                    except:
                        pass
        
        return df_converted
    
    def sample_data(self, df: pd.DataFrame, sample_size: int = 1000, random_state: int = 42) -> pd.DataFrame:
        """
        对大数据集进行采样
        
        Args:
            df: 输入数据框
            sample_size: 采样大小
            random_state: 随机种子
            
        Returns:
            pd.DataFrame: 采样后的数据框
        """
        if len(df) <= sample_size:
            return df
        
        return df.sample(n=sample_size, random_state=random_state).reset_index(drop=True)