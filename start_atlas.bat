@echo off
echo 🚀 URL Cache API - MongoDB Atlas Version for Windows
echo =====================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found:
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing requirements...
pip install -r requirements.txt

REM Check for environment file
if exist ".env" (
    echo ✅ Environment file (.env) found
    
    REM Test MongoDB connection
    echo.
    echo 🔍 Testing MongoDB Atlas connection...
    python test_connection.py
    
    if %errorlevel% neq 0 (
        echo.
        echo ⚠️  MongoDB Atlas connection test failed
        echo Please check:
        echo 1. Your password is set correctly in .env file
        echo 2. Your IP address is whitelisted in MongoDB Atlas
        echo 3. Your internet connection is working
        echo.
        set /p continue="Do you want to continue anyway? (y/N): "
        if /I "%continue%" neq "y" (
            echo Exiting...
            pause
            exit /b 1
        )
    )
) else (
    echo ⚠️  Environment file (.env) not found
    echo.
    echo 📋 Please create a .env file with your MongoDB Atlas credentials:
    echo.
    echo MONGO_USERNAME=m220student
    echo MONGO_PASSWORD=your_actual_password_here
    echo MONGO_CLUSTER=privacy-policy.k3mlivq.mongodb.net
    echo DATABASE_NAME=url_cache_db
    echo COLLECTION_NAME=api_responses
    echo.
    set /p continue="Do you want to continue anyway? (y/N): "
    if /I "%continue%" neq "y" (
        echo Exiting...
        pause
        exit /b 1
    )
)

echo.
echo 🎯 Starting the API server...
echo =================================================
echo 🌐 API will be available at:
echo    • Main API: http://localhost:8001
echo    • API Docs: http://localhost:8001/docs  
echo    • Health Check: http://localhost:8001/health
echo    • Database Info: http://localhost:8001/api/db/info
echo    • Example: http://localhost:8001/api/fetch?url=https://jsonplaceholder.typicode.com/posts/1
echo.
echo 📝 To test the API, open new Command Prompt and run:
echo    venv\Scripts\activate
echo    python test_api_full.py
echo.
echo 🛑 To stop the server, press Ctrl+C
echo.

REM Start the Atlas version of the application
if exist "url_cache_app_atlas.py" (
    python url_cache_app_atlas.py
) else (
    echo ❌ url_cache_app_atlas.py not found
    pause
    exit /b 1
)