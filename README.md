# 유튜브 링크 기반의 개인 맞춤형 여행 장소 추천 서비스

### 🌐 Project Info

> ***'유튜브 URL을 입력하면 LLM을 이용하여 해당 영상의 여행 정보를 분석하고, 실제 존재하는 장소인지 검증한 후 사용자가 여행 계획을 세울 수 있도록 도와주는 개인화 서비스'***

<br>

## 📌 Quick View



<br>

## ⚒️ Usage Stack

분류 | 사용 기술
-- | --
언어 및 프레임워크 | `Python`, `FastAPI`
Gen AI (LLM) | `OpenAI API`, `Gemini API`
데이터 처리 | `BeautifulSoup`, `Haversine`

<br>

## 👉🏻 Role & Responsibilities

- LLM 기반 텍스트 요약 및 장소 추출 프롬프트 설계
- 영상 자막 및 설명 데이터 크롤링 + 장소명 추출 파이프라인 구축
- 거리 기반 Haversine 알고리즘을 활용한 일정 추천 로직 개발
- FastAPI 기반 AI 서버 구축 및 전체 추론 파이프라인 연결

     <img width="620" alt="image" src="https://github.com/user-attachments/assets/8ca90325-78b0-421c-8700-efd13b23dd0f" />

<br>

## 👉🏻 FastAPI end-point

### 1️⃣ GET /process-url

- 유튜브 영상의 설명과 자막 원문을 기반으로, 장소 중심의 요약 정보를 반환함
- 요청 : URL 처리
- 응답
     ```json
     { 
        "id": "integer",
        "category": "string",
        "place_name": "string",
        "summary": "string"
     }
     ```

### 2️⃣ POST /api/recommend

- 사용자가 원하는 장소를 기준으로 추천 일정 생성
- 요청
     ```json
     {
        "days": "integer",
        "places": [
           {
              "id": "integer",
              "category": "string",
              "place_name": "string",
              "summary": "string",
              "latitude" : "float",
              "longitude" : "float"
           }
        ]
     }
     ```
- 응답
     ```json
     {
        "day": "integer",
        "sort": "integer",
        "place_name": "string",
        "summary": "string"
     }
     ```

<br>

## 👉🏻 Service Architecture

<img width="550" alt="image (7)" src="https://github.com/user-attachments/assets/1b71398f-5640-4b68-9109-7989b87092b6" />


<br>
<br>

## 💡 Challenges & Solutions

### 1. 유튜브 영상에서 장소 정보를 추출하는 과정에서의 어려움

- 먼저 유튜브 API를 사용하여 크롤링을 진행하려고 했으나, 자신이 올린 영상만 가능한 문제점이 있었다.
- 다음으로 유튜브의 자동 자막을 떠올렸고, 자막을 크롤링하였다.
- 그러나, 자동 자막이 생성되지 않는 영상들이 있었다.
- 그런 영상들의 경우 정보를 추출할 수 없으므로 상세 정보까지 크롤링하여 두 가지 정보(자막 & 상세 정보) 모두 합쳐서 장소 정보를 추출하고 요약하는 방식으로 문제를 해결하였다.

### 2. 프랜차이즈 중복 문제 (ex. 스타벅스)

- 유튜버가 스타벅스를 방문했을 경우 스타벅스까지 뜨게 되는데, 스타벅스는 한 지역에도 매장이 너무 많았다.
- 이 경우에는 거리 기반 추천 알고리즘을 적용하여 가까운 매장을 선택하는 것으로 해결하였다.

### 3. 백엔드 서버와 AI 서버의 API 연결이 안되는 문제

- AI 서버에서 FastAPI를 가지고 백엔드로 넘겨주었고, 그 데이터를 백엔드에서 파싱해야했었다.
- 하지만, AI 서버는 잘 돌아가는 반면 백엔드 서버에서 데이터의 파싱이 계속해서 실패했었다.
- 백엔드에서 차도가 없어서 직접 백엔드 코드를 살펴보았고, AI 서버의 코드를 변경하는 방식으로 해결을 하였다.

<br>


