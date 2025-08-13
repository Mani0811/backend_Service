# URL Cache API - Complete MongoDB Atlas Setup

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ installed
- Internet connection
- Your MongoDB Atlas password

### 📁 Project Structure
```
url-cache-api/
├── .env                           # Your MongoDB credentials
├── requirements.txt               # Python dependencies
├── url_cache_app_atlas.py        # Main FastAPI application
├── test_connection.py             # Test MongoDB connection
├── test_api_full.py              # Complete API test suite
├── start_atlas.bat               # Windows startup script
├── README.md                     # This file
└── examples/
    ├── sample_requests.py         # Usage examples
    └── privacy_response_test.py   # Privacy analysis testing
```

## 🔧 Installation Steps

### Step 1: Set Up Environment
1. **Create project folder:**
   ```cmd
   mkdir url-cache-api
   cd url-cache-api
   ```

2. **Create virtual environment:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

### Step 2: Configure MongoDB Atlas
1. **Create `.env` file** with your credentials:
   ```
   MONGO_USERNAME=m220student
   MONGO_PASSWORD=your_actual_password_here
   MONGO_CLUSTER=privacy-policy.k3mlivq.mongodb.net
   DATABASE_NAME=url_cache_db
   COLLECTION_NAME=api_responses
   ```

2. **Replace `your_actual_password_here`** with your real MongoDB Atlas password

### Step 3: Test Connection
```cmd
python test_connection.py
```
If successful, you should see: ✅ MongoDB Atlas connection successful!

### Step 4: Start the API
```cmd
python url_cache_app_atlas.py
```

### Step 5: Test the API
Open new terminal:
```cmd
venv\Scripts\activate
python test_api_full.py
```

## 🌐 API Endpoints

- **Main API**: http://localhost:8001
- **Interactive Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Cache URL**: http://localhost:8001/api/fetch?url=YOUR_URL
- **Cache Stats**: http://localhost:8001/api/cache/stats
- **Database Info**: http://localhost:8001/api/db/info

## 🧪 Quick Test Examples

### Test Regular API Caching:
```bash
curl "http://localhost:8001/api/fetch?url=https://jsonplaceholder.typicode.com/posts/1"
```

### Test Privacy Analysis Response:
```bash
curl "http://localhost:8001/api/fetch?url=https://privacy-api.com/analyze?url=https://stackoverflow.com"
```

### Check Cache Statistics:
```bash
curl "http://localhost:8001/api/cache/stats"
```

## 🔍 Troubleshooting

### Connection Issues:
- Check your internet connection
- Verify MongoDB Atlas credentials in `.env`
- Ensure your IP is whitelisted in Atlas Network Access
- Check if password contains special characters (URL encode if needed)

### Port Issues:
- If port 8000 is busy, modify the port in `url_cache_app_atlas.py`
- Or run: `uvicorn url_cache_app_atlas:app --port 8001`

### Python Issues:
- Ensure Python 3.8+ is installed
- Make sure virtual environment is activated
- Check all dependencies are installed: `pip list`

## 📊 MongoDB Atlas Dashboard
- View your cached data at: https://cloud.mongodb.com
- Database: `url_cache_db`
- Collection: `api_responses`

## 🛠️ Development Commands

```bash
# Start development server with auto-reload
uvicorn url_cache_app_atlas:app --reload

# Clear all cached data
curl -X DELETE "http://localhost:8001/api/cache/clear"

# Remove specific URL from cache
curl -X DELETE "http://localhost:8001/api/cache/url?url=YOUR_URL"

# View detailed logs
python url_cache_app_atlas.py --debug
```

## 📝 Notes

- All API responses are cached exactly as received
- Privacy analysis responses work perfectly with this system
- Cache keys are SHA256 hashes of the URLs
- MongoDB Atlas free tier provides 512MB storage
- Connection string uses SRV format for automatic server discovery

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your MongoDB Atlas setup
3. Test with the provided test scripts
4. Check the API documentation at `/docs` endpoint

Happy caching! 🚀