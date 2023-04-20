import requests
import os
import time
import json
from pprint import pprint
from datetime import datetime
import configparser
from alive_progress import alive_bar  # pip install alive_progress
from ModuleYandexDisk import YandexDisk
from ModuleVK import VKontakte

if __name__ == '__main__':

    def cleaner():
        if os.name == 'posix':
            return "os.system('clear')"
        else:
            return "os.system('cls')"
    clean = cleaner()

    exec(clean)

    # Получение токенов из файла ini:
    config = configparser.ConfigParser()
    config.read('tokens/tokens.ini')
    vk_token = config['TOKENS']['VK_token']
    yd_token = config['TOKENS']['YandexDisk_token']

    # Получение токенов из отдельных файлов:
    # with open('tokens/VK_token.txt', 'rt') as file_object_vk:
    #     vk_token = file_object_vk.read().strip()

    # with open('tokens/YandexDisk_token.txt', 'rt') as file_object_yd:
    #     yd_token = file_object_yd.read().strip()

    # Получение токенов из ввода пользователя:
    # vk_token = input('Введите Ваш токен Вконтакте')
    # yd_token = input('Введите Ваш токен Яндекс Диск')

    VK = VKontakte(vk_token)
    YaDi = YandexDisk(yd_token)

# **********************************************************************
    # Получение и загрузка фотографий
    # -----------------------------------------------------------------------------------------------
    # Для тестов:
    owner_id = '159222545'  # есть фото
    # owner_id = '159222547'  # приватный профиль
    # owner_id = '15954778'  # нет нужного размера (z)
    # -----------------------------------------------------------------------------------------------
    # Для боя:
    # print('Введите:')
    # owner_id = input('Введите идентификатор владельца альбома - ')
    album_id = 'wall'  # Идентификатор альбома wall
    print('По умолчанию будут сохранены фотографии из альбома "wall"')
    if input('Если желаете указать другой идентификатор альбома нажмите "y" - ') == 'y':
        album_id = input('Укажите идентификатор (wall, profile) - ')
    print()
    extended = '1'  # дополнительные поля - likes, comments, tags, can_comment, reposts)
    photo_sizes = 'z'  # Размеры фото z - 1080x1024
    print('По умолчанию будут сохранены фотографии размером 1080x1024')
    if input('Если желаете указать вручную шаблон размера сохраняемых фотографий нажмите "y" - ') == 'y':
        photo_sizes = input('Укажите размер (x - 604px, y - 807px, z - 1080x1024) - ')
    print()
    count = '5'
    print('По умолчанию будет сохранено пять фотографий')
    if input('Если желаете указать вручную количество сохраняемых фотографий нажмите "y" - ') == 'y':
        count = input('Укажите количество - ')
    data = VK.photos(owner_id, album_id, extended, photo_sizes, count).json()
    # pprint(data)
    if 'error' in data:
        exec(clean)
        print('Произошла ошибка:\n')
        print(f"Код ошибки - {data['error']['error_code']}")
        print(f"Сообщение - {data['error']['error_msg']}\n")
        print('Работа программы прервана')
        exit()

    sizes = []  # Список для сохранения доступных размеров фото
    for i in data['response']['items']:  # Проверка на существование фото с запрошенным размером
        for j in i['sizes']:
            sizes.append(j['type'])
    if photo_sizes not in sizes:
        exec(clean)
        print(f'Фотографий выбранного размера "{photo_sizes}" у пользователя не найдено.')
        print(f'Доступные размеры - {", ".join(sizes)}\n')
        print('Работа программы остановлена')
        exit()

    sd = []  # Список для сохрарения словарей с данными по фото
    for_dump = []  # Список для сохранения словарей с данными для дампа JSON
    for i in data['response']['items']:
        for j in i['sizes']:
            if j['type'] == photo_sizes:
                d = {
                    'likes': i['likes']['count'],
                    'url': j['url']
                }
                res = {
                    # "file_name": f"{i['likes']['count']}_{datetime.now().timestamp()}.jpg",
                    "file_name": f"{i['likes']['count']}_{datetime.now().strftime('%H-%M-%S')}.jpg",
                    "size": j['type']
                }
        sd.append(d)
        for_dump.append(res)

    # Создание директории на диске:
    def search_folder(path_search):  # Проверка существования директории на диске
        res = YaDi.info(path_search)
        if 'error' in res and res['error'] == 'DiskNotFoundError':
            return 'create'
        elif 'error' in res and res['error'] != 'DiskNotFoundError':
            exec(clean)
            print(f'При проверке наличия директории {path_search} произошла ошибка:\n')
            print(f"Описание - {res['description']}")
            print(f"Ошибка - {res['error']}")
            print(f"Сообщение - {res['message']}\n")
            print('Работа программы прервана')
            exit()
        else:
            return 'ресурс существует'
    directory = f'VK_Photos/User_{data["response"]["items"][0]["owner_id"]}'
    # directory = f'VK_Photos/Users_{data["response"]["items"][0]["owner_id"]}/{album_id}'
    # directory = f'VK_Photos/Users_{data["response"]["items"][0]["owner_id"]}/{datetime.now().date()}'
    path = f'VK_Photos'  # Создание корневой директории
    answer = search_folder(path)
    if answer == 'create':
        method = 'put', 'false'
        YaDi.directory(path, method)
    elif answer == 'ресурс существует':
        print(f'Директория "{path}" уже существует на Диске\n')

    path = directory
    answer = search_folder(path)
    if answer == 'create':
        method = 'put', 'false'
        YaDi.directory(path, method)
    elif answer == 'ресурс существует':
        print(f'Директория "{path}" уже существует на Диске\n')
    time.sleep(3)

    exec(clean)
    print('Загрузка файлов на Яндекс Диск:\n')
    with alive_bar(len(sd)) as bar:  # она же len(data['response']['items'])
        for i in sd:
            targ_url = i['url']
            path = f'{directory}/{i["likes"]}_{datetime.now().strftime("%H-%M-%S")}.jpg'
            print(path)
            YaDi.upload_url(path, targ_url)
            bar()
            # time.sleep(1)

    with open('Result.json', 'wt') as file_object_result:  # Если все удачно, делаем дамп
        json.dump(for_dump, file_object_result, indent=3)
# **********************************************************************
        # Создание/удаление директории на диске:
    # path = 'abcdwxyz/ttest/йцукен/2'
    # method = 'put', 'false'  # Создание директории
    # method = ('delete', 'false')  # Удаление директории в корзину
    # -method- = ('delete', 'true')  # Удаление директории безвозвратно (удалить "--" из имени переменной)
    # result = YaDi.directory(path, method)
