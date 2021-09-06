# Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import json
import requests

url = 'https://api.github.com/users/arkannsk/repos'

response = requests.get(url).json()

with open("github_response.json", "w") as outfile:
    json.dump(response, outfile)
