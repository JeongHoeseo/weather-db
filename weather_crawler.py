import os
import json
import time
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Firebase 초기화 (GitHub Secrets 활용)
service_account_info = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT'))
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)
db = firestore.client()

# 2. 크롤링 함수
def get_weather_data():
    weather_list = []
    url = "https://weather.nate.com/" 
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        forecast_items = soup.select(".list_weather > li") 
        
        for item in forecast_items:
            # Firebase에 저장할 딕셔너리 형태
            weather_list.append({
                "city": "아산시",
                "forecast_date": item.select_one(".date").text.strip(),
                "forecast_time": "09:00",
                "weather_status": item.select_one(".status").text.strip(),
                "temperature": item.select_one(".temp").text.strip(),
                "source": "Nate Weather",
                "collected_at": firestore.SERVER_TIMESTAMP # 서버 시간 저장
            })
    except Exception as e:
        print(f"크롤링 오류: {e}")
    return weather_list

# 3. Firebase 직행 저장 로직
def save_to_firebase():
    data = get_weather_data()
    for item in data:
        # 날짜와 시간을 조합하여 고유 ID 생성 (중복 방지)
        doc_id = f"asan_{item['forecast_date']}_{item['forecast_time'].replace(':', '')}"
        db.collection("asan_weather_forecast").document(doc_id).set(item)
    print(f"{len(data)}건 Firebase 저장 완료.")

if __name__ == "__main__":
    save_to_firebase()
