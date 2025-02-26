import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)

# 모델 선택
model = genai.GenerativeModel("gemini-pro")

from youtube_transcript_api import YouTubeTranscriptApi

# URL에서 비디오 ID 추출
def get_video_id(url):
    if "youtube.com" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be" in url:
        return url.split("/")[-1]
    return None

# 유튜브 자막 가져옴
def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        text = " ".join([t['text'] for t in transcript])
        return text
    except Exception as e:
        return f"자막을 가져오는 데 실패했습니다: {e}"

# Gemini 사용하여 텍스트 요약
def summarize_text_with_gemini(text):
    response = model.generate_content(f"다음 유튜브 영상의 내용을 여행 장소 중심으로 요약해줘. 관광지나 상호명이 올바르게 나왔으면 좋겠어. 장소마다 특징을 한 줄로 정리해서 같이 설명해줘. :\n\n{text}")
    return response.text

# 유튜브 URL 입력
youtube_url = input("유튜브 URL을 입력하세요: ")

# 비디오 ID 추출 및 자막 가져오기
video_id = get_video_id(youtube_url)
if not video_id:
    print("올바른 유튜브 URL을 입력하세요.")
else:
    transcript_text = get_youtube_transcript(video_id)

    if "자막을 가져오는 데 실패했습니다" not in transcript_text:
        # Gemini API로 요약
        summary = summarize_text_with_gemini(transcript_text)
        print("\n📌 유튜브 영상 요약 📌\n")
        print(summary)
    else:
        print(transcript_text)
