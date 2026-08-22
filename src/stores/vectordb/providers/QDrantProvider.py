from ..VectordbInterface import VectordbInterface
from ..VectordbEnums import DistanceMetric
from qdrant_client import models, QdrantClient
import logging
from typing import List
from qdrant_client.models import PointIdsList


class QDrantProvider(VectordbInterface):

    def __init__(self,db_path):

        self.db_path=db_path
        self.client=None
        self.logger=logging.getLogger(__name__)


    def connect(self):
        self.client=QdrantClient(path=self.db_path)


    def set_distance_metric(self,distance_metric:str):
          if distance_metric==DistanceMetric.COSINE.value:
                     self.distance=models.Distance.COSINE
          elif distance_metric==DistanceMetric.DOT.value:
                     self.distance=models.Distance.DOT
          else:
               self.distance=None
               

    def disconnect(self):
       self.client=None

    
    def is_collection_exist(self,collection_name:str) ->bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self)  ->List:
        return self.client.get_collections()

    

    def get_collection_info(self, collection_name: str) -> dict:
        if not self.is_collection_exist(collection_name=collection_name):
            self.logger.error("The collection Not found")
            return None
        return self.client.get_collection(collection_name=collection_name)

    

    def delete_collection(self,collection_name:str) :
        if not self.is_collection_exist(collection_name=collection_name):
                self.logger.error("The collection Not found")
                

        self.client.delete_collection(collection_name=collection_name)
        return True

    def delete_point(self, collection_name: str, record_id):
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(
                    points=[record_id]
                ),
            )
            return True

        except Exception:
            self.logger.exception(
                "Error while deleting point %s from %s",
                record_id,
                collection_name,
            )
            return False


    def create_collection(self,collection_name:str
                              ,vector_size:int
                              ,do_reset:bool=False):
        if do_reset==True:
            _=self.delete_collection(collection_name)


        if not self.is_collection_exist(collection_name=collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=self.distance,
                    datatype=models.Datatype.UINT8,
                ),
            )
            return True

        return False

    def insert_one(self, collection_name: str, text: str, vector: list,
                             metadata: dict = None, 
                            record_id: str= None):
        if not self.is_collection_exist(collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
          
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=record_id,
                        vector=vector,
                        payload={
                            "text": text, "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting batch: {e}")
            return False

        return True
   
    def insert_many(self, collection_name: str, texts: list, 
                         vectors: list, metadata: list = None, 
                         record_ids: list = None, batch_size: int = 50):

        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):
            end_batch = i + batch_size
            batch_vectors = vectors[i:end_batch]
            batch_texts = texts[i:end_batch]
            batch_metadatas = metadata[i:end_batch]
            batch_recordids = record_ids[i:end_batch]



            records = [
                models.Record(
                    id=batch_recordids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x], "metadata": batch_metadatas[x]
                    }
                )
                for x in range(len(batch_texts))
            ]

            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=records)
            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

        return True
    
    def search_by_vector(self, collection_name: str, vector: list, limit: int):
         results= self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

         if results is None or len(results)==0:
              return None

         return results
            
        