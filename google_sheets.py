import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GoogleSheets:
    def __init__(self, credentials_file, spreadsheet_id):
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.service = self._authenticate()
        self.sheet_service = gspread.authorize(self._get_gspread_credentials())

    def _authenticate(self):
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_file, scope)
        return build('sheets', 'v4', credentials=credentials)

    def _get_gspread_credentials(self):
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        return ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_file, scope)

    def open_spreadsheet(self):
        return self.sheet_service.open_by_key(self.spreadsheet_id)

    def get_sheet(self, sheet_name):
        spreadsheet = self.open_spreadsheet()
        try:
            return spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            return spreadsheet.add_worksheet(sheet_name, rows=100, cols=20)

    def write_data(self, sheet_name, data):
        try:
            sheet = self.get_sheet(sheet_name)

            sheet.clear()

            headers = [
                "Вид сайта", "Домен", "Дата", "Google SC Кол-во ссылок",
                "Средняя позиция (1 месяц)", "Средняя позиция (3 месяца)",
                "Кол-во ключей", "Индекс страниц", "Страницы не в индексе",
                "Яндекс Метрика (месяц)", "Яндекс Вебмастер (YW) Кол-во проиндексированных страниц",
                "YW кол-во не проиндексированных страниц"
            ]
            sheet.append_row(headers)

            for row in data:
                date = row["dimensions"][0]["name"]
                visits = row["metrics"][0]
                new_row = ["", "", date, "", "", "", "", "", "", visits, "", ""]
                sheet.append_row(new_row)

        except Exception as e:
            print(f"Ошибка при записи данных: {e}")

    def format_cells(self, sheet_name, range_name, background_color):
        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": 0,
                            "endRowIndex": 10,
                            "startColumnIndex": 0,
                            "endColumnIndex": 10
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": 0.8,
                                    "green": 0.8,
                                    "blue": 0.8
                                }
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor)"
                    }
                }
            ]
        }
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id, body=body).execute()


if __name__ == "__main__":
    import config

    gsheets = GoogleSheets(config.GOOGLE_CREDS_FILE, config.SPREADSHEET_ID)

    data = [
        {"dimensions": [{"name": "2023-01-01"}, {"name": "Прямой трафик"}],
         "metrics": [100, 50]},
        {"dimensions": [{"name": "2023-01-02"}, {"name": "Реклама"}],
         "metrics": [200, 100]}
    ]

    gsheets.write_data("Лист1", data)