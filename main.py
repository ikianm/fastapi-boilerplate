from fastapi import FastAPI
from .routers import auth, todos, admin, users
from .database import engine, Base

app = FastAPI()

Base.metadata.create_all(engine)


@app.get('/health')
async def health_check():
    return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(admin.router)