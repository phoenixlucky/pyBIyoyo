import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from typing import Optional, List, Union
import warnings
warnings.filterwarnings('ignore')

class ChartGenerator:
    """图表生成器类，负责创建各种类型的可视化图表"""
    
    def __init__(self):
        """初始化图表生成器"""
        # 设置默认颜色主题
        self.color_palette = px.colors.qualitative.Set3
        self.template = "plotly_white"
    
    def create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                        color_col: Optional[str] = None, title: Optional[str] = None) -> go.Figure:
        """
        创建柱状图
        
        Args:
            df: 数据框
            x_col: X轴列名
            y_col: Y轴列名
            color_col: 颜色分组列名
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = f"{y_col} 按 {x_col} 分组的柱状图"
        
        # 如果x轴是数值类型，先进行分组聚合
        if df[x_col].dtype in ['int64', 'float64'] and color_col is None:
            # 对数值型x轴进行分组
            df_grouped = df.groupby(x_col)[y_col].sum().reset_index()
            fig = px.bar(df_grouped, x=x_col, y=y_col, title=title, template=self.template)
        else:
            fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title, template=self.template)
        
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=True if color_col else False,
            height=500
        )
        
        return fig
    
    def create_line_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                         color_col: Optional[str] = None, title: Optional[str] = None) -> go.Figure:
        """
        创建折线图
        
        Args:
            df: 数据框
            x_col: X轴列名
            y_col: Y轴列名
            color_col: 颜色分组列名
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = f"{y_col} 随 {x_col} 变化的折线图"
        
        # 按x轴排序
        df_sorted = df.sort_values(x_col)
        
        fig = px.line(df_sorted, x=x_col, y=y_col, color=color_col, 
                     title=title, template=self.template, markers=True)
        
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=True if color_col else False,
            height=500
        )
        
        return fig
    
    def create_scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str, 
                           color_col: Optional[str] = None, size_col: Optional[str] = None,
                           title: Optional[str] = None) -> go.Figure:
        """
        创建散点图
        
        Args:
            df: 数据框
            x_col: X轴列名
            y_col: Y轴列名
            color_col: 颜色分组列名
            size_col: 点大小列名
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = f"{y_col} vs {x_col} 散点图"
        
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col,
                        title=title, template=self.template, hover_data=df.columns)
        
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=True if color_col else False,
            height=500
        )
        
        return fig
    
    def create_pie_chart(self, df: pd.DataFrame, names_col: str, values_col: str,
                        title: Optional[str] = None) -> go.Figure:
        """
        创建饼图
        
        Args:
            df: 数据框
            names_col: 分类列名
            values_col: 数值列名
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = f"{names_col} 分布饼图"
        
        # 聚合数据
        df_agg = df.groupby(names_col)[values_col].sum().reset_index()
        
        fig = px.pie(df_agg, names=names_col, values=values_col, title=title, template=self.template)
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=500)
        
        return fig
    
    def create_histogram(self, df: pd.DataFrame, col: str, bins: int = 30,
                        title: Optional[str] = None) -> go.Figure:
        """
        创建直方图
        
        Args:
            df: 数据框
            col: 列名
            bins: 分箱数量
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = f"{col} 分布直方图"
        
        fig = px.histogram(df, x=col, nbins=bins, title=title, template=self.template)
        
        fig.update_layout(
            xaxis_title=col,
            yaxis_title="频次",
            height=500
        )
        
        return fig
    
    def create_box_plot(self, df: pd.DataFrame, y_col: str, x_col: Optional[str] = None,
                       title: Optional[str] = None) -> go.Figure:
        """
        创建箱线图
        
        Args:
            df: 数据框
            y_col: Y轴列名
            x_col: X轴分组列名（可选）
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = f"{y_col} 箱线图"
        
        fig = px.box(df, x=x_col, y=y_col, title=title, template=self.template)
        
        fig.update_layout(
            xaxis_title=x_col if x_col else "",
            yaxis_title=y_col,
            height=500
        )
        
        return fig
    
    def create_heatmap(self, df: pd.DataFrame, title: Optional[str] = None) -> go.Figure:
        """
        创建相关性热力图
        
        Args:
            df: 数据框
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = "相关性热力图"
        
        # 只选择数值列
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            raise ValueError("数据中没有数值列，无法创建相关性热力图")
        
        correlation_matrix = numeric_df.corr()
        
        fig = px.imshow(correlation_matrix, 
                       text_auto=True, 
                       aspect="auto",
                       title=title,
                       template=self.template,
                       color_continuous_scale="RdBu_r")
        
        fig.update_layout(height=600)
        
        return fig
    
    def create_area_chart(self, df: pd.DataFrame, x_col: str, y_col: str,
                         color_col: Optional[str] = None, title: Optional[str] = None) -> go.Figure:
        """
        创建面积图
        
        Args:
            df: 数据框
            x_col: X轴列名
            y_col: Y轴列名
            color_col: 颜色分组列名
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = f"{y_col} 随 {x_col} 变化的面积图"
        
        # 按x轴排序
        df_sorted = df.sort_values(x_col)
        
        fig = px.area(df_sorted, x=x_col, y=y_col, color=color_col,
                     title=title, template=self.template)
        
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            showlegend=True if color_col else False,
            height=500
        )
        
        return fig
    
    def create_radar_chart(self, df: pd.DataFrame, columns: List[str], 
                          group_col: Optional[str] = None, title: Optional[str] = None) -> go.Figure:
        """
        创建雷达图
        
        Args:
            df: 数据框
            columns: 要显示的列名列表
            group_col: 分组列名
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = "雷达图"
        
        fig = go.Figure()
        
        if group_col and group_col in df.columns:
            # 按组创建多个雷达图
            for group in df[group_col].unique():
                group_data = df[df[group_col] == group]
                values = group_data[columns].mean().tolist()
                values.append(values[0])  # 闭合雷达图
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=columns + [columns[0]],
                    fill='toself',
                    name=str(group)
                ))
        else:
            # 单个雷达图
            values = df[columns].mean().tolist()
            values.append(values[0])  # 闭合雷达图
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=columns + [columns[0]],
                fill='toself',
                name='数据'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([df[col].max() for col in columns])]
                )
            ),
            showlegend=True,
            title=title,
            template=self.template,
            height=500
        )
        
        return fig
    
    def create_violin_plot(self, df: pd.DataFrame, y_col: str, x_col: Optional[str] = None,
                          title: Optional[str] = None) -> go.Figure:
        """
        创建小提琴图
        
        Args:
            df: 数据框
            y_col: Y轴列名
            x_col: X轴分组列名（可选）
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = f"{y_col} 小提琴图"
        
        fig = px.violin(df, x=x_col, y=y_col, title=title, template=self.template, box=True)
        
        fig.update_layout(
            xaxis_title=x_col if x_col else "",
            yaxis_title=y_col,
            height=500
        )
        
        return fig
    
    def create_sunburst_chart(self, df: pd.DataFrame, path_cols: List[str], 
                             values_col: str, title: Optional[str] = None) -> go.Figure:
        """
        创建旭日图
        
        Args:
            df: 数据框
            path_cols: 层级路径列名列表
            values_col: 数值列名
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = "旭日图"
        
        fig = px.sunburst(df, path=path_cols, values=values_col, 
                         title=title, template=self.template)
        
        fig.update_layout(height=600)
        
        return fig
    
    def create_treemap(self, df: pd.DataFrame, path_cols: List[str], 
                      values_col: str, title: Optional[str] = None) -> go.Figure:
        """
        创建树状图
        
        Args:
            df: 数据框
            path_cols: 层级路径列名列表
            values_col: 数值列名
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = "树状图"
        
        fig = px.treemap(df, path=path_cols, values=values_col,
                        title=title, template=self.template)
        
        fig.update_layout(height=600)
        
        return fig
    
    def create_parallel_coordinates(self, df: pd.DataFrame, columns: List[str],
                                   color_col: Optional[str] = None, 
                                   title: Optional[str] = None) -> go.Figure:
        """
        创建平行坐标图
        
        Args:
            df: 数据框
            columns: 要显示的列名列表
            color_col: 颜色列名
            title: 图表标题
            
        Returns:
            go.Figure: Plotly图表对象
        """
        if title is None:
            title = "平行坐标图"
        
        fig = px.parallel_coordinates(df, dimensions=columns, color=color_col,
                                     title=title, template=self.template)
        
        fig.update_layout(height=600)
        
        return fig
    
    def create_dashboard(self, df: pd.DataFrame, chart_configs: List[dict]) -> go.Figure:
        """
        创建仪表板（多子图）
        
        Args:
            df: 数据框
            chart_configs: 图表配置列表
            
        Returns:
            go.Figure: Plotly图表对象
        """
        n_charts = len(chart_configs)
        
        # 计算子图布局
        if n_charts <= 2:
            rows, cols = 1, n_charts
        elif n_charts <= 4:
            rows, cols = 2, 2
        else:
            rows = int(np.ceil(n_charts / 3))
            cols = 3
        
        # 创建子图
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=[config.get('title', f'图表 {i+1}') for i, config in enumerate(chart_configs)]
        )
        
        for i, config in enumerate(chart_configs):
            row = i // cols + 1
            col = i % cols + 1
            
            chart_type = config.get('type', 'scatter')
            
            if chart_type == 'scatter':
                fig.add_trace(
                    go.Scatter(x=df[config['x']], y=df[config['y']], mode='markers'),
                    row=row, col=col
                )
            elif chart_type == 'bar':
                fig.add_trace(
                    go.Bar(x=df[config['x']], y=df[config['y']]),
                    row=row, col=col
                )
            elif chart_type == 'line':
                fig.add_trace(
                    go.Scatter(x=df[config['x']], y=df[config['y']], mode='lines'),
                    row=row, col=col
                )
        
        fig.update_layout(
            height=300 * rows,
            showlegend=False,
            title_text="数据分析仪表板",
            template=self.template
        )
        
        return fig