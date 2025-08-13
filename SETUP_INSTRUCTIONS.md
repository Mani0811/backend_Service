# URL Cache API - Complete File List & Setup Instructions

## 📁 Complete File Structure

```
url-cache-api/
├── .env                           # MongoDB Atlas credentials
├── requirements.txt               # Python dependencies  
├── url_cache_app_atlas.py        # Main FastAPI application
├── test_connection.py             # MongoDB connection test
├── test_api_full.py              # Complete API test suite
├── start_atlas.bat               # Windows startup script
├── README.md                     # Setup guide
├── sample_requests.py            # Usage examples
├── privacy_analysis_test.py      # Privacy analysis demo
└── SETUP_INSTRUCTIONS.md         # This file
```

## 🚀 Complete Setup Instructions

### 1. Download All Files
Save each of the files above with the exact names shown.

### 2. Your MongoDB Atlas URI
You provided: `mongodb+srv://m220student:<db_password>@privacy-policy.k3mlivq.mongodb.net/?retryWrites=true&w=majority&appName=privacy-policy`

### 3. Quick Setup Steps

**Step 1: Create project folder**
```cmd
mkdir url-cache-api
cd url-cache-api
```

**Step 2: Save all the provided files in this folder**

**Step 3: Edit the .env file**
Replace `your_password_here` with your actual MongoDB Atlas password:
```
MONGO_USERNAME=m220student
MONGO_PASSWORD=your_actual_password_here
MONGO_CLUSTER=privacy-policy.k3mlivq.mongodb.net
DATABASE_NAME=url_cache_db
COLLECTION_NAME=api_responses
```

**Important:** If your password contains special characters (@, :, /, ?, &, etc.), URL-encode them:
- @ becomes %40
- : becomes %3A  
- / becomes %2F
- ? becomes %3F
- & becomes %26
- + becomes %2B
- = becomes %3D
- % becomes %25

**Step 4: Run the automated setup**
```cmd
start_atlas.bat
```

This will:
- Create virtual environment
- Install dependencies
- Test MongoDB connection
- Start the API server

### 4. Manual Setup (Alternative)

If the batch script doesn't work:

```cmd
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test MongoDB connection
python test_connection.py

# Start the API server
python url_cache_app_atlas.py
```

### 5. Test the API

**In a new terminal:**
```cmd
venv\Scripts\activate
python test_api_full.py
```

### 6. Usage Examples

**Test basic caching:**
```cmd
curl "http://localhost:8001/api/fetch?url=https://jsonplaceholder.typicode.com/posts/1"
```

**Test privacy analysis format:**
```cmd
python privacy_analysis_test.py
```

**Interactive API docs:**
```
http://localhost:8001/docs
```

## 🔧 Troubleshooting

### Common Issues:

1. **"Cannot connect to MongoDB"**
   - Check your password in .env file
   - Verify IP whitelist in MongoDB Atlas
   - URL-encode special characters in password

2. **"Python not found"**
   - Install Python 3.8+ from python.org
   - Make sure "Add to PATH" is checked during installation

3. **"Port 8000 in use"**
   - Kill the process or use different port:
   - `uvicorn url_cache_app_atlas:app --port 8001`

4. **"Module not found"**
   - Make sure virtual environment is activated
   - Run: python -m venv venv
    - Run:venv\Scripts\activate
   - Run: pip install -r requirements_atlas.txt
    - Run: python url_cache_app_atlas.py
   - Run: `pip install -r requirements.txt`

## 📊 Features

- ✅ **Complete URL caching** in MongoDB Atlas
- ✅ **Privacy analysis response support** 
- ✅ **Fast cache retrieval** from cloud database
- ✅ **Health monitoring** and statistics
- ✅ **Cache management** (clear all, clear specific)
- ✅ **Interactive API documentation**
- ✅ **Comprehensive testing suite**

## 🌐 Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/fetch?url=URL` - Cache URL response
- `GET /api/cache/stats` - Cache statistics  
- `GET /api/db/info` - Database information
- `DELETE /api/cache/clear` - Clear all cache
- `DELETE /api/cache/url?url=URL` - Clear specific URL

## 🎯 Privacy Analysis Ready

Your privacy analysis response format with:
- Cookie analysis (before/after consent)
- Network request tracking  
- Banner analysis
- Domain registration data
- All metadata and model information

**Will be cached perfectly** with complete data integrity!

## 📞 Support

After setup, if you need help:
1. Check the troubleshooting section above
2. Run `python test_connection.py` to verify MongoDB
3. Check logs in the API server output
4. View interactive docs at `/docs` endpoint

## 🎉 You're Ready!

Once set up, your URL Cache API will:
- Cache any API response in MongoDB Atlas
- Return cached responses instantly 
- Preserve complete data integrity
- Scale with MongoDB Atlas cloud infrastructure
- Work perfectly with privacy analysis responses

Happy caching! 🚀