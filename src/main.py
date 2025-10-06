from fastapi import FastAPI
from src.core.db import Base,engine
from src.users.routers import router as users_router
app = FastAPI()


from fastapi import FastAPI
app = FastAPI(title="Rover Backend Developer")

Base.metadata.create_all(bind=engine)

app.include_router(users_router)