import json
import logging
from models.DB_Schema.Cluster import Cluster
from .ProcessController import ProcessController
from stores.llm.LLMEnums import ChatRoles
from .extraction_parsing import parse_extraction_output
from models.DB_Schema.ErrorMessage import ErrorMessage
from .WebscearchController import WebscearchController
from models.DB_Schema.Weabscearch import WeabscearchSearchResponse
from models.DB_Schema.Weabscearch import RetriveSimiler
from models.DB_Schema.Weabscearch import WeabscearchAnswers
from models.DB_Schema.Weabscearch import WeabscearchQuestion
from models.DB_Schema.ProcessingJob import ProcessingJob
from models.Enums.JobProcessingEnums import JobProcessingEnums
from .BaseController import BaseController

logger = logging.getLogger(__name__)


class NlpController(BaseController):
    def __init__(self, embedding_client: object, generation_client: object,
                 vector_store_client: object, classifier_client: object, templete_client: object):
        super().__init__()
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.vector_store_client = vector_store_client
        self.classifier_client = classifier_client
        self.templete_parser = templete_client
        self.process_controller = ProcessController()
        self.WebscearchController = WebscearchController(scearch_backend="stackoverflow")

        # Scoring weights and threshold now come from settings instead of being
        # hardcoded, so they can be tuned without touching code.
        self.similarity_weight = getattr(self.app_settings, "SIMILARITY_WEIGHT", 0.75)
        self.answer_count_weight = getattr(self.app_settings, "ANSWER_COUNT_WEIGHT", 0.10)
        self.question_score_weight = getattr(self.app_settings, "QUESTION_SCORE_WEIGHT", 0.10)
        self.accepted_answer_weight = getattr(self.app_settings, "ACCEPTED_ANSWER_WEIGHT", 0.05)
        self.default_min_similarity = getattr(self.app_settings, "MIN_SIMILARITY", 0.4)

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
        system_prompt = self.generation_client.construct_prompt(ChatRoles.SYSTEM.value, system_prompt)

        try:
            llm_result = self.generation_client.generate(promot=user_prompt, messages=[system_prompt])
        except Exception:
            logger.exception("extract_error_details: generation_client.generate failed")
            return {"success": False, "error": "generation_failed", "data": None, "cleaned_text": cleaned_text}

        if not llm_result:
            return {"success": False, "error": None, "data": None, "cleaned_text": cleaned_text}

        parser_result = parse_extraction_output(llm_result)
        parser_result["cleaned_text"] = cleaned_text
        return parser_result

    def rank_similar_web_results(self,query_text: str,results: WeabscearchSearchResponse,min_similarity: float = None):

        if min_similarity is None:
            min_similarity = self.default_min_similarity

        if not results or not results.results:
            return []

        try:
            query_embedding = self.embedding_client.embed(query_text)
        except Exception:
            logger.exception(
                "rank_similar_web_results: failed to embed query_text"
            )
            return []

        scored = []
        seen_question_ids = set()
        collection_name = self.creater_collection_name()

        for result in results.results:

            question = result.question
            answers = result.answers

            if question.answer_count <= 0 or not answers:
                continue

            if question.question_id in seen_question_ids:
                continue

            top_answers = sorted(
                answers,
                key=lambda a: (a.is_accepted, a.score),
                reverse=True
            )[:self.app_settings.MAX_ANSWERS_PER_DOCUMENT]

            candidate_text = question.body

            try:
                candidate_embedding = self.embedding_client.embed(
                    candidate_text
                )
            except Exception:
                logger.exception(
                    "rank_similar_web_results: failed to embed candidate %s",
                    question.question_id
                )
                continue

            similarity = self._cosine_similarity(
                query_embedding,
                candidate_embedding
            )

            if similarity is None or similarity < min_similarity:
                continue

            answer_count_score = min(
                question.answer_count / 10.0,
                1.0
            )

            question_score_score = min(
                max(question.score, 0) / 20.0,
                1.0
            )

            accepted_answer_score = (
                1.0
                if any(a.is_accepted for a in top_answers)
                else 0.0
            )

            final_score = (
                self.similarity_weight * similarity
                + self.answer_count_weight * answer_count_score
                + self.question_score_weight * question_score_score
                + self.accepted_answer_weight * accepted_answer_score
            )

            seen_question_ids.add(question.question_id)

            scored.append(
                RetriveSimiler(
                    question=question,
                    answers=top_answers,
                    score=final_score
                )
            )

            record_metadata = {
                "question_id": question.question_id,
                "title": question.title,
                "url": question.url,
                "tags": question.tags,
                "question_score": question.score,
                "answer_count": question.answer_count,
                "semantic_similarity": similarity,
                "answer_count_score": answer_count_score,
                "question_score_score": question_score_score,
                "accepted_answer_score": accepted_answer_score,
                "final_score": final_score,
                "answers": [
                    {
                        "answer_id": answer.answer_id,
                        "body": answer.body,
                        "score": answer.score,
                        "is_accepted": answer.is_accepted,
                    }
                    for answer in top_answers
                ],
            }

            try:
                self.vector_store_client.insert_one(
                    collection_name=collection_name,
                    text=candidate_text,
                    vector=candidate_embedding,
                    metadata=record_metadata,
                    record_id=question.question_id
                )
            except Exception:
                logger.exception(
                    "rank_similar_web_results: failed to cache question %s",
                    question.question_id
                )

        scored.sort(
            key=lambda item: item.score,
            reverse=True
        )

        return [item.model_dump() for item in scored]


    
    def answer_error_question(self, query_text: str, results: WeabscearchSearchResponse, min_similarity: float = None):
        similer_questions = self.rank_similar_web_results(
            query_text,
            results,
            min_similarity
        )

        if not similer_questions:
            return None, None, None, []

        similer_questions = sorted(
            similer_questions,
            key=lambda x: x["score"],
            reverse=True
        )[:self.app_settings.MAX_DOCUMENTS]

        retrived_documents = []

        for result in similer_questions:
            question = result['question']
            answers = result['answers']
            similirity_score = result['score']

            document = {
                # Fix: question_id is now included explicitly so the LLM never
                # has to guess/parse it out of the URL for used_documents.
                "question_id": question['question_id'],
                "title": question['title'],
                'body': question['body'][:self.app_settings.MAX_QUESTION_CHARS],
                "tags": question['tags'],
                "url": question['url'],
                "question_score": question['score'],
                "answers": [
                    {
                        "answer_id": answer['answer_id'],
                        "body": answer['body'][:self.app_settings.MAX_ANSWER_CHARS],
                        "score": answer['score'],
                        'is_accepted': answer['is_accepted']
                    }
                    for answer in answers
                ],
                "similirity_score": similirity_score
            }

            retrived_documents.append(document)

        user_prompt = self.templete_parser.get("rag", "USER_INPUT", {
            "query": self.generation_client.process_text(query_text),
            "documents": retrived_documents
        })

        examples = self.templete_parser.get("rag", "EXAMPLES")
        system = self.templete_parser.get("rag", "SYSTEM_PROMPT")
        system_prompt = self.generation_client.construct_prompt(
            self.generation_client.enums.SYSTEM.value,
            "\n\n".join([system, examples])
        )

        try:
            llm_response = self.generation_client.generate(promot=user_prompt, messages=[system_prompt])
        except Exception:
            logger.exception("answer_error_question: generation_client.generate failed")
            return None, system_prompt, user_prompt, retrived_documents

        # Fix: validate the model actually returned parseable JSON matching
        # the contract, instead of trusting the raw string blindly.


        parsed_response, parse_error = self._safe_parse_llm_json(llm_response)
        if parse_error:
            logger.warning("answer_error_question: LLM response failed JSON validation: %s", parse_error)

        return llm_response, system_prompt, user_prompt, retrived_documents

    def get_formatted_answer(self, query_text: str, results: WeabscearchSearchResponse, min_similarity: float = None):
   
        llm_response, system_prompt, user_prompt, retrived_documents = self.answer_error_question(
            query_text, results, min_similarity
        )
        try:
            llm_response = self.generation_client.generate(
                promot=user_prompt,
                messages=[system_prompt]
            )

        except RateLimitError as e:
            logger.warning(
                "LLM rate limit reached. The user's data is valid."
            )

            return {
                "success": False,
                "error_type": "LLM_RATE_LIMIT",
                "error": "LLM service usage limit reached."
            }

        except Exception as e:
            logger.exception(
                "answer_error_question: generation_client.generate failed"
            )

            return {
                "success": False,
                "error_type": "LLM_GENERATION_ERROR",
                "error": str(e)
            }

        if llm_response is None:
            return {
                "success": False,
                "error": "no_results_or_generation_failed",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
            }

        parsed, parse_error = self._safe_parse_llm_json(llm_response)
        if parsed is None:
            return {
                "success": False,
                "error": parse_error,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
            }

        # Resolve question_id -> real title/url so the caller can link sources
        # instead of showing bare IDs.
        doc_lookup = {str(d["question_id"]): d for d in retrived_documents}
        sources = []
        for used_doc in (parsed.get("used_documents") or []):
            doc = doc_lookup.get(str(used_doc.get("question_id")), {})
            sources.append({
                "question_id": used_doc.get("question_id"),
                "answer_id": used_doc.get("answer_id"),
                "is_accepted": used_doc.get("is_accepted"),
                "reason": used_doc.get("reason"),
                "title": doc.get("title"),
                "url": doc.get("url"),
            })

        return {
            "success": True,
            "error_type": parsed.get("error_type"),
            "root_cause": parsed.get("root_cause"),
            "explanation": parsed.get("explanation"),
            "solution": parsed.get("solution"),
            "steps": parsed.get("steps") or [],
            "code_fix": parsed.get("code_fix"),
            "alternative_solutions": parsed.get("alternative_solutions") or [],
            "recommendations": parsed.get("recommendations") or [],
            "sources": sources,
            "confidence": parsed.get("confidence"),
            "missing_information": parsed.get("missing_information") or [],
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        }

    @staticmethod
    def _safe_parse_llm_json(llm_response: str):
        """Attempts to parse and sanity-check the LLM's JSON output.
        Returns (parsed_dict_or_None, error_message_or_None)."""
        if not llm_response:
            return None, "empty response"
        try:
            parsed = json.loads(llm_response)
        except (json.JSONDecodeError, TypeError) as exc:
            return None, f"invalid JSON: {exc}"

        required_fields = {
            "error_type", "root_cause", "explanation", "solution",
            "steps", "code_fix", "alternative_solutions",
            "recommendations", "used_documents", "confidence",
            "missing_information"
        }
        missing = required_fields - parsed.keys()
        if missing:
            return parsed, f"missing fields: {sorted(missing)}"

        confidence = parsed.get("confidence")
        if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
            return parsed, "confidence out of range"

        missing_information = parsed.get("missing_information")
        if not isinstance(missing_information, list):
            return parsed, "missing_information must be a list"

        return parsed, None

    @staticmethod
    def _cosine_similarity(vec1, vec2):
        import numpy as np
        v1, v2 = np.array(vec1), np.array(vec2)
        norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return None
        return float(np.dot(v1, v2) / (norm1 * norm2))