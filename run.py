import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 Memulai {settings.APP_NAME}...")
    print(f"📍 Akses Swagger UI di: http://localhost:{settings.APP_PORT}/docs")
    print(f"📍 API Base URL: http://{settings.APP_HOST}:{settings.APP_PORT}\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG
    )
