import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text
from typing import Optional, List, Dict, Any
import pymysql
import sqlite3
import warnings
warnings.filterwarnings('ignore')

class DatabaseConnector:
    """数据库连接器类，负责连接和操作各种数据库"""
    
    def __init__(self):
        """初始化数据库连接器"""
        self.engine = None
        self.connection = None
    
    def connect(self, db_type: str, host: str = 'localhost', port: int = 3306,
               database: str = '', username: str = '', password: str = '',
               **kwargs) -> Optional[sa.engine.Engine]:
        """
        连接数据库
        
        Args:
            db_type: 数据库类型 ('mysql', 'postgresql', 'sqlite')
            host: 主机地址
            port: 端口号
            database: 数据库名
            username: 用户名
            password: 密码
            **kwargs: 其他连接参数
            
        Returns:
            sqlalchemy.engine.Engine: 数据库引擎对象
        """
        try:
            if db_type.lower() == 'mysql':
                connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            
            elif db_type.lower() == 'postgresql':
                connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
            
            elif db_type.lower() == 'sqlite':
                connection_string = f"sqlite:///{database}"
            
            else:
                raise ValueError(f"不支持的数据库类型: {db_type}")
            
            # 创建引擎
            self.engine = create_engine(connection_string, **kwargs)
            
            # 测试连接
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            return self.engine
            
        except Exception as e:
            raise Exception(f"数据库连接失败: {str(e)}")
    
    def get_tables(self, engine: Optional[sa.engine.Engine] = None) -> List[str]:
        """
        获取数据库中的所有表名
        
        Args:
            engine: 数据库引擎对象
            
        Returns:
            List[str]: 表名列表
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            raise ValueError("请先连接数据库")
        
        try:
            inspector = sa.inspect(engine)
            return inspector.get_table_names()
        except Exception as e:
            raise Exception(f"获取表列表失败: {str(e)}")
    
    def get_table_info(self, table_name: str, engine: Optional[sa.engine.Engine] = None) -> Dict[str, Any]:
        """
        获取表的详细信息
        
        Args:
            table_name: 表名
            engine: 数据库引擎对象
            
        Returns:
            Dict[str, Any]: 表信息字典
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            raise ValueError("请先连接数据库")
        
        try:
            inspector = sa.inspect(engine)
            
            # 获取列信息
            columns = inspector.get_columns(table_name)
            
            # 获取主键
            primary_keys = inspector.get_pk_constraint(table_name)['constrained_columns']
            
            # 获取外键
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            # 获取索引
            indexes = inspector.get_indexes(table_name)
            
            return {
                'columns': columns,
                'primary_keys': primary_keys,
                'foreign_keys': foreign_keys,
                'indexes': indexes
            }
            
        except Exception as e:
            raise Exception(f"获取表信息失败: {str(e)}")
    
    def load_table_data(self, table_name: str, engine: Optional[sa.engine.Engine] = None,
                       limit: Optional[int] = None, where_clause: Optional[str] = None) -> pd.DataFrame:
        """
        从表中加载数据
        
        Args:
            table_name: 表名
            engine: 数据库引擎对象
            limit: 限制返回行数
            where_clause: WHERE条件子句
            
        Returns:
            pd.DataFrame: 数据框
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            raise ValueError("请先连接数据库")
        
        try:
            # 构建SQL查询
            query = f"SELECT * FROM {table_name}"
            
            if where_clause:
                query += f" WHERE {where_clause}"
            
            if limit:
                query += f" LIMIT {limit}"
            
            # 执行查询
            df = pd.read_sql(query, engine)
            
            return df
            
        except Exception as e:
            raise Exception(f"加载表数据失败: {str(e)}")
    
    def execute_query(self, query: str, engine: Optional[sa.engine.Engine] = None) -> pd.DataFrame:
        """
        执行自定义SQL查询
        
        Args:
            query: SQL查询语句
            engine: 数据库引擎对象
            
        Returns:
            pd.DataFrame: 查询结果
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            raise ValueError("请先连接数据库")
        
        try:
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            raise Exception(f"执行查询失败: {str(e)}")
    
    def save_to_database(self, df: pd.DataFrame, table_name: str, 
                        engine: Optional[sa.engine.Engine] = None,
                        if_exists: str = 'replace', index: bool = False) -> bool:
        """
        将数据框保存到数据库表
        
        Args:
            df: 要保存的数据框
            table_name: 目标表名
            engine: 数据库引擎对象
            if_exists: 如果表存在时的处理方式 ('fail', 'replace', 'append')
            index: 是否保存索引
            
        Returns:
            bool: 是否保存成功
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            raise ValueError("请先连接数据库")
        
        try:
            df.to_sql(table_name, engine, if_exists=if_exists, index=index)
            return True
        except Exception as e:
            raise Exception(f"保存数据到数据库失败: {str(e)}")
    
    def get_table_row_count(self, table_name: str, engine: Optional[sa.engine.Engine] = None) -> int:
        """
        获取表的行数
        
        Args:
            table_name: 表名
            engine: 数据库引擎对象
            
        Returns:
            int: 行数
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            raise ValueError("请先连接数据库")
        
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = pd.read_sql(query, engine)
            return result['count'].iloc[0]
        except Exception as e:
            raise Exception(f"获取表行数失败: {str(e)}")
    
    def get_column_statistics(self, table_name: str, column_name: str,
                             engine: Optional[sa.engine.Engine] = None) -> Dict[str, Any]:
        """
        获取列的统计信息
        
        Args:
            table_name: 表名
            column_name: 列名
            engine: 数据库引擎对象
            
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            raise ValueError("请先连接数据库")
        
        try:
            query = f"""
            SELECT 
                COUNT(*) as total_count,
                COUNT({column_name}) as non_null_count,
                COUNT(DISTINCT {column_name}) as unique_count,
                MIN({column_name}) as min_value,
                MAX({column_name}) as max_value
            FROM {table_name}
            """
            
            result = pd.read_sql(query, engine)
            
            stats = {
                'total_count': result['total_count'].iloc[0],
                'non_null_count': result['non_null_count'].iloc[0],
                'null_count': result['total_count'].iloc[0] - result['non_null_count'].iloc[0],
                'unique_count': result['unique_count'].iloc[0],
                'min_value': result['min_value'].iloc[0],
                'max_value': result['max_value'].iloc[0]
            }
            
            return stats
            
        except Exception as e:
            raise Exception(f"获取列统计信息失败: {str(e)}")
    
    def create_table_from_dataframe(self, df: pd.DataFrame, table_name: str,
                                   engine: Optional[sa.engine.Engine] = None,
                                   dtype_mapping: Optional[Dict[str, str]] = None) -> bool:
        """
        根据数据框创建数据库表
        
        Args:
            df: 数据框
            table_name: 表名
            engine: 数据库引擎对象
            dtype_mapping: 数据类型映射字典
            
        Returns:
            bool: 是否创建成功
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            raise ValueError("请先连接数据库")
        
        try:
            # 如果提供了数据类型映射，使用它
            if dtype_mapping:
                df.to_sql(table_name, engine, if_exists='replace', index=False, dtype=dtype_mapping)
            else:
                df.to_sql(table_name, engine, if_exists='replace', index=False)
            
            return True
            
        except Exception as e:
            raise Exception(f"创建表失败: {str(e)}")
    
    def backup_table(self, table_name: str, backup_table_name: str,
                    engine: Optional[sa.engine.Engine] = None) -> bool:
        """
        备份表
        
        Args:
            table_name: 源表名
            backup_table_name: 备份表名
            engine: 数据库引擎对象
            
        Returns:
            bool: 是否备份成功
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            raise ValueError("请先连接数据库")
        
        try:
            query = f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name}"
            
            with engine.connect() as conn:
                conn.execute(text(query))
                conn.commit()
            
            return True
            
        except Exception as e:
            raise Exception(f"备份表失败: {str(e)}")
    
    def drop_table(self, table_name: str, engine: Optional[sa.engine.Engine] = None) -> bool:
        """
        删除表
        
        Args:
            table_name: 表名
            engine: 数据库引擎对象
            
        Returns:
            bool: 是否删除成功
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            raise ValueError("请先连接数据库")
        
        try:
            query = f"DROP TABLE IF EXISTS {table_name}"
            
            with engine.connect() as conn:
                conn.execute(text(query))
                conn.commit()
            
            return True
            
        except Exception as e:
            raise Exception(f"删除表失败: {str(e)}")
    
    def close_connection(self):
        """
        关闭数据库连接
        """
        if self.engine:
            self.engine.dispose()
            self.engine = None
    
    def test_connection(self, engine: Optional[sa.engine.Engine] = None) -> bool:
        """
        测试数据库连接
        
        Args:
            engine: 数据库引擎对象
            
        Returns:
            bool: 连接是否正常
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            return False
        
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except:
            return False
    
    def get_database_info(self, engine: Optional[sa.engine.Engine] = None) -> Dict[str, Any]:
        """
        获取数据库信息
        
        Args:
            engine: 数据库引擎对象
            
        Returns:
            Dict[str, Any]: 数据库信息字典
        """
        if engine is None:
            engine = self.engine
        
        if engine is None:
            raise ValueError("请先连接数据库")
        
        try:
            info = {
                'database_type': engine.dialect.name,
                'database_version': None,
                'tables': self.get_tables(engine),
                'table_count': len(self.get_tables(engine))
            }
            
            # 尝试获取数据库版本
            try:
                with engine.connect() as conn:
                    if engine.dialect.name == 'mysql':
                        result = conn.execute(text("SELECT VERSION() as version"))
                    elif engine.dialect.name == 'postgresql':
                        result = conn.execute(text("SELECT version() as version"))
                    elif engine.dialect.name == 'sqlite':
                        result = conn.execute(text("SELECT sqlite_version() as version"))
                    else:
                        result = None
                    
                    if result:
                        info['database_version'] = result.fetchone()[0]
            except:
                pass
            
            return info
            
        except Exception as e:
            raise Exception(f"获取数据库信息失败: {str(e)}")