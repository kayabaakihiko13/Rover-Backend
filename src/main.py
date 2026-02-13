from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.core.auth import Base,engine
from src.core.config import settings
from src.users.routers import router as users_router
from src.posts.routers import router as posts_router


# initial app
app = FastAPI(title="Rover Backend Developer",
              version="0.0.1")

# initial database
Base.metadata.create_all(bind=engine)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_FE_DEV],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers = [settings.CORS_FE_METHODS]
)

# Router Section
app.include_router(users_router)
app.include_router(posts_router)

app.mount("/uploads", StaticFiles(directory="uploads"),
           name="uploads")

@app.get("/health")
def health_check():
    return {"status": "ok"}

