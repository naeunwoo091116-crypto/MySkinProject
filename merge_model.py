import torch
from transformers import AutoProcessor, LlavaForConditionalGeneration
from peft import PeftModel

base_model_id = "llava-hf/llava-1.5-7b-hf"
adapter_path = "./llava_server/final"  # 현재 어댑터가 있는 경로
save_path = "./llava_server/merged_final" # 합쳐진 모델이 저장될 경로

print("1. 베이스 모델 로드 중...")
model = LlavaForConditionalGeneration.from_pretrained(
    base_model_id, torch_dtype=torch.float16, device_map="cpu"
)

print("2. 어댑터 결합 중...")
model = PeftModel.from_pretrained(model, adapter_path)

print("3. 모델 병합 중 (Merge and Unload)...")
model = model.merge_and_unload()

print("4. 병합된 모델 저장 중...")
model.save_pretrained(save_path)
processor = AutoProcessor.from_pretrained(adapter_path)
processor.save_pretrained(save_path)

print(f"✅ 병합 완료! '{save_path}' 폴더를 확인하세요.")