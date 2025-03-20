from fastapi import FastAPI
from routers import auth, todos
from database import engine, Base

app = FastAPI()

Base.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(todos.router)

