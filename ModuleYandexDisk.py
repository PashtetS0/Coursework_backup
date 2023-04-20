import requests
from pprint import pprint

class YandexDisk:

    '''
    Модуль содержит методы для работы с Яндекс Диск.

    Доступны методы:

        upload_file()
            Принимает аргументы:
                disk_file_path = Путь к директории для размещения файла
                filename = Имя, с которым файл будет записан

        upload_url()
            Принимает аргументы:
                disk_file_path = Путь к директории для размещения файла
                targ_url = URL данные с которого нужно записать

        directory()
            Принимает аргументы:
                path = Путь к директории которую нужно создать или удалить
                args = Кортеж параметров:
                    1) Метод - PUT / DELETE (PUT для создания директории, DELETE для удаления)
                    2) Параметр 'false' - если удалять в корзину, или 'true' для удания безвозвратно

        info()
            Принимает аргумент:
                path = Путь к файлу или директории информацию о которых нужно получить
            Возвращает JSON с ответом API на запрос
    '''

    def __init__(self, token):
        self.token = token

    def _get_headers(self):  # метод возвращает заголовки для авторизации
        return {  # словарь из 2х элементов
            'Content-Type': 'application/json',  # тип данных json
            'Authorization': f'OAuth {self.token}',  # в формате f-строк, авторизация по токену
            }

    def _get_upload_link(self, disk_file_path):  # внутренний метод получения ссылки на upload файла
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"  # из API URL на получение ссылки
        headers = self._get_headers()  # обращение к методу получения заголовков (для авторизации)
        params = {"path": disk_file_path, "overwrite": "true"}  # создание словаря параметров
        response = requests.get(url=upload_url, headers=headers, params=params)  # выполнение запроса
        return response.json()  # Возврат полученных данных с помощью функции json()

    def upload_file(self, disk_file_path, filename):  # Метод загружает файл на диск
        data = self._get_upload_link(disk_file_path=disk_file_path)  #
        url = data.get('href')  # Выделение ссылки (hypertext reference — гипертекстовая ссылка) словарный метод get() из data
        response = requests.put(url=url, data=open(filename, 'rb'))  # Загрузка файла. В Питоне тело передается в атрибуте data в байтовом виде. С помощью запроса put по урлу. Авторизационные заголовки не требуются, т.к. урл для закачки их уже содержит.
        if response.status_code != 201:  # Если не вернулся код 201
            print(response)  #

    def upload_url(self, disk_file_path, targ_url):  # Метод загружает файл по URL'у на диск
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self._get_headers()  # обращение к методу получения заголовков (для авторизации)
        params = {"path": disk_file_path, "url": targ_url}  # создание словаря параметров
        response = requests.post(url=upload_url, headers=headers, params=params)  # Загрузка по URL'у на диск
        if response.status_code != 202:  # Если не вернулся код 202
            # print(response["message"])  #
            print(response)  #

    def directory(self, path, args):
        method, to_trash = args
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self._get_headers()  # обращение к методу получения заголовков (для авторизации)
        if method == 'put':
            params = {'path': path}  # создание словаря параметров
            response = requests.put(url=url, headers=headers, params=params)  # выполнение запроса
            if response.status_code != 201:
                res = response.json()
                print(f'При создании директории {path} произошла ошибка:\n')
                print(f"Описание - {res['description']}")
                print(f"Ошибка - {res['error']}")
                print(f"Сообщение - {res['message']}\n")
                print('Работа программы прервана')
                exit()
            print(f'Код завершения {response.status_code}\n\nПараметры:')
            pprint(response.json())
        if method == 'delete':
            params = {'path': path, 'permanently': to_trash}  # создание словаря параметров
            response = requests.delete(url=url, headers=headers, params=params)  # выполнение запроса
            if response.status_code == 204:
                print(f'Код завершения {response.status_code}')
                print(f'Удаление {path} успешно. Безвозвратно - {to_trash}')
            else:
                print(f'Код завершения {response.status_code}\n\nПараметры:')
                pprint(response.json())

    def info(self, path):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self._get_headers()  # обращение к методу получения заголовков (для авторизации)
        params = {'path': path}  # создание словаря параметров
        response = requests.get(url=url, headers=headers, params=params)  # выполнение запроса
        return response.json()
