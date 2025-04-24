from fastapi import FastAPI
from utils.database import engine
import utils.models as models
from routers import auth, todos, admin
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


origins = [
    "http://localhost:3000",
    "http://localhost:8501",
    "http://localhost:8080",
    # Add other origins as needed
]

# Allow frontend (React) to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/health/")
def heath_check():
    return {"Status":"Healthy"}


models.Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)