import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://world-weather.ru/pogoda/russia/saint_petersburg/"
HTML_FILE = "weather.html"


def get_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 YaBrowser/25.12.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML сохранён в {HTML_FILE}")
        return html
    except Exception as e:
        print("При выполнении запроса произошла ошибка:", e)
        return None


def load_html() -> str:
    """Дописал функцию load_html() - потому-что не удобно каждый раз перезагружая отладку (для того что бы в процессе отладки добавлялись
    новые преременные) - это в свою очерерь заного подгружает html файл со страницы,что не хорошо - можно получить блокировку,
    данная функции сразу безопасно сохраняет код страницы и дальше мы уже работаем с этим кодом в отладке повторно его не подгружая
    поэтому-при запуске программы так же появился файл HTML_FILE = 'weather.html' - который сохранен в программе в качестве константы
    """
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            html = f.read()
        print("HTML загружен из файла")
        return html
    except FileNotFoundError:
        print(f"Файл '{HTML_FILE}' не найден. Загружаю с сайта...")
        return get_html(BASE_URL)


def parse_all_weather(html: str) -> dict:
    """У меня не получилось разбить все 3 уровня вложенности цикла на отдельные функции - я запутался и потерял много времени,решил
    сделать с помощью вложенных циклов в одной функции - как изначально мы и планировали на занятия в группе
    """

    soup = BeautifulSoup(html, "html.parser")
    all_days = soup.find_all("div", class_="weather-short")
    result = {}
    for day_block in all_days:  # сымый верхний цикл  - получения - дат и дней недели
        date_element = day_block.find("div", class_="dates")
        if not date_element:
            continue
        date_key = date_element.get_text(strip=True)

        times_of_day = {}  # подготовка словаря для переудов дня
        periods = [
            "night",
            "morning",
            "day",
            "evening",
        ]  # подготовка списка с периудами( так как они известны)
        for period in periods:  # цикл по периудам - внутренний цикл
            row = day_block.find("tr", class_=period)
            if not row:
                continue

            # получение всех данных внутри периуда
            temperature = row.find("td", class_="weather-temperature").get_text(
                strip=True
            )
            feels_like = row.find("td", class_="weather-feeling").get_text(strip=True)
            precipitation = row.find("td", class_="weather-probability").get_text(
                strip=True
            )
            pressure = row.find("td", class_="weather-pressure").get_text(strip=True)
            humidity = row.find("td", class_="weather-humidity").get_text(strip=True)
            wind_speed = (
                row.find("td", class_="weather-wind")
                .find_all("span")[-1]
                .get_text(strip=True)
            )
            # запись данных в словарь - где ключами являются - периоды
            times_of_day[period] = {
                "temperature": temperature,
                "feels_like": feels_like,
                "precipitation": precipitation,
                "pressure": pressure,
                "wind_speed_m_s": wind_speed,
                "humidity": humidity,
            }
        result[date_key] = (
            times_of_day  # добавление всех данных во внешнем цикле где ключами являются - даты и дни недели
        )

    return result


if __name__ == "__main__":
    html = (
        load_html()
    )  # если html не загружен - загрузить его - загрузка иже сохраненного кода страницы
    weather_data = parse_all_weather(html)  # парсинг всех данных

    """Запись данных в файл с расширением json"""

    with open("weather.json", "w", encoding="utf-8") as f:
        json.dump(weather_data, f, ensure_ascii=False, indent=2)
        print("Данные сохранены в weather.json")
