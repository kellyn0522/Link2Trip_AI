import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import json

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
            f"다음 유튜브 영상의 내용을 여행 장소 중심으로 요약해줘. "
            f"관광지나 상호명이 올바르게 나왔으면 좋겠어. "
            f"장소마다 특징을 한 줄로 정리해서 같이 설명해줘. "
            f"상호명이 없는 장소는 제외하고 알려줘. :\n\n{text}"
        )
        
        return response.text


# 클래스 호출
yt_model = YouTubeModel()

# 유튜브 URL 입력
youtube_url = input("유튜브 URL을 입력하세요: ")

# 비디오 ID 추출 및 자막 가져오기
video_id = yt_model.get_video_id(youtube_url)
if not video_id:
    print("올바른 유튜브 URL을 입력하세요.")
else:
    transcript_text = yt_model.get_youtube_transcript(video_id)

    if "자막을 가져오는 데 실패했습니다" not in transcript_text:
        # Gemini API로 요약
        summary = yt_model.summarize_text_with_gemini(transcript_text)
        print("\n📌 유튜브 영상 요약 📌\n")
        print(summary)
    else:
        print(transcript_text)

