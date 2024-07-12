import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# SQLite 데이터베이스 연결
conn = sqlite3.connect('medical_terms2.db')
cursor = conn.cursor()

# 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS terms
(id INTEGER PRIMARY KEY, term TEXT, explanation TEXT)
''')

# 기본 URL
base_url = "https://www.amc.seoul.kr/asan/healthinfo/easymediterm/easyMediTermDetail.do"

# dictId 1부터 5016까지 순회
for dict_id in range(1, 5017):
    url = f"{base_url}?dictId={dict_id}"
    
    # 웹페이지 가져오기
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # #popupWrap > div.popHeader > h1 선택 (term)
    term_element = soup.select_one("#popupWrap > div.popHeader > h1")
    
    # #popupWrap > div.drugContent > div.description > dl > dd 선택 (explanation)
    explanation_element = soup.select_one("#popupWrap > div.drugContent > div.description > dl > dd")
    
    if term_element and explanation_element:
        term = term_element.text.strip()
        explanation = explanation_element.text.strip()
        
        # 데이터베이스에 삽입
        cursor.execute('INSERT INTO terms (term, explanation) VALUES (?, ?)', (term, explanation))
    
    print(f"Term {dict_id} processed.")
    
    # 서버에 과도한 부하를 주지 않기 위해 잠시 대기
    time.sleep(0.1)
    
    # 100개의 용어마다 변경사항 저장
    if dict_id % 100 == 0:
        conn.commit()
        print(f"Data saved up to term {dict_id}")

# 마지막 변경사항 저장
conn.commit()

# 연결 종료
conn.close()

print("Scraping completed and terms saved to SQLite database.")