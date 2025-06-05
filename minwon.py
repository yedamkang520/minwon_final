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