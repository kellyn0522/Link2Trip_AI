from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# ✅ Ubuntu에 맞춘 Chrome & ChromeDriver 설정
def get_chrome_driver():
    options = Options()
    options.add_argument("--headless")  # 브라우저 창 숨기기
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # ✅ Ubuntu에서는 직접 설치된 Chromium과 Chromedriver를 사용하도록 설정
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/local/bin/chromedriver")

    # ✅ Ubuntu에 맞게 WebDriver 실행
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# 🎯 유튜브 데이터 크롤링 함수
def get_youtube_data(video_url):
    driver = get_chrome_driver()
    wait = WebDriverWait(driver, 15)

    try:
        print(f"🔗 URL 접근 중: {video_url}")
        driver.get(video_url)

        # 🎬 영상 제목 가져오기
        try:
            title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#title > h1 > yt-formatted-string"))
            )
            title = title_element.text
            print(f"📌 영상 제목: {title}")
        except:
            title = "제목 없음"
            print("⚠️ 제목을 찾을 수 없습니다.")

        # 📜 영상 설명 가져오기 (더보기 버튼 클릭)
        try:
            expand_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#expand"))
            )
            driver.execute_script("arguments[0].click();", expand_button)

            video_detail_element = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#description-inline-expander > yt-attributed-string")
                )
            )
            video_detail = video_detail_element.text
            print(f"📝 설명: {video_detail[:100]}...")  # 100자까지만 미리보기
        except:
            video_detail = "설명 없음"
            print("⚠️ 설명을 찾을 수 없습니다.")

        return {
            "title": title,
            "video_detail": video_detail
        }

    finally:
        driver.quit()

# ✅ 실행 예시
if __name__ == "__main__":
    YOUTUBE_URL = "https://www.youtube.com/watch?v=R4AlFMAgDz0"
    youtube_data = get_youtube_data(YOUTUBE_URL)

    print("\n=== 최종 결과 ===")
    print(f"📌 영상 제목: {youtube_data['title']}")
    print(f"📝 설명: {youtube_data['video_detail']}\n")
