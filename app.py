import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder
import io
import warnings
warnings.filterwarnings('ignore')

# 导入自定义模块
from utils.data_loader import DataLoader
from utils.data_processor import DataProcessor
from utils.chart_generator import ChartGenerator
from utils.database_connector import DatabaseConnector

# 页面配置
st.set_page_config(
    page_title="BI数据分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """主函数"""
    # 标题
    st.markdown('<h1 class="main-header">📊 BI数据分析平台</h1>', unsafe_allow_html=True)
    
    # 侧边栏菜单
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/1f77b4/ffffff?text=BI+Platform", width=200)
        
        selected = option_menu(
            menu_title="主菜单",
            options=["数据导入", "数据预览", "数据分析", "图表展示", "报表导出"],
            icons=["upload", "table", "graph-up", "bar-chart", "download"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee"
                },
                "nav-link-selected": {"background-color": "#1f77b4"},
            }
        )
    
    # 初始化session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    
    # 根据选择的菜单显示不同页面
    if selected == "数据导入":
        show_data_import_page()
    elif selected == "数据预览":
        show_data_preview_page()
    elif selected == "数据分析":
        show_data_analysis_page()
    elif selected == "图表展示":
        show_chart_display_page()
    elif selected == "报表导出":
        show_report_export_page()

def show_data_import_page():
    """数据导入页面"""
    st.header("📥 数据导入")
    
    # 数据源选择
    data_source = st.selectbox(
        "选择数据源类型",
        ["Excel文件", "CSV文件", "MySQL数据库", "PostgreSQL数据库", "SQLite数据库"]
    )
    
    data_loader = DataLoader()
    
    if data_source in ["Excel文件", "CSV文件"]:
        uploaded_file = st.file_uploader(
            f"上传{data_source}",
            type=['xlsx', 'xls', 'csv'] if data_source == "Excel文件" else ['csv']
        )
        
        if uploaded_file is not None:
            try:
                if data_source == "Excel文件":
                    # Excel文件处理
                    excel_file = pd.ExcelFile(uploaded_file)
                    sheet_names = excel_file.sheet_names
                    
                    if len(sheet_names) > 1:
                        selected_sheet = st.selectbox("选择工作表", sheet_names)
                    else:
                        selected_sheet = sheet_names[0]
                    
                    st.session_state.data = data_loader.load_excel(uploaded_file, selected_sheet)
                else:
                    # CSV文件处理
                    encoding = st.selectbox("选择编码", ["utf-8", "gbk", "gb2312"])
                    st.session_state.data = data_loader.load_csv(uploaded_file, encoding)
                
                st.success(f"✅ 数据加载成功！共{len(st.session_state.data)}行，{len(st.session_state.data.columns)}列")
                
                # 显示数据预览
                st.subheader("数据预览")
                st.dataframe(st.session_state.data.head(10))
                
            except Exception as e:
                st.error(f"❌ 数据加载失败：{str(e)}")
    
    else:
        # 数据库连接
        st.subheader("数据库连接配置")
        
        col1, col2 = st.columns(2)
        with col1:
            host = st.text_input("主机地址", value="localhost")
            port = st.number_input("端口", value=3306 if "MySQL" in data_source else 5432)
        
        with col2:
            database = st.text_input("数据库名")
            username = st.text_input("用户名")
        
        password = st.text_input("密码", type="password")
        
        if st.button("连接数据库"):
            try:
                db_connector = DatabaseConnector()
                connection = db_connector.connect(
                    db_type=data_source.split("数据库")[0].lower(),
                    host=host,
                    port=port,
                    database=database,
                    username=username,
                    password=password
                )
                
                if connection:
                    st.success("✅ 数据库连接成功！")
                    
                    # 获取表列表
                    tables = db_connector.get_tables(connection)
                    selected_table = st.selectbox("选择数据表", tables)
                    
                    if st.button("加载数据"):
                        st.session_state.data = db_connector.load_table_data(connection, selected_table)
                        st.success(f"✅ 数据加载成功！共{len(st.session_state.data)}行，{len(st.session_state.data.columns)}列")
                        st.dataframe(st.session_state.data.head(10))
                
            except Exception as e:
                st.error(f"❌ 数据库连接失败：{str(e)}")

def show_data_preview_page():
    """数据预览页面"""
    st.header("👀 数据预览")
    
    if st.session_state.data is None:
        st.warning("⚠️ 请先在数据导入页面加载数据")
        return
    
    data = st.session_state.data
    
    # 数据基本信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f'<div class="metric-card"><h3>📊 总行数</h3><h2>{len(data):,}</h2></div>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f'<div class="metric-card"><h3>📋 总列数</h3><h2>{len(data.columns)}</h2></div>',
            unsafe_allow_html=True
        )
    
    with col3:
        missing_values = data.isnull().sum().sum()
        st.markdown(
            f'<div class="metric-card"><h3>❓ 缺失值</h3><h2>{missing_values:,}</h2></div>',
            unsafe_allow_html=True
        )
    
    with col4:
        duplicates = data.duplicated().sum()
        st.markdown(
            f'<div class="metric-card"><h3>🔄 重复行</h3><h2>{duplicates:,}</h2></div>',
            unsafe_allow_html=True
        )
    
    # 数据表格显示
    st.subheader("📋 数据表格")
    
    # 分页显示
    page_size = st.selectbox("每页显示行数", [10, 25, 50, 100], index=1)
    total_pages = (len(data) - 1) // page_size + 1
    page_number = st.number_input("页码", min_value=1, max_value=total_pages, value=1)
    
    start_idx = (page_number - 1) * page_size
    end_idx = min(start_idx + page_size, len(data))
    
    st.write(f"显示第 {start_idx + 1} - {end_idx} 行，共 {len(data)} 行")
    
    # 使用AgGrid显示数据
    gb = GridOptionsBuilder.from_dataframe(data.iloc[start_idx:end_idx])
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
    gridOptions = gb.build()
    
    AgGrid(
        data.iloc[start_idx:end_idx],
        gridOptions=gridOptions,
        enable_enterprise_modules=True,
        height=400
    )
    
    # 数据类型信息
    st.subheader("📊 数据类型信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**列信息**")
        info_df = pd.DataFrame({
            '列名': data.columns,
            '数据类型': data.dtypes.astype(str),
            '非空值数量': data.count(),
            '缺失值数量': data.isnull().sum()
        })
        st.dataframe(info_df)
    
    with col2:
        st.write("**数值列统计**")
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            st.dataframe(data[numeric_cols].describe())
        else:
            st.info("没有数值类型的列")

def show_data_analysis_page():
    """数据分析页面"""
    st.header("🔍 数据分析")
    
    if st.session_state.data is None:
        st.warning("⚠️ 请先在数据导入页面加载数据")
        return
    
    data = st.session_state.data
    processor = DataProcessor()
    
    # 数据处理选项
    st.subheader("🛠️ 数据处理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 缺失值处理
        st.write("**缺失值处理**")
        missing_action = st.selectbox(
            "选择处理方式",
            ["不处理", "删除含缺失值的行", "用均值填充", "用中位数填充", "用众数填充"]
        )
    
    with col2:
        # 重复值处理
        st.write("**重复值处理**")
        duplicate_action = st.selectbox(
            "选择处理方式",
            ["不处理", "删除重复行"]
        )
    
    if st.button("应用数据处理"):
        processed_data = data.copy()
        
        # 处理缺失值
        if missing_action != "不处理":
            processed_data = processor.handle_missing_values(processed_data, missing_action)
        
        # 处理重复值
        if duplicate_action == "删除重复行":
            processed_data = processor.remove_duplicates(processed_data)
        
        st.session_state.processed_data = processed_data
        st.success("✅ 数据处理完成！")
        
        # 显示处理前后对比
        col1, col2 = st.columns(2)
        with col1:
            st.write("**处理前**")
            st.write(f"行数: {len(data)}")
            st.write(f"缺失值: {data.isnull().sum().sum()}")
            st.write(f"重复行: {data.duplicated().sum()}")
        
        with col2:
            st.write("**处理后**")
            st.write(f"行数: {len(processed_data)}")
            st.write(f"缺失值: {processed_data.isnull().sum().sum()}")
            st.write(f"重复行: {processed_data.duplicated().sum()}")
    
    # 使用处理后的数据进行分析
    analysis_data = st.session_state.processed_data if st.session_state.processed_data is not None else data
    
    # 相关性分析
    st.subheader("📈 相关性分析")
    
    numeric_cols = analysis_data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        correlation_matrix = analysis_data[numeric_cols].corr()
        
        fig = px.imshow(
            correlation_matrix,
            text_auto=True,
            aspect="auto",
            title="变量相关性热力图",
            color_continuous_scale="RdBu_r"
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("需要至少2个数值列才能进行相关性分析")
    
    # 分布分析
    st.subheader("📊 分布分析")
    
    if len(numeric_cols) > 0:
        selected_col = st.selectbox("选择要分析的数值列", numeric_cols)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 直方图
            fig = px.histogram(
                analysis_data,
                x=selected_col,
                title=f"{selected_col} 分布直方图",
                nbins=30
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 箱线图
            fig = px.box(
                analysis_data,
                y=selected_col,
                title=f"{selected_col} 箱线图"
            )
            st.plotly_chart(fig, use_container_width=True)

def show_chart_display_page():
    """图表展示页面"""
    st.header("📊 图表展示")
    
    if st.session_state.data is None:
        st.warning("⚠️ 请先在数据导入页面加载数据")
        return
    
    data = st.session_state.processed_data if st.session_state.processed_data is not None else st.session_state.data
    chart_generator = ChartGenerator()
    
    # 图表类型选择
    chart_type = st.selectbox(
        "选择图表类型",
        ["柱状图", "折线图", "散点图", "饼图", "面积图", "雷达图"]
    )
    
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if chart_type == "柱状图":
        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("X轴（分类变量）", categorical_cols + numeric_cols)
        with col2:
            y_col = st.selectbox("Y轴（数值变量）", numeric_cols)
        
        if x_col and y_col:
            fig = chart_generator.create_bar_chart(data, x_col, y_col)
            st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "折线图":
        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("X轴", numeric_cols + categorical_cols)
        with col2:
            y_col = st.selectbox("Y轴", numeric_cols)
        
        if x_col and y_col:
            fig = chart_generator.create_line_chart(data, x_col, y_col)
            st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "散点图":
        col1, col2, col3 = st.columns(3)
        with col1:
            x_col = st.selectbox("X轴", numeric_cols)
        with col2:
            y_col = st.selectbox("Y轴", numeric_cols)
        with col3:
            color_col = st.selectbox("颜色分组（可选）", ["无"] + categorical_cols)
        
        if x_col and y_col:
            color_col = None if color_col == "无" else color_col
            fig = chart_generator.create_scatter_plot(data, x_col, y_col, color_col)
            st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "饼图":
        col1, col2 = st.columns(2)
        with col1:
            names_col = st.selectbox("分类列", categorical_cols)
        with col2:
            values_col = st.selectbox("数值列（可选）", ["计数"] + numeric_cols)
        
        if names_col:
            if values_col == "计数":
                pie_data = data[names_col].value_counts().reset_index()
                pie_data.columns = [names_col, 'count']
                fig = chart_generator.create_pie_chart(pie_data, names_col, 'count')
            else:
                fig = chart_generator.create_pie_chart(data, names_col, values_col)
            st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "面积图":
        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("X轴", numeric_cols + categorical_cols)
        with col2:
            y_col = st.selectbox("Y轴", numeric_cols)
        
        if x_col and y_col:
            fig = chart_generator.create_area_chart(data, x_col, y_col)
            st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "雷达图":
        if len(numeric_cols) >= 3:
            selected_cols = st.multiselect(
                "选择要显示的数值列（至少3个）",
                numeric_cols,
                default=numeric_cols[:5] if len(numeric_cols) >= 5 else numeric_cols
            )
            
            if len(selected_cols) >= 3:
                fig = chart_generator.create_radar_chart(data, selected_cols)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("请至少选择3个数值列")
        else:
            st.warning("雷达图需要至少3个数值列")

def show_report_export_page():
    """报表导出页面"""
    st.header("📤 报表导出")
    
    if st.session_state.data is None:
        st.warning("⚠️ 请先在数据导入页面加载数据")
        return
    
    data = st.session_state.processed_data if st.session_state.processed_data is not None else st.session_state.data
    
    st.subheader("📋 数据导出")
    
    # 导出格式选择
    export_format = st.selectbox(
        "选择导出格式",
        ["CSV", "Excel", "JSON"]
    )
    
    # 导出选项
    col1, col2 = st.columns(2)
    
    with col1:
        export_all = st.checkbox("导出全部数据", value=True)
        if not export_all:
            start_row = st.number_input("起始行", min_value=0, max_value=len(data)-1, value=0)
            end_row = st.number_input("结束行", min_value=start_row+1, max_value=len(data), value=min(1000, len(data)))
    
    with col2:
        selected_columns = st.multiselect(
            "选择要导出的列（留空则导出全部列）",
            data.columns.tolist()
        )
    
    # 准备导出数据
    export_data = data.copy()
    
    if not export_all:
        export_data = export_data.iloc[start_row:end_row]
    
    if selected_columns:
        export_data = export_data[selected_columns]
    
    # 生成下载按钮
    if export_format == "CSV":
        csv_data = export_data.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下载CSV文件",
            data=csv_data,
            file_name=f"data_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    elif export_format == "Excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            export_data.to_excel(writer, sheet_name='数据', index=False)
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 下载Excel文件",
            data=excel_data,
            file_name=f"data_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    elif export_format == "JSON":
        json_data = export_data.to_json(orient='records', force_ascii=False, indent=2)
        st.download_button(
            label="📥 下载JSON文件",
            data=json_data,
            file_name=f"data_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # 显示导出预览
    st.subheader("👀 导出预览")
    st.write(f"将导出 {len(export_data)} 行，{len(export_data.columns)} 列")
    st.dataframe(export_data.head(10))
    
    # 数据统计报告
    st.subheader("📊 数据统计报告")
    
    report_data = {
        "总行数": len(data),
        "总列数": len(data.columns),
        "数值列数量": len(data.select_dtypes(include=[np.number]).columns),
        "文本列数量": len(data.select_dtypes(include=['object']).columns),
        "缺失值总数": data.isnull().sum().sum(),
        "重复行数量": data.duplicated().sum(),
        "数据大小(MB)": round(data.memory_usage(deep=True).sum() / 1024 / 1024, 2)
    }
    
    report_df = pd.DataFrame(list(report_data.items()), columns=['指标', '值'])
    st.table(report_df)

if __name__ == "__main__":
    main()