import os
import mysql.connector
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 초기화 (기존과 동일)
service_account_info = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT'))
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)
db_fire = firestore.client()

# MySQL 연결 함수
def get_mysql_connection():
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST'),          # 네이버 클라우드 호스트 주소 (예: xxxx.mysql.ncloud.com)
        user=os.environ.get('MYSQL_USER'),          # 생성 시 설정한 ID
        password=os.environ.get('MYSQL_PASSWORD'),  # 생성 시 설정한 비밀번호
        database=os.environ.get('MYSQL_DATABASE')   # 생성 시 설정한 기본 DB명
    )

def save_to_mysql(data):
    cnx = get_mysql_connection()
    cursor = cnx.cursor()
    
    # 예시: weather_table에 데이터 삽입
    query = "INSERT INTO weather_table (city, temp, status) VALUES (%s, %s, %s)"
    for item in data:
        cursor.execute(query, (item['city'], item['temperature'], item['weather_status']))
    
    cnx.commit()
    cursor.close()
    cnx.close()
