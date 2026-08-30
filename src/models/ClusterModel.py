from bson import ObjectId
from .DataBaseModel import DataBaseModel
from models.DB_Schema.Cluster import Cluster
from .Enums.CollectionValues import CollectionValues


class ClusterModel(DataBaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.Cluster_Collection = self.db_client[CollectionValues.CLUSTERS.value]

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if CollectionValues.CLUSTERS.value not in all_collections:
            self.Cluster_Collection = self.db_client[CollectionValues.CLUSTERS.value]
            indexes = Cluster.get_indexes()
            for index in indexes:
                await self.Cluster_Collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index.get("unique", False)
                )

    @classmethod
    async def create_instance(cls, db_client):
        instance = cls(db_client)
        await instance.init_collection()
        return instance


    async def insert_cluster(self, cluster: Cluster):

        result = await self.Cluster_Collection.insert_one(
            cluster.model_dump(
                by_alias=True,
                exclude_none=True
            )
        )

        cluster.id = result.inserted_id
        return cluster

    
    async def get_data_by_cluster(self, cluster_name: str):

        result = await self.Cluster_Collection.find_one(
            {"cluster_name": cluster_name}
        )

        if result is None:
            return None

        return Cluster(**result)

    async def get_or_create_cluster(self, cluster: Cluster, error_id: str):

        result = await self.Cluster_Collection.find_one(
            {"cluster_name": cluster.cluster_name}
        )

        object_id = ObjectId(error_id)

        if result is None:
            cluster.error_ids.append(object_id)
            cluster.error_counts = 1

            return await self.insert_cluster(cluster)

        result = Cluster.model_validate(result)

        if object_id not in result.error_ids:
            result.error_ids.append(object_id)
            result.error_counts += 1

            await self.Cluster_Collection.update_one(
                {"_id": result.id},
                {
                    "$set": {
                        "error_ids": result.error_ids,
                        "error_counts": result.error_counts,
                    }
                }
            )

        return result

    async def delete_by_error_id(self, error_id: str):

        error_object_id = ObjectId(error_id)

        result = await self.ClusterCollection.delete_one(
            {
                "error_id": error_object_id
            }
        )

        return result.deleted_count