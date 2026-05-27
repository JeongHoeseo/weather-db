import os
import mysql.connector
import firebase_admin
from firebase_admin import credentials, firestore
import time
import requests
from bs4 import BeautifulSoup
import json

# 1. 환경 설정 및 DB/Firebase 초기화
# GitHub Secrets에서 인증 키 내용을 JSON 파일로 생성
service_account_info = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT'))
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)
db = firestore.client()

# MySQL 연결 (os.environ.get 사용)
cnx = mysql.connector.connect(
    host=os.environ.get('MYSQL_HOST'),
    user=os.environ.get('MYSQL_USER'),
    password=os.environ.get('MYSQL_PASSWORD'),
    database=os.environ.get('MYSQL_DATABASE')
)
cursor = cnx.cursor(dictionary=True)

# 2. 크롤링 함수 (Nate 날씨)
def get_weather_data():
    weather_list = []
    url = "https://news.nate.com/weather?areaCode=11C20302" 
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        forecast_items = soup.select(".list_weather > li") 
        
        for item in forecast_items:
            weather_list.append({
                "city": "아산시",
                "forecast_date": item.select_one(".date").text.strip(),
                "forecast_time": "09:00",
                "weather_status": item.select_one(".status").text.strip(),
                "temperature": item.select_one(".temp").text.strip(),
                "source": "Nate Weather"
            })
    except Exception as e:
        print(f"크롤링 오류: {e}")
    return weather_list

# 3. 저장 및 동기화 로직
def save_and_sync():
    # 저장
    data = get_weather_data()
    sql = "INSERT IGNORE INTO weather_forecast (city, forecast_date, forecast_time, weather_status, temperature, source, collected_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())"
    for item in data:
        cursor.execute(sql, (item["city"], item["forecast_date"], item.get("forecast_time"), item["weather_status"], item.get("temperature"), item["source"]))
    cnx.commit()
    
    # 동기화
    cursor.execute("SELECT * FROM weather_forecast WHERE firebase_synced = FALSE")
    rows = cursor.fetchall()
    for row in rows:
        time_str = row['forecast_time'].replace(":", "") if row['forecast_time'] else "0000"
        doc_id = f"asan_{row['forecast_date']}_{time_str}"
        db.collection("asan_weather_forecast").document(doc_id).set(row)
        cursor.execute("UPDATE weather_forecast SET firebase_synced = TRUE WHERE id = %s", (row['id'],))
    cnx.commit()
    print(f"{len(rows)}건 처리 완료.")

# 4. 실행
if __name__ == "__main__":
    save_and_sync()
    cursor.close()
    cnx.close()
