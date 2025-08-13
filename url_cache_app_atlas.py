# URL Cache API - FastAPI Web Application (MongoDB Atlas Version)
import os
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
import requests
import hashlib
from datetime import datetime
from typing import Optional
import json
import urllib.parse
from pydantic import BaseModel

from privacy_compliance_scorer import PrivacyComplianceScorer


# Initialize FastAPI app
app = FastAPI(title="URL Cache API", description="Cache API responses in MongoDB Atlas")

class AnalyzeRequest(BaseModel):
    url: str

# MongoDB Atlas connection configuration
# Load from environment variables or use defaults
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "m220student")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "your_password_here")  
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER", "privacy-policy.k3mlivq.mongodb.net")
DATABASE_NAME = os.getenv("DATABASE_NAME", "url_cache_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "api_responses")

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
    # Reload variables after loading .env
    MONGO_USERNAME = os.getenv("MONGO_USERNAME", MONGO_USERNAME)
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", MONGO_PASSWORD)
    MONGO_CLUSTER = os.getenv("MONGO_CLUSTER", MONGO_CLUSTER)
    DATABASE_NAME = os.getenv("DATABASE_NAME", DATABASE_NAME)
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", COLLECTION_NAME)
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables or defaults.")

# Construct MongoDB Atlas connection string
def get_mongo_connection_string():
    """Construct MongoDB Atlas connection string with credentials"""
    # URL encode the username and password to handle special characters
    username = urllib.parse.quote_plus(MONGO_USERNAME)
    password = urllib.parse.quote_plus(MONGO_PASSWORD)
    
    # MongoDB Atlas SRV connection string format
    # Based on your provided URI: mongodb+srv://m220student:<db_password>@privacy-policy.k3mlivq.mongodb.net/?retryWrites=true&w=majority&appName=privacy-policy
    connection_string = f"mongodb+srv://{username}:{password}@{MONGO_CLUSTER}/?retryWrites=true&w=majority&appName=url-cache-api"
    
    return connection_string

# Initialize MongoDB client with Atlas connection
try:
    connection_string = get_mongo_connection_string()
    print(f"🔗 Connecting to: mongodb+srv://{MONGO_USERNAME}:***@{MONGO_CLUSTER}/...")
    
    client = MongoClient(connection_string)
    
    # Test the connection
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
    
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    # Print connection details
    server_info = client.server_info()
    print(f"📊 MongoDB Version: {server_info.get('version')}")
    print(f"📂 Database: {DATABASE_NAME}")
    print(f"📄 Collection: {COLLECTION_NAME}")
    
except Exception as e:
    print(f"❌ Failed to connect to MongoDB Atlas: {e}")
    print("Please check your credentials and connection string")
    print(f"Username: {MONGO_USERNAME}")
    print(f"Cluster: {MONGO_CLUSTER}")
    print("Make sure to replace 'your_password_here' in .env file with your actual password")
    client = None
    db = None
    collection = None

def create_url_hash(url: str) -> str:
    """Create a hash of the URL for use as MongoDB document ID"""
    return hashlib.sha256(url.encode()).hexdigest()

def make_api_call(url: str) -> dict:
    """Make HTTP GET request to the provided URL"""
    try:
        endpoint = "http://127.0.0.1:8000/analyze_cookies"
        payload={"url": url}
        response = requests.post(endpoint, json=payload, timeout=300)
        print("response",response)
        response.raise_for_status()
        
        # Try to parse as JSON, otherwise return text
        try:
            data = response.json()
        except:
            data = {"text_response": response.text, "status_code": response.status_code}
        
        return {
            "success": True,
            "data": data,
            "status_code": response.status_code,
            "headers": dict(response.headers)
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    connection_status = "✅ Connected" if client else "❌ Not Connected"
    return {
        "message": "URL Cache API (MongoDB Atlas)",
        "description": "Use /api/fetch?url=<your_url> to fetch and cache API responses",
        "example": "/api/fetch?url=https://jsonplaceholder.typicode.com/posts/1",
        "database_status": connection_status,
        "database_name": DATABASE_NAME,
        "collection_name": COLLECTION_NAME,
        "cluster": MONGO_CLUSTER,
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if client:
            # Test database connection
            client.admin.command('ping')
            db_status = "healthy"
            
            # Get additional connection info
            server_info = client.server_info()
            db_stats = db.command("dbStats")
            
        else:
            db_status = "disconnected"
            server_info = {}
            db_stats = {}
    except Exception as e:
        db_status = f"error: {str(e)}"
        server_info = {}
        db_stats = {}
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
        "cluster": MONGO_CLUSTER,
        "database_name": DATABASE_NAME,
        "mongodb_version": server_info.get("version", "unknown"),
        "database_size_mb": round(db_stats.get("dataSize", 0) / (1024 * 1024), 2) if db_stats else 0
    }

@app.post("/api/fetch")
async def fetch_url_data(body: AnalyzeRequest):
    """
    Main endpoint that:
    1. Checks if URL response exists in MongoDB Atlasclera
    2. If exists, returns cached response
    3. If not exists, makes API call, saves to MongoDB Atlas, and returns response
    """
    
    # Check if MongoDB is connected
   

    try:
        url = body.url
        print(f"Fetching cached_response")
        query = {"url": url}
        # Check if URL exists in MongoDB Atlas
        cached_response = collection.find_one(query)
        
        if cached_response:
            # URL found in cache
            scorer = PrivacyComplianceScorer(cached_response.get("api_response"))
            score = scorer.calculate_score()
            return {
                "privacy_score": score,
                "source": "cache",
                "url": url,
                "cached_at": cached_response.get("cached_at"),
                "api_response": cached_response.get("api_response"),
            }
        
        # URL not in cache - make API call
        api_response = make_api_call(url)
        
        if not api_response["success"]:
            raise HTTPException(
                status_code=api_response.get("status_code", 500),
                detail=f"Failed to fetch data from URL: {api_response.get('error')}"
            )
        scorer = PrivacyComplianceScorer(api_response)
        score = scorer.calculate_score()
        # Save response to MongoDB Atlas
        document = {
            "_id": url,
            "url": url,
            "api_response": api_response,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        try:
            collection.insert_one(document)
        except Exception as e:
            # If MongoDB insert fails, still return the API response
            return {
                "source": "api_call_only",
                "url": url,
                "api_response": api_response,
                "warning": f"Failed to cache response in Atlas: {str(e)}"
            }
        
        # Return the fresh API responses
        return {
            "privacy_score": score,
            "source": "fresh_api_call",
            "url": url,
            "cached_at": document["cached_at"],
            "api_response": api_response
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database operation failed: {str(e)}"
        )

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get statistics about cached URLs"""
    if not collection:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        total_cached = collection.count_documents({})
        recent_cached = collection.find().sort("cached_at", -1).limit(5)
        
        recent_urls = []
        for doc in recent_cached:
            recent_urls.append({
                "url": doc.get("url"),
                "cached_at": doc.get("cached_at")
            })
        
        # Get database statistics
        db_stats = db.command("dbStats")
        
        return {
            "total_cached_urls": total_cached,
            "recent_cached_urls": recent_urls,
            "database_info": {
                "cluster": MONGO_CLUSTER,
                "database": DATABASE_NAME,
                "collection": COLLECTION_NAME,
                "database_size_mb": round(db_stats.get("dataSize", 0) / (1024 * 1024), 2),
                "document_count": db_stats.get("objects", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")

@app.delete("/api/cache/clear")
async def clear_cache():
    """Clear all cached responses"""
    if not collection:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        result = collection.delete_many({})
        return {
            "message": f"Cache cleared successfully. Deleted {result.deleted_count} documents from Atlas.",
            "deleted_count": result.deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@app.delete("/api/cache/url")
async def clear_url_cache(url: str = Query(..., description="The URL to remove from cache")):
    """Clear cache for a specific URL"""
    if not collection:
        raise HTTPException(status_code=503, detail="Database not available")
    
    url_hash = create_url_hash(url)
    
    try:
        result = collection.delete_one({"_id": url_hash})
        if result.deleted_count == 0:
            return {"message": f"URL not found in cache: {url}"}
        else:
            return {"message": f"Successfully removed URL from Atlas cache: {url}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove URL from cache: {str(e)}")

@app.get("/api/db/info")
async def get_database_info():
    """Get MongoDB Atlas database information"""
    if not client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        # Get database stats
        db_stats = db.command("dbStats")
        server_info = client.server_info()
        
        return {
            "connection_status": "connected",
            "cluster": MONGO_CLUSTER,
            "database_name": DATABASE_NAME,
            "collection_name": COLLECTION_NAME,
            "mongodb_version": server_info.get("version"),
            "database_size_mb": round(db_stats.get("dataSize", 0) / (1024 * 1024), 2),
            "document_count": db_stats.get("objects", 0),
            "indexes": db_stats.get("indexes", 0),
            "storage_size_mb": round(db_stats.get("storageSize", 0) / (1024 * 1024), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get database info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 URL Cache API with MongoDB Atlas")
    print("="*60)
    print(f"Database: {DATABASE_NAME}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Cluster: {MONGO_CLUSTER}")
    print("="*60)
    
    if client:
        print("✅ MongoDB Atlas connection successful")
    else:
        print("❌ MongoDB Atlas connection failed")
        print("Please check your credentials in the .env file")
        print("Make sure to replace 'your_password_here' with your actual password")
    
    print("\n🌐 Starting server on http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🏥 Health Check: http://localhost:801/health")
    print("📊 Database Info: http://localhost:8001/api/db/info")
    print("\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)