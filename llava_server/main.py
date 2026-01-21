import os
import torch
import base64
import io
import subprocess
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from transformers import AutoProcessor, LlavaForConditionalGeneration, BitsAndBytesConfig
from PIL import Image

app = FastAPI()

# --- [설정] ---
BUCKET_NAME = "skincare-model-storage" 
GCS_MODEL_PATH = f"gs://{BUCKET_NAME}/final"
LOCAL_MODEL_PATH = "/app/model_files"

model = None
processor = None

# A100에서는 양자화 없이 FP16으로 직접 로드 (더 빠름)
# 4비트 양자화는 VRAM이 부족한 경우에만 사용
USE_QUANTIZATION = False  # A100은 VRAM 충분하므로 False

if USE_QUANTIZATION:
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16
    )
else:
    bnb_config = None

def download_model_from_gcs():
    if not os.path.exists(LOCAL_MODEL_PATH) or not os.listdir(LOCAL_MODEL_PATH):
        print(f"--- [GCS] 모델 다운로드 시작 ---")
        os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)
        try:
            subprocess.run(["gsutil", "-m", "cp", "-r", f"{GCS_MODEL_PATH}/*", LOCAL_MODEL_PATH], check=True)
            print("✅ [GCS] 다운로드 완료")
        except Exception as e:
            print(f"❌ [GCS] 다운로드 실패: {e}")
            raise e

@app.on_event("startup")
async def load_model():
    global model, processor
    try:
        download_model_from_gcs()
        
        print("--- [LOAD] 모델 및 프로세서 로딩 중 ---")
        # 1. 토큰 깨짐 방지를 위해 use_fast=False 및 trust_remote_code=True 설정
        processor = AutoProcessor.from_pretrained(LOCAL_MODEL_PATH, use_fast=False, trust_remote_code=True)
        
        # 양자화 여부에 따라 모델 로드 방식 변경
        if bnb_config:
            model = LlavaForConditionalGeneration.from_pretrained(
                LOCAL_MODEL_PATH,
                quantization_config=bnb_config,
                device_map="auto",
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
        else:
            # A100: FP16 + SDPA로 최대 속도 (양자화 없음, PyTorch 2.0 내장)
            model = LlavaForConditionalGeneration.from_pretrained(
                LOCAL_MODEL_PATH,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                attn_implementation="sdpa"  # PyTorch 2.0 내장 SDPA
            )
            print("✅ SDPA (Scaled Dot Product Attention) 활성화됨")

        # 2. [토큰 강제 교정] 패딩 방향과 토큰 ID를 명확히 지정
        processor.tokenizer.padding_side = "left"
        if processor.tokenizer.pad_token is None:
            processor.tokenizer.pad_token = processor.tokenizer.eos_token
        
        model.config.pad_token_id = processor.tokenizer.pad_token_id
        model.eval()
        print("✅ [SUCCESS] 모델 로드 및 토크나이저 보정 완료!")
    except Exception as e:
        print(f"❌ [ERROR] 로드 실패: {e}")

@app.get("/health")
async def health():
    if model is not None:
        return {"status": "healthy"}
    return JSONResponse(content={"status": "loading"}, status_code=503)

@app.post("/predict")
async def predict(request: Request):
    if model is None:
        return JSONResponse(content={"error": "Model not ready"}, status_code=503)
    
    try:
        body = await request.json()
        instances = body.get("instances", [])
        results = []
        
        for instance in instances:
            question = instance.get("prompt", "")
            image_base64 = instance.get("image")

            # 3. [프롬프트 최적화] 불필요한 공백 제거 및 CoT 구조 적용
            # 이미지 유무에 따라 <image> 태그 조건부 적용
            if image_base64:
                formatted_prompt = f"USER: <image>\n{question.strip()}\n\n[STRICT RULE] Your ENTIRE response must be under 150 words. Be concise.\nChain-of-Thought: (2-3 sentences max)\nAnswer: (3-4 sentences max)\nASSISTANT:"
                image = Image.open(io.BytesIO(base64.b64decode(image_base64))).convert("RGB")
                inputs = processor(text=formatted_prompt, images=image, return_tensors="pt").to("cuda")
            else:
                formatted_prompt = f"USER: {question.strip()}\n\n[STRICT RULE] Your ENTIRE response must be under 150 words. Be concise.\nChain-of-Thought: (2-3 sentences max)\nAnswer: (3-4 sentences max)\nASSISTANT:"
                inputs = processor(text=formatted_prompt, return_tensors="pt").to("cuda")

            with torch.no_grad():
                # 4. [생성 파라미터 보정] 환각 방지 + 반복 방지 균형
                output = model.generate(
                    **inputs,
                    max_new_tokens=1024,  # 적절한 길이
                    do_sample=False,  # Greedy decoding으로 환각 방지
                    repetition_penalty=1.1,  # 적당한 반복 방지
                    pad_token_id=processor.tokenizer.pad_token_id,
                    eos_token_id=processor.tokenizer.eos_token_id
                )
            
            full_text = processor.decode(output[0], skip_special_tokens=True)

            # 답변만 추출
            if "ASSISTANT:" in full_text:
                reply = full_text.split("ASSISTANT:")[-1].strip()
            else:
                reply = full_text

            # 후처리: 반복 답변 제거 (첫 번째 완성된 답변만 사용)
            # \n\n 이후 반복되는 내용 제거
            if "\n\n" in reply:
                parts = reply.split("\n\n")
                # 첫 번째 부분만 사용 (또는 Chain-of-Thought + Answer까지)
                clean_reply = parts[0]
                # Answer 부분이 있으면 포함
                for i, part in enumerate(parts[1:], 1):
                    if part.strip().startswith("Answer:") or part.strip().startswith("Chain-of-Thought:"):
                        clean_reply += "\n\n" + part
                    elif i == 1 and not parts[0].strip().endswith(("다.", "요.", "습니다.", "세요.", "니다.")):
                        # 첫 번째 부분이 문장으로 안 끝나면 두 번째도 포함
                        clean_reply += "\n\n" + part
                    else:
                        break
                reply = clean_reply.strip()

            results.append(reply)
            
        return {"predictions": results}

    except Exception as e:
        print(f"❌ 추론 오류: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)