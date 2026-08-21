from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import base_app, data_app, nlp_app
import uvicorn
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from helper.config import get_settings
from stores.llm.LLMFactory import LLMFactory
from stores.classifiers.ClassiferFactory import ClassiferFactory
from stores.vectordb.VectordbFactory import VectordbFactory
from stores.templetes.Templete_parser import Templete_parser
from stores.Cache.RedisCacheController import RedisCacheController


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- Startup ----
    settings = get_settings()

    llm_factory = LLMFactory(config=settings)
    classifier_factory = ClassiferFactory(config=settings)
    vectordb_factory = VectordbFactory(config=settings)

    logger.info("Application startup initiated.")

    # Embedding
    app.embedding = llm_factory.create(
        provider=settings.EMBEDDING_BACKEND
    )
    logger.info("Embedding model loaded successfully.")

    # Redis
    app.redis_conn = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )
    app.redis = RedisCacheController(
        redis_client=app.redis_conn
    )
    logger.info("Redis cache connected successfully.")

    # Generation LLM
    app.generation = llm_factory.create(
        provider=settings.GENERATION_BACKEND
    )
    logger.info("Generation model loaded successfully.")

    # Classifier
    app.classifier = classifier_factory.create(
        provider=settings.CLASSIFIER_BACKEND
    )
    app.classifier.load_model()
    app.classifier.load_label_encoder()
    app.classifier.load_text_encoder()
    logger.info("Classifier model loaded successfully.")

    # Vector DB
    app.vectordb = vectordb_factory.create(
        provider=settings.VECTOR_STORE_BACKEND
    )
    app.vectordb.set_distance_metric(
        distance_metric=settings.DISTANCE_METRIC
    )
    app.vectordb.connect()
    logger.info("VectorDB connected successfully.")

    # MongoDB
    app.mongo_conn = AsyncIOMotorClient(
        settings.MONGODB_URI
    )
    app.db_client = app.mongo_conn[settings.DB_NAME]

    # Template parser
    app.templete_parser = Templete_parser(
        lang=settings.PRIMARY_LANGUAGE,
        default_lang=settings.DEFAULT_LANGUAGE
    )

    logger.info("Application startup completed.")

    yield  # <-- app runs while paused here

    # ---- Shutdown ----
    app.mongo_conn.close()
    await app.redis_conn.close()
    logger.info("Application shutdown completed.")


app = FastAPI(
    title="FixFlow API",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(base_app)
app.include_router(data_app)
app.include_router(nlp_app)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )