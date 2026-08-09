from models.DB_Schema.Cluster import Cluster
from .ProcessController import ProcessController
from stores.llm.LLMEnums import ChatRoles
from .extraction_parsing import parse_extraction_output
from models.DB_Schema.ErrorMessage import ErrorMessage
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

    def creater_collection_name(self,error:ErrorMessage):
         return f"{error.id}_collection"









   




        


            
        


        


