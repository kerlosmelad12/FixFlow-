from fastapi import FastAPI
from routes import base_app,data_app
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from helper.config import get_settings
from controllers import LLMService
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    logger.info("Application startup initiated.")

    try:
        LLMService.get_langchain_pipeline()
        logger.info("LLM loaded successfully.")
    except Exception as e:
        logger.exception(f"Failed to load LLM: {e}")

    try:
        settings = get_settings()

        app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)
        app.db_client = app.mongo_conn[settings.DB_NAME]

        logger.info("MongoDB connected successfully.")
    except Exception as e:
        logger.exception(f"Failed to connect to MongoDB: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("Application shutdown")
    try:
       app.mongo_conn.close()
    except Exception as e:
        logger.exception(f"Failed to close MongoDB: {e}")
        raise




app.include_router(base_app)
app.include_router(data_app)

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)