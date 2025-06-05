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