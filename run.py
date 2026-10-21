import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 Memulai {settings.APP_NAME}...")
    print(f"💬 Web Chat UI Interaktif: http://localhost:{settings.APP_PORT}/chat")
    print(f"📖 Swagger UI Docs: http://localhost:{settings.APP_PORT}/docs")
    print(f"🩺 Health Check: http://localhost:{settings.APP_PORT}/api/v1/health\n")
    
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG
    )

