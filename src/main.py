from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.core.db import Base,engine
from src.core.config import settings
from src.users.routers import router as users_router
from src.posts.routers import router as posts_router




## initial limiter 
# limiter = Limiter(key_func=get_remote_address,default_limits=["1/minute"])

# initial app
app = FastAPI(title="Rover Backend Developer",
              version="0.0.1")

# initial database
Base.metadata.create_all(bind=engine)

# limiter setup
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# app.add_middleware(SlowAPIMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_FE_DEV],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# Router Section
app.include_router(users_router)
app.include_router(posts_router)

app.mount("/uploads", StaticFiles(directory="uploads"),
           name="uploads")

@app.get("/health")
def health_check():
    return {"status": "ok"}

