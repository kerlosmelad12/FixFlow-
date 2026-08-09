from ..LLMInterface import LLMInterface
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
import logging
from ..LLMEnums import ChatRoles, TorchDType,Devicemap
import os
from controllers.BaseController import BaseController

from huggingface_hub import snapshot_download
from huggingface_hub.utils import LocalEntryNotFoundError

class QweenProvider(LLMInterface):

    def __init__(self, model_name, default_TEMPERATURE: float = 0.7,
                 MAX_OUTPUT_TOKENS: int = 2048,
        
                 TORCH_DTYPE: str = TorchDType.FLOAT16.name, LOAD_IN_4BIT: bool = True,
                 device_map: str = Devicemap.CUDA.value,
                 INPUT_MAX_CHRACTERS:int=2500):
                    
            self.base_controller = BaseController()

            self.model_name = model_name

            self.model_path = self.base_controller.get_model_path(model_name)

            self.default_TEMPERATURE = default_TEMPERATURE
            self.max_output_tokens = MAX_OUTPUT_TOKENS
            self.device_map = device_map
            self.load_in_4bit = LOAD_IN_4BIT
            self.logger = logging.getLogger(__name__)
            self.torch_dtype = TorchDType[TORCH_DTYPE.upper()].value
            self.input_max_chracters = INPUT_MAX_CHRACTERS

            quant_config = None

            if self.load_in_4bit:
                quant_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=self.torch_dtype,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )

            self.load_or_download_model(quant_config)





    def load_or_download_model(self, quant_config=None):

        try:
            # Explicitly resolve the local snapshot path — no network call if cached
            local_path = snapshot_download(
                repo_id=self.model_name,
                cache_dir=self.model_path,
                local_files_only=True,
            )
            self.logger.info(f"Found model locally at: {local_path}")

            self.llm = AutoModelForCausalLM.from_pretrained(
                local_path,
                local_files_only=True,
                torch_dtype=self.torch_dtype,
                device_map=self.device_map,
                quantization_config=quant_config,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                local_path,
                local_files_only=True,
            )
            self.logger.info("Loaded model from local cache.")

        except (LocalEntryNotFoundError, FileNotFoundError, OSError):
            self.logger.info("Model not found locally. Downloading from HuggingFace...")

            local_path = snapshot_download(
                repo_id=self.model_name,
                cache_dir=self.model_path,
            )

            self.llm = AutoModelForCausalLM.from_pretrained(
                local_path,
                torch_dtype=self.torch_dtype,
                device_map=self.device_map,
                quantization_config=quant_config,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(local_path)

            self.logger.info("Model downloaded successfully.")



    def set_generation_model(self, model_id: str):

        if hasattr(self, "llm") and self.llm is not None:
            del self.llm
            torch.cuda.empty_cache()

        self.model_name = model_id
        self.model_path = self.base_controller.get_model_path(model_id)

        quant_config = None

        if self.load_in_4bit:
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=self.torch_dtype,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
            )

        self.load_or_download_model(quant_config)



    def set_embedding_model(self, model_id, embedding_size):
        raise NotImplemented("this function not support for embedding data")

    

  


    def generate(self,promot: str,messages: list[dict] | dict,max_new_tokens: int = None, temperature: float = None) -> str:


        if not self.tokenizer:
            self.logger.error("tokenizer not added")
        if not self.llm:
            self.logger.error("llm not added")

        if promot:
            messages = [self.construct_prompt(ChatRoles.SYSTEM.value, promot)] + messages

        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.llm.device)

        generated_ids = self.llm.generate(
            **model_inputs,
            max_new_tokens=max_new_tokens or self.max_output_tokens,
            temperature=self.default_TEMPERATURE,
            do_sample=self.default_TEMPERATURE > 0,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        return self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    


    def embed(self, text) -> list[list[float]]:
         raise NotImplemented("this model not support for embedding data")
         
         

    def construct_prompt(self, role: str, message: str) :
            return {'role':role,
                    'content':message}
           


    