from fastapi import FastAPI
import uvicorn
from api.routes.users import router as users_router
from db.database import engine, Base


app = FastAPI()
app.include_router(users_router)
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
