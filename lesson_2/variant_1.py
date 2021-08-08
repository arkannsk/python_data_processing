# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы)
# с сайтов Superjob и HH. Приложение должно анализировать несколько страниц сайта
# (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:

# Наименование вакансии.
# Предлагаемую зарплату (отдельно минимальную и максимальную).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.  По желанию можно добавить ещё параметры вакансии
# (например, работодателя и расположение). Структура должна быть одинаковая для вакансий с обоих сайтов.
# Общий результат можно вывести с помощью dataFrame через pandas.


import pandas as pd
import requests
import lxml
import urllib.parse
from bs4 import BeautifulSoup
from fake_headers import Headers

'''
1 000 – 10 000 руб.
от 1 000 руб.
до 1 000 руб.
договорная
'''


def parse_hh_wage(wage_source):
    wage_source = wage_source.replace('\u202f', '')

    if len(wage_source.split('–')) > 1:
        wage_split = wage_source.split('–')
        min_w = wage_split[0].replace(' ', '')
        max_w = wage_split[1].strip().split(' ')[0]
        cur = wage_split[1].strip().split(' ')[-1]

        return int(min_w), int(max_w), cur, True
    else:
        wage_split = wage_source.split(' ')
        if len(wage_split) == 3:
            if wage_split[0].strip().lower() == 'от':
                min_w = wage_split[1].replace(' ', '')
                cur = wage_split[2].strip()
                return int(min_w), None, cur, True
            elif wage_split[0].strip().lower() == 'до':
                max_w = wage_split[1].replace(' ', '')
                cur = wage_split[2].strip()
                return None, int(max_w), cur, True

    return None, None, None, False


def parse_superjob_wage(wage_source):
    cur = wage_source.split()[-1]
    first_word = wage_source.split()[0]
    wage_source = wage_source.replace('\xa0', '')

    nums = []
    i = 0
    while i <= len(wage_source) - 1:
        if wage_source[i].isdigit():
            tmp_num = ''
            for j in range(i, len(wage_source) - 1):
                if not wage_source[j].isdigit():
                    i = j
                    nums.append(tmp_num)
                    break
                else:
                    tmp_num += wage_source[j]
        else:
            i += 1

    if len(nums) == 0:
        return None, None, None, False
    elif len(nums) == 1:
        if first_word == 'от':
            return int(nums[0]), None, cur, True
        elif first_word == 'до':
            return None, int(nums[0]), cur, True
    elif len(nums) == 2:
        return int(nums[0]), int(nums[1]), cur, True

    return None, None, None, False


headers = Headers(headers=True).generate()
pages = 3
query = 'Frontend-разработчик'

hh_url = f'https://hh.ru/search/vacancy?&text={urllib.parse.quote(query)}'

hh_vacancies = []
for i in range(0, pages):
    hh_response = requests.get(hh_url + f'&page={i}', headers=headers)
    soup_hh = BeautifulSoup(hh_response.text, 'lxml')
    hh_vacancies += soup_hh.find_all(class_='vacancy-serp-item')


result = []
for val in hh_vacancies:
    tmp = {'source_site': 'hh.ru'}

    vacancy = BeautifulSoup(str(val), 'lxml')
    title = vacancy.find(attrs={"data-qa": 'vacancy-serp__vacancy-title'})
    if title is not None:
        tmp['title'] = title.text
        tmp['url'] = title['href']

    wage = vacancy.find(attrs={"data-qa": 'vacancy-serp__vacancy-compensation'})
    if wage is not None:
        min_wage, max_wage, currency, is_indicated = parse_hh_wage(wage.text)
        tmp['min_wage'] = min_wage
        tmp['max_wage'] = max_wage
        tmp['wage_currency'] = currency
        tmp['wage_is_indicated'] = is_indicated
    else:
        tmp['wage_is_indicated'] = False

    city = vacancy.find(attrs={"data-qa": 'vacancy-serp__vacancy-address'})
    if city is not None:
        tmp['city'] = city.text

    short_description = vacancy.find(attrs={"data-qa": 'vacancy-serp__vacancy_snippet_responsibility'})
    if short_description is not None:
        tmp['short_description'] = short_description.text

    result.append(tmp)


superjob_url = f'https://superjob.ru/vacancy/search/?keywords={urllib.parse.quote(query)}'

superjob_vacancies = []
for i in range(1, pages + 1):
    superjob_response = requests.get(superjob_url + f'&page={i}', headers=headers)
    soup_superjob = BeautifulSoup(superjob_response.text, 'lxml')
    superjob_vacancies += soup_superjob.find_all(class_='f-test-vacancy-item')


for val in superjob_vacancies:
    tmp = {'source_site': 'superjob.ru'}

    vacancy = BeautifulSoup(str(val), 'lxml')
    title = vacancy.find(class_='_1UJAN')
    if title is not None:
        tmp['title'] = title.text
        tmp['url'] = 'https://www.superjob.ru' + title['href']

    wage = vacancy.select_one('.f-test-text-company-item-salary > span:nth-child(1)')
    if wage is not None:
        min_wage, max_wage, currency, is_indicated = parse_superjob_wage(wage.text.strip())
        tmp['min_wage'] = min_wage
        tmp['max_wage'] = max_wage
        tmp['wage_currency'] = currency
        tmp['wage_is_indicated'] = is_indicated
    else:
        tmp['wage_is_indicated'] = False

    city = vacancy.select_one('.f-test-text-company-item-location span:nth-child(3)')
    if city is not None:
        tmp['city'] = city.text

    short_description = vacancy.select_one(
        'div.HSTPm._3C76h._10Aay._2_FIo._1tH7S > span._1h3Zg._38T7m.e5P5i._2hCDz._2ZsgW._2SvHc')
    if short_description is not None:
        tmp['short_description'] = short_description.text

    result.append(tmp)

df = pd.DataFrame(result)
print(df.to_string())
