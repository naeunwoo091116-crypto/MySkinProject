import base64
from google.cloud import aiplatform

class ChatbotService:
    def __init__(self):
        self.project_id = "skincare-data-platform"
        self.location = "us-central1"
        self.endpoint_id = "2282954475658280960"
        
        # 전체 리소스 경로 형식
        self.endpoint_path = f"projects/{self.project_id}/locations/{self.location}/endpoints/{self.endpoint_id}"
        
        try:
            aiplatform.init(project=self.project_id, location=self.location)
            self.endpoint = aiplatform.Endpoint(self.endpoint_path)
            print(f"✅ Vertex AI 엔드포인트 연결 성공: {self.endpoint_id}")
        except Exception as e:
            print(f"❌ Vertex AI 초기화 실패: {e}")
            self.endpoint = None

    def generate_response(self, message, image_file=None):
        if self.endpoint is None:
            return "AI 서비스가 현재 준비되지 않았습니다."

        instances = [{}]

        # 이미지 유무에 따라 프롬프트 다르게 구성
        if image_file:
            try:
                image_bytes = image_file.read()
                image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                instances[0]["image"] = image_b64
                # 이미지가 있을 때만 <image> 태그 포함
                formatted_prompt = f"""USER: <image>
{message.strip()}
Please provide your answer in the following format:
Chain-of-Thought: [Detailed analysis of skin condition, environmental factors, and scientific reasoning for ingredient selection]
Answer: [Final skincare recommendations with specific ingredients and usage instructions]
ASSISTANT:"""
            except Exception as e:
                return f"이미지 처리 오류: {str(e)}"
        else:
            # 이미지가 없을 때는 <image> 태그 제거
            formatted_prompt = f"""USER: {message.strip()}
Please provide your answer in the following format:
Chain-of-Thought: [Detailed analysis of skin condition, environmental factors, and scientific reasoning for ingredient selection]
Answer: [Final skincare recommendations with specific ingredients and usage instructions]
ASSISTANT:"""

        instances[0]["prompt"] = formatted_prompt

        try:
            # AI가 생각할 시간을 충분히 주기 위해 timeout 300초 설정
            prediction = self.endpoint.predict(instances=instances, timeout=300)
            if prediction.predictions:
                ans = prediction.predictions[0]
                # 답변에서 ASSISTANT: 이후만 추출
                if "ASSISTANT:" in ans:
                    return ans.split("ASSISTANT:")[-1].strip()
                return ans.strip()
            return "답변을 생성할 수 없습니다."
        except Exception as e:
            return f"AI 상담 중 오류 발생: {str(e)}"

# [필수] app.py에서 호출하는 함수
_chatbot_instance = None
def get_chatbot_service():
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = ChatbotService()
    return _chatbot_instance