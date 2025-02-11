from fastapi import FastAPI
from database import engine
import models
from routers import auth, todos


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


app.include_router(auth.route)
app.include_router(todos.router)
