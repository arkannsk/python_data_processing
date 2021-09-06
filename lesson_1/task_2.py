# Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import json
import requests

api_token = '4ff7c4792d91d1359a7c95c11e002ddc'
url = f'https://api.openweathermap.org/data/2.5/weather?q=Novosibirsk&appid={api_token}'

response = requests.get(url).json()

with open("task2_response.json", "w") as outfile:
    json.dump(response, outfile)

