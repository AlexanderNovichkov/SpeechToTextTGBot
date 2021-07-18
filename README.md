# SpeechToTextTGBot
Телеграм бот, который распознает текст голосовых сообщений и пишет его в ответ. Поддерживаются русский и английский языки.

В папке data нужно создать следующие файлы:
* telegram-token.txt - Telegram API token
* yandex-oauth-token.txt - [Yandex OAuth token](https://cloud.yandex.ru/docs/iam/concepts/authorization/oauth-token)
* yandex-folder-id.txt - [Yandex folderId](https://cloud.yandex.ru/docs/resource-manager/operations/folder/get-id)

Установка зависимостей:
```
pip install -r requirements.txt
```

Запуск:
```
python3 main.py
```

