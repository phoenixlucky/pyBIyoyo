@echo off
chcp 65001 >nul
SETLOCAL

REM ========== 配置 ==========
set ENV_NAME=pyBIyo_env
set PY_VER=3.11
set PROJECT_DIR=D:\home\pyBIyoyo
set REQUIREMENTS=requirements.txt
set MARKER_FILE=%PROJECT_DIR%\.deps_installed
REM ==========================

REM 检查 Conda 是否存在
where conda >nul 2>&1
if errorlevel 1 (
    echo ❌ Conda 未安装，请先安装 Anaconda 或 Miniconda。
    pause
    exit /b 1
)

REM 接受 ToS（手动逐个 channel）
call conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
call conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
call conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2

REM 检查环境是否存在
call conda env list | findstr /R /C:"%ENV_NAME%" >nul
if errorlevel 1 (
    echo ⚠️ 未发现环境 [%ENV_NAME%]，正在创建新环境...
    call conda create -y -n %ENV_NAME% python=%PY_VER%
) else (
    echo ✅ 环境 [%ENV_NAME%] 已存在。
)

REM 激活环境
call conda activate %ENV_NAME%

REM 切换到项目目录
cd /D %PROJECT_DIR%

REM 安装依赖（仅第一次或 marker 文件不存在）
if not exist %MARKER_FILE% (
    echo 🔧 安装依赖中...
    pip install -r %REQUIREMENTS%
    if errorlevel 1 (
        echo ❌ 依赖安装失败，请检查 %REQUIREMENTS%
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
    type nul > %MARKER_FILE%
) else (
    echo 📦 已检测到依赖安装过，跳过安装。
)

REM 启动 Streamlit
echo 🚀 启动 Streamlit 应用...
streamlit run app.py

REM 保持窗口
pause
ENDLOCAL
