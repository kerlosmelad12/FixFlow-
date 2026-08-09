from fastapi import FastAPI
from routes import base_app,data_app,nlp_app
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from helper.config import get_settings
import logging
from stores.llm.LLMFactory import LLMFactory
from stores.classifiers.ClassiferFactory import ClassiferFactory
from stores.vectordb.VectordbFactory import VectordbFactory
from stores.llm.LLMEnums import LLMbackend
from stores.classifiers.ClassificationEnums import ClassificationEnums
from stores.vectordb.VectordbEnums import VectordbEnums
from templetes.Templete_parser import Templete_parser



logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
app = FastAPI()

@app.on_event("startup")
async def startup_application():
    #inilize the LLM, Classifier and VectorDB and settings
    settings = get_settings()
    llm_factory = LLMFactory(config=settings)
    classifier_factory = ClassiferFactory(config=settings)
    vectordb_factory = VectordbFactory(config=settings)

    logger.info("Application startup initiated.")

    app.embedding=llm_factory.create(provider=settings.EMBEDDING_BACKEND)

    logger.info("Embedding model loaded successfully.")

    

    app.generation=llm_factory.create(provider=settings.GENERATION_BACKEND)

    logger.info("Generation model loaded successfully.")



    app.classifier=classifier_factory.create(provider=settings.CLASSIFIER_BACKEND)

    app.classifier.load_model()
    app.classifier.load_label_encoder()
    app.classifier.load_text_encoder()

    logger.info("Classifier model loaded successfully.")



    app.vectordb=vectordb_factory.create(provider=settings.VECTOR_STORE_BACKEND)
    app.vectordb.set_distance_metric(distance_metric=settings.DISTANCE_METRIC)

    app.vectordb.connect()
    

    logger.info("VectorDB model loaded successfully.")
   

    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)
    app.db_client = app.mongo_conn[settings.DB_NAME]

    app.templete_parser=Templete_parser(lang=settings.PRIMARY_LANGUAGE,default_lang=settings.DEFAULT_LANGUAGE)



@app.on_event("shutdown")
async def shutdown_application():
       app.mongo_conn.close()





app.include_router(base_app)
app.include_router(data_app)
app.include_router(nlp_app)

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True)