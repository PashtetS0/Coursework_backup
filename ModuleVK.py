import requests

class VKontakte:

    '''
    Модуль содержит метод для работы с ВКонтакте.

    photos()
        Принимает аргументы:
            owner_id = Идентификатор владельца альбома.
            album_id = Идентификатор альбома.
            extended = дополнительные поля likes, comments, tags, can_comment, reposts.
            photo_sizes = Возвращать доступные размеры фотографии в специальном формате.
            count = Количество записей, которое будет получено.
    '''

    def __init__(self, token):
        self.token = token

    def photos(self, owner_id, album_id, extended, photo_sizes, count):
        if not owner_id.isdigit():
            url = 'https://api.vk.com/method/utils.resolveScreenName'
            params = {
            'access_token': self.token,
            'screen_name': owner_id,
            'v': '5.131'
            }
            response = requests.get(url=url, params=params).json()
            owner_id = response['response']['object_id']

        url = 'https://api.vk.com/method/photos.get'
        params = {
            'access_token': self.token,
            'owner_id': owner_id,
            'album_id': album_id,
            'extended': extended,
            'photo_sizes': photo_sizes,
            'count': count,
            'v':'5.131'
        }
        response = requests.get(url=url, params=params)
        # print(response)
        return response
