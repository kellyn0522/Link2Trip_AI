from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time

# 🚀 Selenium WebDriver 설정
options = Options()
options.add_argument("--headless")  # 배포 시 활성화 (개발 시 주석 처리)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")


# 유튜브 URL 설정
# YOUTUBE_URL = "https://www.youtube.com/watch?v=R4AlFMAgDz0"

# 🎯 유튜브 데이터 크롤링 함수
def get_youtube_data(video_url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
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

        # # ✅ 3. 댓글 가져오기
        # # 댓글이 포함된 iframe이 로드될 때까지 대기
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # # 스크롤을 내려 댓글을 로드하는 함수
        # def scroll_to_load_comments(scroll_count=1, wait_time=1):
        #     body = driver.find_element(By.TAG_NAME, "body")
            
        #     for _ in range(scroll_count):
        #         body.send_keys(Keys.PAGE_DOWN)  # 페이지 다운 키 입력
        #         time.sleep(wait_time)  # 스크롤 후 대기 (로딩 기다림)
            
        #     time.sleep(2)  # 추가 대기 (완전한 로딩을 위해)

        # # 댓글을 불러오기 위해 스크롤 수행
        # scroll_to_load_comments()

        # # 댓글 요소 가져오기
        # comments = []
        # elements = driver.find_elements(By.CSS_SELECTOR, "span.yt-core-attributed-string.yt-core-attributed-string--white-space-pre-wrap")

        # # 댓글 개수 확인 후 12번째 댓글 출력
        # if len(elements) > 11:
        #     twelfth_comment = elements[11].text
        #     print(f"12번째 댓글: {twelfth_comment}")
        # else:
        #     print("❌ 댓글 개수가 충분하지 않음.")

        # # 요소 내용 저장
        # for element in elements:
        #     comments.append(element.text)

        return {
            "title": title,
            "video_detail": video_detail,
            #"comments": comments
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