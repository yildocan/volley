from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.app.db import Base, SessionLocal, engine
from api.app.routers import auth, events, users
from api.app.seed import seed_users

app = FastAPI(title="Volleyball Team Matcher")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_users(db)


app.include_router(auth.router)
app.include_router(events.router)
app.include_router(users.router)
