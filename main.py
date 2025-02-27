# 이후에 다른 라이브러리들을 임포트합니다.
import json
import re
import google.generativeai as genai
from pydantic import BaseModel
from youtube_model import YouTubeModel
from crowler import get_youtube_data
from fastapi import FastAPI, HTTPException
from typing import List
from trip_model import TripModel

app = FastAPI()
trip_model = TripModel()


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
            trinscript_text = ""

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
        #print("\n📌 유튜브 영상 최종 요약 📌\n")
        #print(final_summary)

        # 결과를 저장할 딕셔너리 초기화
        records = []
        current_category = None
        id_counter = 1

        # 각 줄을 순회하면서 데이터 파싱
        for line in final_summary.strip().splitlines():
            line = line.strip()
            if not line:
                continue

            # 카테고리 라인: '!'로 시작
            if line.startswith("!"):
                current_category = line[1:].strip()
            # 데이터 항목 라인: '@'로 시작하며 '$'로 구분
            elif line.startswith("@"):
                if "$" in line:
                    parts = line[1:].split("$", 1)
                    place_name = parts[0].strip()
                    summary = parts[1].strip()
                    records.append({
                        "id": id_counter,
                        "category": current_category,
                        "place_name": place_name,
                        "summary": summary
                    })
                    id_counter += 1

        # JSON으로 변환 (한글 깨짐 방지)
        json_data = json.dumps(records, ensure_ascii=False)
        return json_data
        # print(json_data)


class URLRequest(BaseModel):
    url: str

@app.get("/process-url")
async def process_url(url: str):#payload: URLRequest
    # records = process_youtube_url(payload.url)
    # return records
    records = process_youtube_url(url)
    return records




# 입력 JSON의 places 요소를 위한 Pydantic 모델
class Place(BaseModel):
    id: int
    category: str
    place_name: str
    summary: str
    latitude: float
    longitude: float

# 전체 요청 JSON 데이터를 위한 모델
class TripData(BaseModel):
    days: int
    places: List[Place]
    

# GET 요청으로 JSON Body를 받기 위한 엔드포인트
@app.get("/api/recommend")
async def recommend(days: int, places: str): # trip_data: TripData
    places_list = json.loads(places)  # ✅ JSON 문자열을 Python 리스트로 변환

    # ✅ Place 모델 리스트로 변환 (기존 코드와 동일한 구조 유지)
    places_objects = [Place(**place) for place in places_list]  # 🔥 해결 핵심

    # ✅ 기존 trip_data와 동일한 구조로 변환
    input_data = {
        "days": days,
        "places": places_objects  # ✅ Place 객체 리스트 전달
    }

    # ✅ 기존 코드 유지 (trip_model 호출)
    initial_schedule = trip_model.generate_initial_schedule(input_data)
    parsed_schedule = trip_model.parse_llm_schedule(initial_schedule)
    optimized_schedule = trip_model.optimize_schedule_with_distance(parsed_schedule, places_objects)
    final_data = trip_model.convert_to_join(optimized_schedule)

    return final_data  # ✅ 기존 코드와 동일한 결과 반환
    # input_data = trip_data.model_dump()

    # # LLM을 통한 초기 일정 생성
    # initial_schedule = trip_model.generate_initial_schedule(input_data)

    # # 응답 파싱
    # parsed_schedule = trip_model.parse_llm_schedule(initial_schedule)

    # # 거리 기반 경로 최적화 (Place 객체 유지)
    # optimized_schedule = trip_model.optimize_schedule_with_distance(
    #     parsed_schedule, trip_data.places  # ✅ Place 객체 그대로 전달
    # )

    # # 최종 일정 데이터를 JSON 문자열로 변환 후 반환
    # final_data = trip_model.convert_to_join(optimized_schedule)
    # return final_data
    

@app.get("/")
async def root():
    return {"message": "FastAPI 서버 정상 실행 중!"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)









# # 결과 출력
# if "error" in summary_result:
#     print(f"❌ 오류: {summary_result['error']}")
# else:
#     print("\n📌 유튜브 영상 요약 📌\n")
#     print(summary_result["summary"])

