from builtins import bytes

from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.update import Update

from yandexclients import SpeechRecognition, SpeechRecognitionException, IAMToken


class SpeechRecognitionTGBot:
    def __init__(self, telegram_token: str, oauth_token: str, folder_id: str):
        self._speech_recognition = SpeechRecognition(IAMToken(oauth_token=oauth_token), folder_id)
        self._updater = Updater(token=telegram_token)
        dispatcher: Dispatcher = self._updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', self.__start))
        dispatcher.add_handler(MessageHandler(Filters.audio | Filters.voice, self.__voice_or_audio_message))

    def start(self):
        self._updater.start_polling()

    def __start(self, update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Этот бот распознает текст голосовых сообщений и пишет его в ответ.")

    def __voice_or_audio_message(self, update: Update, context: CallbackContext):
        if update.message.voice:
            speech: bytes = update.message.voice.get_file().download_as_bytearray()
        else:
            speech: bytes = update.message.audio.get_file().download_as_bytearray()
        try:
            text = self._speech_recognition.recognize(speech)
            if len(text) == 0:
                text = "Не получилось здесь распознать речь"
        except SpeechRecognitionException:
            text = "Ошибка при распознавании. Возможно, данный формат не поддерживается, или длительность больше 30 секунд."
        context.bot.send_message(reply_to_message_id=update.message.message_id, chat_id=update.effective_chat.id,
                                 text=text)


def read_token_from_file(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()


def main():
    telegram_token = read_token_from_file('data/telegram-token.txt')
    yandex_oauth_token = read_token_from_file('data/yandex-oauth-token.txt')
    yandex_folder_id = read_token_from_file('data/yandex-folder-id.txt')

    srtb = SpeechRecognitionTGBot(telegram_token, yandex_oauth_token, yandex_folder_id)
    srtb.start()


if __name__ == '__main__':
    main()
