import config
import logging
from yandex_metrica import YandexMetrica
from google_sheets import GoogleSheets
from gsc_api import get_gsc_data, write_to_sheets

def main():
    try:
        metrika = YandexMetrica(config.YANDEX_TOKEN, config.COUNTER_ID)
        metrika.check_data()

        gsheets = GoogleSheets(config.GOOGLE_CREDS_FILE, config.SPREADSHEET_ID)

        print("ID таблицы:", config.SPREADSHEET_ID)
        print("Имя листа:", "Лист1")

        metrics = config.METRICS
        dimensions = config.DIMENSIONS
        date_range = config.DATE_RANGE

        params = {
            "ids": config.COUNTER_ID,
            "metrics": metrics,
            "dimensions": dimensions,
            "date1": date_range["start"],
            "date2": date_range["end"],
            "limit": config.LIMIT
        }

        logging.info("Получение данных из Яндекс.Метрики...")
        data = metrika.get_data(params)

        if data and "data" in data:
            logging.info("Данные получены успешно.")
            data = data["data"]

            logging.info("Запись данных из Яндекс.Метрики в Google Таблицы...")
            gsheets.write_data("Лист1", data)
            logging.info("Данные записаны успешно.")

        site_url = 'https://example.com'
        gsc_data = get_gsc_data(site_url)

        logging.info("Запись данных из Google Search Console в Google Таблицы...")
        write_to_sheets(gsc_data, 'Лист2')
        logging.info("Данные записаны успешно.")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()