import os
import json
import google.generativeai as genai
from math import radians, sin, cos, sqrt, atan2
from itertools import permutations


# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")


# JSON 파일 불러오기
def load_trip_data(filename="trip_data.json"):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


# Haversine 공식: 두 위도/경도 좌표 간 거리 계산 (단위: km)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # 지구 반지름 (km)
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c



# LLM을 활용한 여행 일정 추천
def generate_initial_schedule(data):
    days = data["days"]
    places = data["places"]
    total_places = len(places)

    # 하루에 몇 개의 장소를 방문할지 자동 계산
    places_per_day = total_places // days
    extra_places = total_places % days  # 나머지 장소 개수 (고르게 분배)

    # 📌 LLM 프롬프트 수정: 반드시 **모든 장소**를 포함하도록 강제
    prompt = f"""
    아래 여행 데이터를 기반으로 반드시 **{days}일치 여행 일정**을 추천해줘.
    모든 장소({total_places}개)를 일정에 포함해야 하며, 하루에 {places_per_day}~{places_per_day + (1 if extra_places > 0 else 0)}개 장소를 배치해야 해.

    🔹 **출력 형식:**  
    ```
    1 | 점심 | 막국수 | 막국수와 수육 세트 인기
    1 | 오후 | 해변 | 피크닉 추천
    1 | 오후 | 돌체 | 휘낭시에와 돌낭스크가 유명한 빵 맛집
    1 | 저녁 | 라멘 | 일본식 라멘 맛집
    2 | 점심 | 찰떡 | 찹쌀떡, 선물용 추천
    2 | 오후 | 소품샵 | 수제 도자기 소품 판매
    2 | 오후 | 삐삐 | 모던하고 컬러풀한 브런치 카페
    3 | 점심 | 두딩 | 두부로 만든 푸딩 판매
    3 | 오후 | 르봉마젤 | 프랑스 감성의 식기 및 소품 판매
    3 | 오후 | 말차로 | 말차라떼 맛집
    ```

    🔹 **추가 조건:**  
    - **모든 장소({total_places}개)를 일정에 포함해야 함.**
    - 반드시 `{days}일` 일정이 포함되어야 함.
    - 장소는 아래 JSON 데이터에서만 선택해야 함.
    - 하루에 `{places_per_day}~{places_per_day + (1 if extra_places > 0 else 0)}`개의 장소가 포함되어야 함.
    - {places}에서 summary를 고려해서 위치를 약간 변경해줘.
    - JSON 데이터의 category를 참고하여, 일정에 맞게 배치할 것.
    - 점심과 저녁에는 반드시 "음식점" 카테고리에서 선택.
    - 오후 일정에는 "관광지" 1개 이상, "카페/디저트" 1개 이상 포함해야 함.
    - 야간 일정은 선택 사항이며, 필요하면 "관광지"에서 선택.
    - **표 헤더(일자 | 시간 | 상호명 | 요약)는 출력하지 말고, 위의 예시 형식으로만 출력할 것.**
    - **일정이 1,2일차까지만 나오면 반드시 3일차를 추가해서 작성할 것.**
    - **장소 중복 없이, 모든 장소가 일정에 한번씩만 포함되도록 할 것.**

    🔹 **JSON 데이터:**  
    {places}
    """

    response = model.generate_content(prompt)
    
    # LLM 응답에서 불필요한 부분 제거 후 반환
    return response.text.strip()


# LLM 응답 데이터에서 헤더 제거 및 데이터 정리
def parse_llm_schedule(schedule):
    parsed_schedule = []
    
    for line in schedule.split("\n"):
        parts = line.strip().split(" | ")

        # "일자 | 시간 | 상호명 | 요약" 같은 헤더가 포함되지 않도록 필터링
        if len(parts) == 4 and parts[0].isdigit():
            parsed_schedule.append({
                "day": int(parts[0]),  # "1" → int(1)
                "time": parts[1],
                "place_name": parts[2],
                "summary": parts[3]
            })

    return parsed_schedule

# Haversine 공식을 활용한 경로 최적화
def optimize_schedule_with_distance(parsed_schedule, places):
    # 장소 정보를 위도/경도와 매칭
    place_dict = {p["place_name"]: p for p in places}

    # 하루 단위로 일정 최적화
    optimized_schedule = []
    for day in range(1, max(p["day"] for p in parsed_schedule) + 1):
        day_schedule = [p for p in parsed_schedule if p["day"] == day]

        # 출발점 설정 (첫 번째 장소 기준)
        start_place = place_dict[day_schedule[0]["place_name"]]
        remaining_places = [place_dict[p["place_name"]] for p in day_schedule[1:]]

        # 최적화된 경로 찾기 (최소 거리 경로 선택)
        min_distance = float('inf')
        best_route = None

        for perm in permutations(remaining_places):
            route = [start_place] + list(perm)
            total_distance = sum(
                haversine(route[i]["latitude"], route[i]["longitude"], 
                          route[i+1]["latitude"], route[i+1]["longitude"])
                for i in range(len(route) - 1)
            )

            if total_distance < min_distance:
                min_distance = total_distance
                best_route = route

        # 최적 경로를 스케줄에 반영
        for i, place in enumerate(best_route):
            optimized_schedule.append({
                "day": day,
                "time": day_schedule[i]["time"],
                "place_name": place["place_name"],
                "summary": place["summary"]
            })

    return optimized_schedule


# json 형식으로 바꿈 
def convert_to_join(schedule_list):
    records = []
    day_counter = {}

    for entry in schedule_list:
        day = entry["day"]

        if day not in day_counter:
            day_counter[day] = 1
        else : 
            day_counter[day] += 1

        records.append({
            "day" : day,
            "sort" : day_counter[day],
            "place_name" : entry["place_name"],
            "summary" : entry["summary"]
        })

    json_data = json.dumps(records, ensure_ascii=False, indent=4)

    return json_data


'''
# 최적화된 일정 출력
def print_schedule(schedule):
    print("\n📌 [최적화된 여행 일정] 📌\n")
    print("일자 | 시간 | 상호명 | 요약")
    print("-" * 50)
    for entry in schedule:
        print(f"{entry['day']} | {entry['time']} | {entry['place_name']} | {entry['summary']}")
'''

# 실행
if __name__ == "__main__":
    trip_data = load_trip_data()

    # 기본 여행 일정 추천
    initial_schedule = generate_initial_schedule(trip_data)

    # LLM 응답에서 헤더 제거 & 데이터 정리
    parsed_schedule = parse_llm_schedule(initial_schedule)

    # 거리 기반 최적화 알고리즘 적용
    optimized_schedule = optimize_schedule_with_distance(parsed_schedule, trip_data["places"])

    # 최적화된 일정 출력
    # print_schedule(optimized_schedule)
    
    # json 형식 데이터 출력
    final_data = convert_to_join(optimized_schedule)
    print(final_data)

