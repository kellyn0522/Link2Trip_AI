import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class YouTubeModel:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    # URL에서 비디오 ID 추출
    def get_video_id(self, url):
        if "youtube.com" in url:
            return url.split("v=")[-1].split("&")[0]
        elif "youtu.be" in url:
            return url.split("/")[-1]
        return None

    # 유튜브 자막 가져옴
    def get_youtube_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
            text = " ".join([t['text'] for t in transcript])
            return text
        except Exception as e:
            return f"자막을 가져오는 데 실패했습니다: {e}"

    # Gemini 사용하여 텍스트 요약
    def summarize_text_with_gemini(self, text):

        response = self.model.generate_content(
            f"다음 유튜브 영상의 내용과 영상 설명에 대해서 여행 장소 중심으로 요약해줘. "
            f"카테고리는 '카페/디저트', '음식점', '관광지', '활동/체험', '쇼핑', '기타' 이 6가지로 분류해서 알려줘."
            f"없는 카테고리는 제외하고 말해줘. "
            f"떡집의 경우에는 카페/디저트 카테고리로 넣어줘."
            f"관광지나 상호명이 올바르게 나왔으면 좋겠어. "
            f"장소마다 특징을 한 줄로 정리해서 같이 설명해줘. "
            f"상호명이 없는 장소는 제외하고 알려줘. " 
            f"요약 맨 앞에 카테고리는 !, 상호명은 @, 특징은 $ 으로 시작해줘. "
            f"주소 데이터가 같이 있는 경우에 주소 데이터는 제외하고 알려줘. :\n\n{text}"
        )
    
        return response.text
    
    def process_youtube_summary(self, url):
        # 비디오 ID 추출 및 자막 가져오기
        video_id = self.get_video_id(url)
        if not video_id:
            return {"error" : "올바른 유튜브 URL을 입력하세요."}

        transcript_text = self.get_youtube_transcript(video_id)
        if "자막을 가져오는 데 실패했습니다" in transcript_text:
            return {"error": transcript_text}

        summary = self.summarize_text_with_gemini(transcript_text)
        return {"summary": summary}


