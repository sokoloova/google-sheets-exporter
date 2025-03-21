import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class YandexMetrica:
    def __init__(self, token, counter_id):
        self.token = token
        self.counter_id = counter_id
        self.api_url = "https://api-metrika.yandex.net/stat/v1/data"
        self.headers = {
            "Authorization": f"OAuth {self.token}",
            "Content-Type": "application/json"
        }

    def get_data(self, params):
        try:
            logger.debug(f"Параметры запроса: {params}")
            # ...
            response = requests.get(self.api_url, params=params, headers=self.headers)
            logger.debug(f"URL запроса: {response.url}")
            logger.debug(f"Код ответа: {response.status_code}")
            logger.debug(f"Текст ответа: {response.text}")
            response.raise_for_status()  # Вызывает исключение для кодов ошибок HTTP
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Ошибка HTTP: {e}")
            return None
        url = 'https://api-metrika.yandex.net/stat/v1/data'
        headers = {'Autorization': f'OAuth {self.token}'}

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f'Ошибка при получении данных: {response.text}')
            return None

    def check_data(self):
        url = "https://api-metrika.yandex.net/stat/v1/data"
        params = {
            "ids": self.counter_id,
            "metrics": "ym:s:visits",
            "dimensions": "ym:s:date",
            "date1": "7daysAgo",
            "date2": "today",
            "limit": 1000
        }
        headers = {"Authorization": f"OAuth {self.token}"}

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                print("Данные получены успешно:", data["data"])
            else:
                print("Данных нет.")
        else:
            print("Ошибка при получении данных:", response.text)


def prepare_params(counter_id, metrics, dimensions, date_range, limit=1000):
    return{
        "ids": counter_id,
        "metrics": metrics,
        "dimensions": dimensions,
        "date1": date_range["start"],
        "date2": date_range["end"],
        "limit": limit
    }

if __name__ == '__main__':
    import config

    metrika = YandexMetrica(config.YANDEX_TOKEN, config.COUNTER_ID)

    metrics = "ym:s:visits,ym:s:users"
    dimensions = "ym:s:date,ym:s:trafficSource"
    date_range = {
        "start": "7daysAgo",
        "end": "today"
    }

    params = prepare_params(config.COUNTER_ID, metrics, dimensions, date_range)

    data = metrika.get_data(params)

    if data:
        print("Полученные данные:")
        print(data)