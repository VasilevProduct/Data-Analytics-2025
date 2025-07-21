import easyocr
import re
import os
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Настройки Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1DN6uvLTVhNkmg_UrxXtL62g6PT6FixXR8lHNpp7OZvI'  # вставь сюда ID своей таблицы
SHEET_NAME = 'Sheet1'

# Аутентификация Google API
def get_sheets_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('sheets', 'v4', credentials=creds)
    return service

# Извлечение текста с изображения с помощью EasyOCR
reader = easyocr.Reader(['ru', 'en'])

def extract_text(image_path):
    return ' '.join(reader.readtext(image_path, detail=0))

# Парсинг данных из текста (пример)
def parse_receipt(text):
    # Примерные шаблоны для даты и суммы
    date_pattern = r'(\d{2}[./-]\d{2}[./-]\d{4})'
    sum_pattern = r'(\d+[.,]?\d*)\s*(руб|RUB|₽)?'

    date_match = re.search(date_pattern, text)
    sum_match = re.search(sum_pattern, text)

    date = date_match.group(1) if date_match else ""
    amount = sum_match.group(1) if sum_match else ""
    # Пример получения названия магазина (просто первая строка)
    store = text.split('\n')[0] if '\n' in text else text[:20]

    return [date, amount, store]

# Запись данных в Google Sheets
def append_to_sheet(service, values):
    body = {
        'values': [values]
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_NAME,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    return result

# Основная логика
if __name__ == "__main__":
    service = get_sheets_service()

    folder_path = "path_to_receipts"  # путь к папке с изображениями
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            text = extract_text(image_path)
            data = parse_receipt(text)
            append_to_sheet(service, data)
            print(f'Обработано {filename}: {data}')