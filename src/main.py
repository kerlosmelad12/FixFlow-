from fastapi import FastAPI
from routes import base_app
import uvicorn

app=FastAPI()

app.include_router(base_app)

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)