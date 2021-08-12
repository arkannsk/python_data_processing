"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
 записывающую собранные вакансии в созданную БД.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
"""
import json
from pymongo import MongoClient, ASCENDING


# Проигнорируем курсы валют
def get_wage_gt(db_collection, wage):
    result = db_collection.find(
        {'$and': [
            {'wage_is_indicated': True},
            {'$or': [
                {'min_wage': {'$gt': wage}},
                {'max_wage': {'$gt': wage}}
            ]
            },
        ]
        }
    )
    return result


client = MongoClient('localhost', 27017, username='root', password='password')

db = client['test_database']

db.test_collection.drop()

collection = db.test_collection

# используем данные с прошлого урока через файл, для экономии времени
with open('result_from_lesson_2.json') as f:
    file_data = json.load(f)

collection.insert_many(file_data)

data = get_wage_gt(collection, 10000)

for document in data:
    print(document)

# Лучше конечно id объявления + источник парсинга брать(но он предварительно не парсился), для примера можно взять url
collection.create_index([("url", ASCENDING)], unique=True)

base_count = collection.count_documents({})

for row in file_data:
    collection.update_one({"url": row['url']}, {'$set': row})

after_insert_count = collection.count_documents({})

print(f'Начальное кол-во: {base_count}   После вставки: {after_insert_count}')

client.close()
