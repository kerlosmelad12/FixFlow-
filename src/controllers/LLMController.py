from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
    BitsAndBytesConfig
)
from langchain_huggingface import HuggingFacePipeline
from helper import get_settings
import torch


class LLMService:
    _model = None
    _tokenizer = None
    _pipeline = None
    _langchain_pipeline = None
    
    @classmethod
    def get_model(cls):
        if cls._model is None:
            settings = get_settings()

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )

            cls._tokenizer = AutoTokenizer.from_pretrained(
                settings.LLM_DATA_EXTRACTOR_PATH,
                cache_dir=settings.MODELS_CACHE_PATH
            )

            cls._model = AutoModelForCausalLM.from_pretrained(
                settings.LLM_DATA_EXTRACTOR_PATH,
                quantization_config=quantization_config,
                device_map="auto",
                cache_dir=settings.MODELS_CACHE_PATH
            )

        return cls._model, cls._tokenizer

    @classmethod
    def get_pipeline(cls):
        if cls._pipeline is None:
            model, tokenizer = cls.get_model()

            cls._pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                temperature=0.1,
                do_sample=False,
                return_full_text=False,
            )

        return cls._pipeline

    @classmethod
    def get_langchain_pipeline(cls):
        if cls._langchain_pipeline is None:
            hf_pipeline = cls.get_pipeline()
            cls._langchain_pipeline = HuggingFacePipeline(
                pipeline=hf_pipeline
            )

        return cls._langchain_pipeline