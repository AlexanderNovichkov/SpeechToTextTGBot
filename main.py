from builtins import bytes

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater,
    Dispatcher,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
    PicklePersistence,
)
from telegram.update import Update

from yandexclients import (
    SpeechRecognition,
    SpeechRecognitionException,
    IAMToken,
    Language,
)


class SpeechRecognitionTGBot:
    def __init__(self, telegram_token: str, speech_recognition: SpeechRecognition):
        self._speech_recognition = speech_recognition

        persistence = PicklePersistence(filename="botdata.pickle")
        self._updater = Updater(token=telegram_token, persistence=persistence)

        dispatcher: Dispatcher = self._updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.__start))
        dispatcher.add_handler(CommandHandler("language", self.__language))
        dispatcher.add_handler(CallbackQueryHandler(self.__keyboard_callback_handler))
        dispatcher.add_handler(
            MessageHandler(Filters.audio | Filters.voice, self.__voice_or_audio_message)
        )

    def start(self):
        self._updater.start_polling()
        self._updater.idle()

    def __start(self, update: Update, context: CallbackContext):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Этот бот распознает текст голосовых сообщений и пишет его в ответ.\n\n"
            "/language - выбор языка распознавания речи",
        )

    def __language(self, update: Update, context: CallbackContext):
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(lang.name, callback_data=lang.code)
                    for lang in self._speech_recognition.LANGUAGES
                ]
            ]
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Текущий язык для распознавания: "
            f"{self.__get_current_chat_language(context).name}. \n"
            "Выберите новый язык",
            reply_markup=keyboard,
        )

    def __keyboard_callback_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        language_code = query.data
        try:
            language = next(
                filter(
                    lambda lang: lang.code == language_code,
                    self._speech_recognition.LANGUAGES,
                )
            )
        except StopIteration:
            query.edit_message_text(f"Ошибка при обработке клавиатуры")
            return

        query.edit_message_text(f"Выбран язык распознавания: {language.name}")
        self.__set_new_chat_language(language, context)

    def __voice_or_audio_message(self, update: Update, context: CallbackContext):
        if update.message.voice:
            speech: bytes = update.message.voice.get_file().download_as_bytearray()
        else:
            speech: bytes = update.message.audio.get_file().download_as_bytearray()

        try:
            text = self._speech_recognition(
                speech, self.__get_current_chat_language(context).code
            )
            if len(text) == 0:
                text = "Не получилось здесь распознать речь"
        except SpeechRecognitionException:
            text = (
                "Ошибка при распознавании. "
                "Возможно, данный формат не поддерживается, или длительность больше 30 секунд."
            )
        context.bot.send_message(
            reply_to_message_id=update.message.message_id,
            chat_id=update.effective_chat.id,
            text=text,
        )

    def __get_current_chat_language(self, context: CallbackContext) -> Language:
        return context.chat_data.get("language", self._speech_recognition.LANGUAGES[0])

    def __set_new_chat_language(self, language: Language, context: CallbackContext):
        context.chat_data["language"] = language


def read_token_from_file(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()


def main():
    telegram_token = read_token_from_file("data/telegram-token.txt")
    yandex_oauth_token = read_token_from_file("data/yandex-oauth-token.txt")
    yandex_folder_id = read_token_from_file("data/yandex-folder-id.txt")

    speech_recognition = SpeechRecognition(
        IAMToken(oauth_token=yandex_oauth_token), yandex_folder_id
    )

    srtb = SpeechRecognitionTGBot(telegram_token, speech_recognition)
    srtb.start()


if __name__ == "__main__":
    main()
