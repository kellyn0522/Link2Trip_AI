# 이후에 다른 라이브러리들을 임포트합니다.
import json
import re
import google.generativeai as genai
from pydantic import BaseModel
from youtube_model import YouTubeModel
from crowler import get_youtube_data
from fastapi import FastAPI, HTTPException

app = FastAPI()

# 유튜브 URL 입력
# youtube_url = input("유튜브 URL을 입력하세요: ")

class UrlRequest(BaseModel):
    url: str

def process_youtube_url(youtube_url: str):

    # Selenium으로 유튜브 데이터 가져오기
    youtube_data = get_youtube_data(youtube_url)
    title = youtube_data.get("title", "제목 없음")
    video_detail = youtube_data.get("video_detail", "설명 없음")

    # print(f"\n📌 영상 제목: {youtube_data['title']}")
    # print(f"📝 설명: {youtube_data['video_detail']}\n\n")

    # Gemini API를 이용한 영상 요약
    yt_model = YouTubeModel()   # 클래스 호출 
    video_id = yt_model.get_video_id(youtube_url) 

    if not video_id:
        print("❌ 올바른 유튜브 URL을 입력하세요.")
    else:
        transcript_text = yt_model.get_youtube_transcript(video_id)

    if "자막을 가져오는 데 실패했습니다" in transcript_text:
        print(f"❌ 오류: {transcript_text}")
    else:
        # 크롤링 데이터 + 자막 원문을 합쳐서 LLM에게 전달
        combined_text = f"""
        아래는 유튜브 영상의 정보야. 영상 설명과 자막 원문을 분석해서 여행 장소 중심으로 요약해줘.

        [유튜브 영상 제목]
        {title}

        [유튜브 영상 설명]
        {video_detail}

        [유튜브 자막 원문]
        {transcript_text}

        위 내용을 기반으로 여행 장소 중심으로 요약해줘. 
        관광지나 상호명이 올바르게 나왔으면 좋겠어. 장소마다 특징을 한 줄로 정리해서 같이 설명해줘. 
        상호명이 없는 장소는 제외하고 알려줘.
        """

        # 기존 요약 함수 그대로 사용
        final_summary = yt_model.summarize_text_with_gemini(combined_text)

        # 최종 요약 출력
        print("\n📌 유튜브 영상 최종 요약 📌\n")
        print(final_summary)


# # 결과 출력
# if "error" in summary_result:
#     print(f"❌ 오류: {summary_result['error']}")
# else:
#     print("\n📌 유튜브 영상 요약 📌\n")
#     print(summary_result["summary"])

