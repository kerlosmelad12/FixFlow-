from models.DB_Schema.Cluster import Cluster
from .ProcessController import ProcessController
from stores.llm.LLMEnums import ChatRoles
from .extraction_parsing import parse_extraction_output
from models.DB_Schema.ErrorMessage import ErrorMessage
from .WebscearchController import WebscearchController
from models.DB_Schema.ErrorMessage import ErrorMessage
from models.DB_Schema.Weabscearch import WeabscearchSearchResponse
import json
from models.DB_Schema.Weabscearch import RetriveSimiler
from models.DB_Schema.Weabscearch import WeabscearchAnswers
from models.DB_Schema.Weabscearch import WeabscearchQuestion
from models.DB_Schema.ProcessingJob import ProcessingJob
from models.Enums.JobProcessingEnums import JobProcessingEnums


class NlpController:
    def __init__(self, embedding_client: object,generation_client: object,
                 vector_store_client: object,classifier_client: object,templete_client: object):
        super().__init__()
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.vector_store_client = vector_store_client
        self.classifier_client = classifier_client
        self.templete_parser = templete_client
        self.process_controller = ProcessController()
        self.WebscearchController=WebscearchController(scearch_backend="stackoverflow")
        self.vector_store_client.create_collection(
        collection_name=self.creater_collection_name(),
        vector_size=self.embedding_client.embedding_size
    )


    @classmethod
    def creater_collection_name(cls):
         return "web_search_cache"

    def reset_web_cache(self):

        self.vector_store_client.create_collection(
            collection_name=self.creater_collection_name(),
            vector_size=self.embedding_client.embedding_size,
            do_reset=True
        )
    
    def classify_text(self, text: str):
        result = self.classifier_client.predict(text)
        
        if not result:
            return Cluster(cluster_name="Other")

        top_label = max(result, key=result.get)
        top_score = result[top_label]

        return Cluster(cluster_name=top_label, cluster_score=top_score)

    def extract_error_details(self, text: str):

        cleaned_text = self.process_controller.clean_text(text)
        extraction_system_prompt = self.templete_parser.get("Feature_extraction", "EXTRACTION_SYSTEM_PROMPT")
        extraction_instructions = self.templete_parser.get("Feature_extraction", "EXTRACTION_INSTRUCTIONS_TEMPLATE")
        examples = self.templete_parser.get("Feature_extraction", "EXAMPLES_TEMPLATE")

        system_prompt = "\n\n".join([
            str(extraction_system_prompt),
            str(extraction_instructions),
            str(examples),
        ])

        user_prompt = self.templete_parser.get("Feature_extraction", "USER_PROMPT_TEMPLATE", {"cleaned_text": cleaned_text})

        system_prompt=self.generation_client.construct_prompt(ChatRoles.SYSTEM.value, system_prompt)

        llm_result = self.generation_client.generate(promot=user_prompt, messages=[system_prompt])

      

        if not llm_result:
            return {"success": False, "error": None, "data": None, "cleaned_text": cleaned_text}

        parser_result = parse_extraction_output(llm_result)
        parser_result["cleaned_text"] = cleaned_text
        return parser_result

    
    def rank_similar_web_results(self,query_text: str, results: WeabscearchSearchResponse, min_similarity: float = 0.4):
        if not results or not results.results:
            return []

    
        query_embedding = self.embedding_client.embed(query_text)

        scored = []

        collection_name = self.creater_collection_name()

        for result in results.results:

            question = result.question
            answers = result.answers

            if question.answer_count <= 0 or not answers:
                continue

            candidate_text = question.body

            candidate_embedding = self.embedding_client.embed(
                candidate_text
            )

    
            similarity = self._cosine_similarity(
                query_embedding,
                candidate_embedding
            )

            if similarity < min_similarity:
                continue


            scored.append(
                RetriveSimiler(
                    question=question,
                    answers=answers,
                    score=similarity
                )
            )


            record_metadata = {
                "question_id": question.question_id,
                "title": question.title,
                "url": question.url,
                "tags": question.tags,
                "question_score": question.score,
                "answer_count": question.answer_count,

                "answers": [
                    {
                        "answer_id": answer.answer_id,
                        "body": answer.body,
                        "score": answer.score,
                        "is_accepted": answer.is_accepted,
                    }
                    for answer in answers
                ],
            }

            self.vector_store_client.insert_one(
                collection_name=collection_name,
                text=candidate_text,
                vector=candidate_embedding,
                metadata=record_metadata,
                record_id=question.question_id
            )

  
        scored.sort(
            key=lambda item: item.score,
            reverse=True
        )


        return [
            item.model_dump()
            for item in scored
        ]


    def answer_error_question(self,query_text:str,results: WeabscearchSearchResponse, min_similarity: float = 0.4):

        similer_questions=self.rank_similar_web_results(query_text,results,min_similarity)

        if not similer_questions:
            return None

      



    @staticmethod
    def _cosine_similarity(vec1, vec2):
        import numpy as np
        v1, v2 = np.array(vec1), np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))