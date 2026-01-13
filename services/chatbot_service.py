import os
import torch
import logging
from PIL import Image
from transformers import (
    AutoTokenizer,
    CLIPImageProcessor,
    LlavaForConditionalGeneration
)
from peft import PeftModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
BASE_MODEL_NAME = "llava-hf/llava-1.5-7b-hf"
ADAPTER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "final")
MAX_LENGTH = 2048

class ChatbotService:
    _instance = None
    _model = None
    _tokenizer = None
    _image_processor = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ChatbotService()
        return cls._instance

    def __init__(self):
        if ChatbotService._model is None:
            self.load_model()

    def load_model(self):
        logger.info("Loading Chatbot Model...")
        try:
            # 1. Load Tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, use_fast=False)
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
            
            # 2. Load Image Processor
            self._image_processor = CLIPImageProcessor.from_pretrained(BASE_MODEL_NAME)
            
            # 3. Load Base Model
            logger.info(f"Loading base model: {BASE_MODEL_NAME}")
            base_model = LlavaForConditionalGeneration.from_pretrained(
                BASE_MODEL_NAME,
                torch_dtype=torch.float16, # Use float16 for inference
                device_map="cuda",
                low_cpu_mem_usage=True
            )
            
            # 4. Load LoRA Adapter
            if os.path.exists(ADAPTER_PATH):
                logger.info(f"Loading LoRA adapter from: {ADAPTER_PATH}")
                self._model = PeftModel.from_pretrained(
                    base_model,
                    ADAPTER_PATH,
                    torch_dtype=torch.float16
                )
            else:
                logger.warning(f"Adapter path {ADAPTER_PATH} not found. Using base model only.")
                self._model = base_model

            logger.info("Chatbot Model Loaded Successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load chatbot model: {e}")
            import traceback
            traceback.print_exc()
            self._model = None # Ensure model is None if load fails

    def generate_response(self, message, image=None):
        if self._model is None:
             # Try reloading if it failed initially or wasn't loaded
            self.load_model()
            if self._model is None:
                return "상담 챗봇 모델을 로드할 수 없습니다. 관리자에게 문의하세요."

        try:
            # Prepare inputs
            prompt = ""
            pixel_values = None

            if image:
                # Handle Image
                if not isinstance(image, Image.Image):
                     image = Image.open(image).convert('RGB')
                
                # Resize/Process image
                pixel_values = self._image_processor(
                    images=image,
                    return_tensors="pt"
                )['pixel_values'].to(self._model.device, dtype=torch.float16)

                prompt = f"USER: <image>\n{message}\nASSISTANT:"
            else:
                # Text only interaction (Note: LLaVA is optimized for vision, but can do text)
                prompt = f"USER: {message}\nASSISTANT:"

            # Tokenize
            input_ids = self._tokenizer(
                prompt,
                return_tensors='pt',
                truncation=True,
                max_length=MAX_LENGTH
            ).input_ids.to(self._model.device)

            # Generate
            with torch.inference_mode():
                output_ids = self._model.generate(
                    input_ids,
                    pixel_values=pixel_values,
                    max_new_tokens=1024,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    use_cache=True
                )

            # Decode
            generated_text = self._tokenizer.decode(
                output_ids[0][input_ids.shape[1]:], 
                skip_special_tokens=True
            ).strip()

            return generated_text

        except Exception as e:
            logger.error(f"Error during chatbot generation: {e}")
            import traceback
            traceback.print_exc()
            return "죄송합니다. 답변을 생성하는 도중 오류가 발생했습니다."

# Singleton accessor
def get_chatbot_service():
    return ChatbotService.get_instance()
