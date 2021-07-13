import threading
import time
from collections import namedtuple
from datetime import timedelta

import requests


class IAMToken:
    def __init__(self, oauth_token: str, time_between_update: timedelta = timedelta(hours=1)):
        self.__oauth_token = oauth_token
        self.__time_between_updates = time_between_update
        self.__iam_token = None
        self.__update_iam_token()
        self.__th = threading.Thread(target=self.__schedule_token_updating, daemon=True)
        self.__th.start()

    def get(self):
        return self.__iam_token

    def __schedule_token_updating(self):
        while True:
            time.sleep(self.__time_between_updates.total_seconds())
            self.__update_iam_token()

    def __update_iam_token(self):
        url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
        params = {'yandexPassportOauthToken': self.__oauth_token}
        try:
            response = requests.post(url, params=params)
        except requests.exceptions.RequestException:
            return
        if response.status_code == 200:
            self.__iam_token = response.json()['iamToken']


class SpeechRecognitionException(Exception):
    pass


class Language:
    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code


class SpeechRecognition:
    __BASE_URL = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'

    LANGUAGES = [Language('Russian', 'ru-RU'), Language('English', 'en-US')]

    def __init__(self, iam_token: IAMToken, folder_id: str):
        self._iam_token = iam_token
        self._folder_id = folder_id

    def __call__(self, speech: bytes, language_code: str) -> str:
        params = {'folderId': self._folder_id,
                  'lang': language_code}
        headers = {'Authorization': f'Bearer {self._iam_token.get()}'}
        try:
            response = requests.post(self.__BASE_URL, params=params, data=speech, headers=headers)
        except requests.exceptions.RequestException as e:
            raise SpeechRecognitionException
        if response.status_code != 200:
            raise SpeechRecognitionException(response.text)
        return response.json()['result']
