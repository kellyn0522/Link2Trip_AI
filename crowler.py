from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import subprocess
import time
import os

# Chrome 및 ChromeDriver 버전 자동 맞추기
def get_chrome_driver():
    # MacOS용 Chrome 실행 경로
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    # 현재 Chrome 버전 확인 (MacOS용)
    try:
        chrome_version = subprocess.run([chrome_path, "--version"], capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        print("❌ Google Chrome이 설치되지 않았거나 경로를 찾을 수 없습니다.")
        print("🔹 Chrome이 설치되어 있는지 확인하고, '/Applications/Google Chrome.app'에 있는지 확인하세요.")
        exit(1)

    print(f"🌐 현재 Chrome 버전: {chrome_version}")

    # Chrome 옵션 설정 (MacOS에서 실행 가능하도록)
    options = Options()
    options.binary_location = chrome_path  # MacOS에서 Chrome 실행 경로 지정
    options.add_argument("--headless")  # 브라우저 창 숨기기 (클라우드 배포 시 필수)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")

    # ChromeDriverManager를 사용하여 Chrome 버전에 맞는 드라이버 설치
    driver_path = ChromeDriverManager().install()
    return webdriver.Chrome(service=Service(driver_path), options=options)

'''
# Selenium WebDriver 설정
options = Options()
options.add_argument("--headless")  # 배포 시 활성화 (개발 시 주석 처리)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
'''

# 유튜브 데이터 크롤링 함수
def get_youtube_data(video_url):
    driver = get_chrome_driver() # webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    try : 
        driver.get(video_url)   # 유튜브 페이지 열음

        # 영상 제목 가져오기
        try:
            title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#title > h1 > yt-formatted-string"))
            )
            title = title_element.text
        except:
            title = "제목 없음"

        # 더보기 버튼 클릭 후 영상 설명 가져오기
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
        except:
            video_detail = "설명 없음"
            
        return {
            "title": title,
            "video_detail": video_detail,
        }
    finally:
        driver.quit()


# # 실행
# youtube_data = get_youtube_data(YOUTUBE_URL)

# wait = WebDriverWait(driver, 5)

# # ✅ 결과 출력
# print(f"📌 영상 제목: {youtube_data['title']}")
# print(f"📝 설명: {youtube_data['video_detail']}\n")

# # print("💬 댓글:")
# # for idx, comment in enumerate(youtube_data["comments"], start=1):
# #     print(f"{idx}. {comment}")

# # 드라이버 종료
# driver.quit()

