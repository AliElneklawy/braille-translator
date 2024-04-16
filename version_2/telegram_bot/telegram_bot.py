import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler
from process_images import ProcessImage
from inference import Inference
from spell_checker import TextCorrection
from TTS import TTS
from en_to_braille import TextToBraille
from speech_to_text import SpeechToText
from tg_tqdm_v2 import tg_tqdm
from telepot.exception import TelegramError
from urllib3.exceptions import ProtocolError
<<<<<<< Updated upstream

=======
from telegram.error import TimedOut
>>>>>>> Stashed changes


TOKEN = os.getenv('BOT_TOKEN')


async def start(update: Update, context: CallbackContext):
    context.user_data['voice'] = 'male'
    first_name = update.effective_user.first_name
    await update.message.reply_text(f'Hey {first_name}. Please, type /standards to get information about the input image stadards.')


async def help(update: Update, context: CallbackContext):
    reply_text = (
        "The bot currently supports English, grade 1 Braille\.\n"
        "You can:\n"
        "  *send a photo with Braille text*: it will be translated into English\.\n"
        "  *send a message containig English text*: it will be translated into Braille\.\n"
        "  *send an audio file, voice or video message in English*: it will be transcribed then translated into Braille\.\n"
    )

    await update.message.reply_text(reply_text, parse_mode='MarkdownV2')


async def standards(update: Update, context: CallbackContext):
    reply_text = (
        "For accurate translation, we recommend that you follow these standards:```\n"
        "  Printer: INDEX BRAILLE Everest-D V5\n"
        "  Printed page size: 23cm x 33cm\n"
        "  Dot size: 2mm\n"
        "  Distance between 2 dots in the same symbol: 0.7mm\n"
        "  Distance between 2 rows: 3mm\n"
        "  Distance between 2 columns: 2mm\n"
        "\n"
        "  Scanner: Canon PIXIMA TS3140\n"
        "  Scan settings:\n"
        "      Source: Flatbed\n"
        "      Color format: Grayscale\n"
        "      File type: JPG, PNG\n"
        "      Resolution (DPI): 100\n"
        "```\nWe don\'t guarantee good results if any of these standards are not met\."
    )

    await update.message.reply_text(reply_text, parse_mode='MarkdownV2')


async def repo(update: Update, context: CallbackContext):
    await update.message.reply_text('You can find the code to the project on our GitHub: \
                               https://github.com/AliElneklawy/braille-translation/tree/main')
    

async def emails(update: Update, context: CallbackContext):
    reply_text = (
        "*Machine Learning Team*\n"
        "  Ali Elneklawy: es\-ali\.elsayed2024@alexu\.edu\.eg\n"
        "  Nada Gamal\-Eldin: es\-nadagamal2024@alexu\.edu\.eg\n"
        "  Nada Tarek: es\-nada\.tarek2024@alexu\.edu\.eg\n"
        "*Image Processing Team*\n"
        "  Adham Hedia: es\-adham\.ahmed2024@alexu\.edu\.eg\n"
        "  Ayman Feteha: es\-aymanmahmoudfeteha2024@alexu\.edu\.eg\n"
        "  Abdallah Ashraf: 3bdallah\.ashraf@gmail\.com\n"
        "  Ahmed Abdalal: abdalalahmed11@gmail\.com\n"
    )
    
    await update.message.reply_text(reply_text, parse_mode='MarkdownV2')


async def voice_selection(update: Update, context: CallbackContext):
    """Send a message with two options for voice selection."""
    keyboard = [
        [InlineKeyboardButton("Male Voice", callback_data='male')],
        [InlineKeyboardButton("Female Voice", callback_data='female')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Please choose a voice:', reply_markup=reply_markup)


async def handle_voice_selection(update: Update, context: CallbackContext):
    """Handle the user's selection from the voice menu."""
    query = update.callback_query
    await query.answer()

    if query.data == 'male':
        context.user_data['voice'] = 'male'
        await query.edit_message_text(text="Voice set to Male.")
    elif query.data == 'female':
        context.user_data['voice'] = 'female'
        await query.edit_message_text(text="Voice set to Female.")


async def get_file(update: Update, context: CallbackContext, current_dir):
    if update.message.voice:
        file = update.message.voice
    elif update.message.audio:
        file = update.message.audio
    elif update.message.video:
        file = update.message.video
    elif update.message.photo:
        file = update.message.photo[-1]

    file = await context.bot.get_file(file.file_id)
    file_bytes = await file.download_as_bytearray()
    file_path_local = os.path.join(current_dir, f"{file.file_id}")

    with open(file_path_local, 'wb') as f:
        f.write(file_bytes)

    return file_path_local 


async def start_translation(update: Update, context: CallbackContext,
                            oProcessImage, oInference, oCorrect):
    
        message = await update.message.reply_text('Translation in progress....')
        images_arr = oProcessImage.divide_the_image_return_array_of_images()
        images_arr_preprocessed = oInference.preprocess(images_arr)

        encoded_arr: list = []
        chat_id = update.message.chat_id

        try:
            for im in tg_tqdm(images_arr_preprocessed, TOKEN, chat_id, unit=' chars'): # show progress bar
                encoded_arr.append(oInference.predict(im))
        except TelegramError as e:
            print("TelegramError occurred. Progress message in tg_tqdm encountered an error:", e)
        except ProtocolError: # TO BE RECHECKED WITH LINE 178 (WORKS)
            await update.message.reply_text('Something went wrong. Please, resend the image.')
            return ''

        text: str = oInference.decode(encoded_arr)

        await message.edit_text('Translation is done. Performing text correction....')
        corrected_txt: str = oCorrect.correction(text)
        await message.edit_text(corrected_txt)

        encoded_arr.clear()
        images_arr_preprocessed.clear()

        return corrected_txt

async def generate_voice(update: Update, context: CallbackContext, current_dir, oVoice, text):
    if context.user_data['voice'] == 'male':
        voice_id = 0 
    else:
        voice_id = 1

    # retry mecahnism
    max_retries, retry_delay = 3, 5
    oVoice.save_file(text, current_dir, voice_id)
    voice_path_local = os.path.join(current_dir, 'tts.ogg')
    for attempt in range(max_retries):
        try:
            with open(voice_path_local, 'rb') as voice_file:
                await update.message.reply_voice(voice_file)
            break # If successful, break out of the loop
        except TimedOut as e:
            print('Error occured while generating voice: ', e)
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else: 
                await update.message.reply_text('Couldn\'t generate voice.')


async def clean_up(current_dir, file_path):
    voice_path_local = os.path.join(current_dir, 'tts.ogg')
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(voice_path_local):
        os.remove(voice_path_local)


def create_text_to_braille(oTextToBraille):
    async def text_to_braille(update: Update, context: CallbackContext):
        text = update.message.text
        braille = oTextToBraille.en_to_braille(text)
        await update.message.reply_text(braille)
    return text_to_braille


def create_speech_to_braille(oVoiceToText, oTextToBraille, current_dir):
    async def speech_to_braille(update: Update, context: CallbackContext):
        msg_path = await get_file(update, context, current_dir)

        message = await update.message.reply_text('Transcribtion and translation in progress....')
        text = oVoiceToText.transcribe(msg_path)        
        braille = oTextToBraille.en_to_braille(text)

        await message.edit_text(text)
        await update.message.reply_text(braille)

        await clean_up(current_dir, msg_path)

    return speech_to_braille


def create_handle_photo(oVoice, oCorrect, oInference, current_dir):
    async def handle_photo(update: Update, context: CallbackContext):
        image_path = await get_file(update, context, current_dir)
        oProcessImage = ProcessImage(image_path)
        text = await start_translation(update, context, oProcessImage, oInference, oCorrect)
        if text != '': 
            await generate_voice(update, context, current_dir, oVoice, text)
        await clean_up(current_dir, image_path)
    return handle_photo


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = r"path\to\model.h5"

    oInference = Inference(model_path)
    oCorrect = TextCorrection()
    oVoice = TTS()
    oTextToBraille = TextToBraille()
    oVoiceToText = SpeechToText()

    handle_photo_handler = create_handle_photo(oVoice, oCorrect, oInference, current_dir)
    speech_to_braille_handler = create_speech_to_braille(oVoiceToText, oTextToBraille, current_dir)
    text_to_braille_handler = create_text_to_braille(oTextToBraille)

    app = ApplicationBuilder().token(TOKEN).build()

    # command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("standards", standards))
    app.add_handler(CommandHandler("repo", repo))
    app.add_handler(CommandHandler("developers", emails))
    app.add_handler(CommandHandler("voice_selection", voice_selection))
    app.add_handler(CallbackQueryHandler(handle_voice_selection))

    # message handlers
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_handler, block=False)) # handle photo
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_braille_handler)) # handle text
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO | filters.VIDEO, speech_to_braille_handler)) # handle voice, video and audio

    app.run_polling()


if __name__ == '__main__':
    main()
