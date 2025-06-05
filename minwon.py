import os
import pickle
import streamlit as st
from datetime import date
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from streamlit_folium import st_folium
import folium

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TOKEN_PATH = 'token.pickle'
CLIENT_SECRET_FILE = '/Users/damifasol/Documents/year2sem2/info_adv_program/client_secret_878177295372-6jlhs563t0fgeq097qdcns7to7ucjdch.apps.googleusercontent.com.json'
SPREADSHEET_ID = "1OaWf-VthvDWe3ul-8oyW39YkSzQdQAY9rBwFXGI07lI"

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token_file:
            creds = pickle.load(token_file)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token_file:
            pickle.dump(creds, token_file)
    return creds

creds = get_credentials()
service = build('sheets', 'v4', credentials=creds)

st.title("📌 민원 접수 시스템")

# 구글 시트 연동 함수
def append_to_sheet(spreadsheet_id, _values):
    try:
        body = {"values": _values}
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range="Sheet1!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def read_sheet(spreadsheet_id):
    try:
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range="Sheet1!A2:E")
            .execute()
        )
        return result.get("values", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
    
    st.subheader("지도에서 민원 위치 선택")

# 지도 표시 및 클릭 처리
yonsei_center = [37.565784, 126.938572]  # 연세대학교 중심 좌표
m = folium.Map(location=yonsei_center, zoom_start=16)
m.add_child(folium.LatLngPopup())

# 이미 등록된 민원 마커 추가
existing_data = read_sheet(SPREADSHEET_ID)
for row in existing_data:
    try:
        content, latlon, author, date_str = row
        lat, lon = map(float, latlon.split(","))
        folium.Marker(
            location=[lat, lon],
            popup=f"{date_str} | {author}: {content}",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
    except Exception as e:
        print("Marker Error:", e)

map_data = st_folium(m, width=700, height=500)

if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.session_state["selected_lat"] = lat
    st.session_state["selected_lon"] = lon
    st.success(f"선택된 위치는 위도 {lat:.6f}, 경도 {lon:.6f} 입니다. 밑에서 이어서 민원을 작성해주세요!")

# 민원 클래스
class CivilComplaint:
    def __init__(self, author, content, lat, lon, date):
        self.author = author
        self.content = content
        self.lat = lat
        self.lon = lon
        self.date = date

    def __str__(self):
        return f"{self.date} | {self.author} | {self.content} | 좌표: ({self.lat}, {self.lon})"
    
st.subheader("민원 접수")

lat = st.number_input("위도 입력", format="%.6f", value=st.session_state.get("selected_lat", 0.0))
lon = st.number_input("경도 입력", format="%.6f", value=st.session_state.get("selected_lon", 0.0))
author = st.text_input("작성자")
content = st.text_area("민원 내용")
created_at = st.date_input("작성 날짜", value=date.today())
created_at_str = created_at.isoformat()

if st.button("민원 제출"):
    if author and content and lat and lon and created_at:
        complaint = CivilComplaint(author, content, lat, lon, created_at)
        st.success("민원이 저장되었습니다!")
        st.write("입력한 민원:", str(complaint))
        append_to_sheet(SPREADSHEET_ID, [[content, f"{lat},{lon}", author, created_at.isoformat()]])
    else:
        st.error("모든 항목을 입력해주세요.")

# 민원 조회
st.subheader("민원 목록 조회")
data = read_sheet(SPREADSHEET_ID)

if data:
    st.write("민원 개수:", len(data))
    st.write("최근 민원:")
    for row in data[-5:][::-1]:
        try:
            content, latlon, author, date = row
            lat, lon = map(float, latlon.split(","))
            st.text(f"{date} | {author}: {content} @ ({lat}, {lon})")
        except:
            continue

    st.subheader("작성자 민원 조회")
    target_author = st.text_input("작성자 이름으로 검색")
    if st.button("조회"):
        filtered = [r for r in data if len(r) >= 4 and r[2] == target_author]
        if filtered:
            for r in filtered:
                st.text(f"{r[3]} | {r[2]}: {r[0]}")
        else:
            st.write("해당 작성자의 민원이 없습니다.")

    date_counts = {}
    for row in data:
        if len(row) >= 4:
            d = row[3]
            date_counts[d] = date_counts.get(d, 0) + 1

    if date_counts:
        st.subheader("📈 날짜별 민원 수")
        st.bar_chart(date_counts)
else:
    st.write("아직 등록된 민원이 없습니다.")