from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler
import os
#import asyncio
import time
from process_images import ProcessImage
from inference import Inference
from spell_checker import TextCorrection
from TTS import TTS
from tg_tqdm_v2 import tg_tqdm
from telepot.exception import TelegramError
from urllib3.exceptions import ProtocolError


TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: CallbackContext):
    context.user_data['voice'] = 'male'
    await update.message.reply_text('Welcome to Braille translator.\nPlease, type /standards to get information about the input image stadards.')


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
        "```\nWe don\'t guarantee good results if any of these standards are not met"
    )

    await update.message.reply_text(reply_text, parse_mode='MarkdownV2')


async def repo(update: Update, context: CallbackContext):
    await update.message.reply_text('You can find the code to the project on our GitHub: \
                               https://github.com/AliElneklawy/braille-translation/tree/main')
    

async def emails(update: Update, context: CallbackContext):
    reply_text = (
        "Machine learning team:\n"
        "  Ali Elneklawy: es-ali.elsayed2024@alexu.edu.eg\n"
        "  Nada Gamal-Eldin: es-nadagamal2024@alexu.edu.eg\n"
        "  Nada Tarek: es-nada.tarek2024@alexu.edu.eg\n"
        "Image processing team:\n"
        "  Adham Hedia: es-adham.ahmed2024@alexu.edu.eg\n"
        "  Ayman Feteha: es-aymanmahmoudfeteha2024@alexu.edu.eg\n"
        "  Abdallah Ashraf: 3bdallah.ashraf@gmail.com\n"
        "  Ahmed Abdalal: abdalalahmed11@gmail.com\n"
    )
    
    await update.message.reply_text(reply_text)

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


async def get_image(update: Update, context: CallbackContext, current_dir):
    if update.message.photo:
        photo = update.message.photo[-1]
        # Download the photo
        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()

        # Save the photo to the current working directory
        image_path_local = os.path.join(current_dir, f"{photo.file_id}.jpg")
        with open(image_path_local, 'wb') as f:
            f.write(file_bytes)
        
    return image_path_local


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
        except ProtocolError: # TO BE RECHECKED WITH LINE 178
            await update.message.reply_text('Something went wrong. Please, resend the image.')
            return ''

        text: str = oInference.decode(encoded_arr)

        try:
            await message.edit_text('Translation is done. Performing text correction....')
        except:
            await update.message.reply_text('Translation is done. Performing text correction....')

        corrected_txt: str = oCorrect.correction(text)

        try:
            await message.edit_text(corrected_txt)
        except:
            await update.message.reply_text(corrected_txt)

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
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else: 
                await update.message.reply_text('Couldn\'t generate voice.')


async def clean_up(current_dir, image_path):
    voice_path_local = os.path.join(current_dir, 'tts.ogg')
    if os.path.exists(image_path):
        os.remove(image_path)
    if os.path.exists(voice_path_local):
        os.remove(voice_path_local)


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = r"C:\Users\ALJAZEERA\Desktop\inference\grade_1_model.h5" # change this path to the path where you saved the model.

    oInference = Inference(model_path)
    oCorrect = TextCorrection()
    oVoice = TTS()


    async def handle_photo(update: Update, context: CallbackContext): # handle incoming photo
        image_path = await get_image(update, context, current_dir)
        oProcessImage = ProcessImage(image_path)
        text = await start_translation(update, context, oProcessImage, oInference, oCorrect)
        if text != '': 
            await generate_voice(update, context, current_dir, oVoice, text)
        await clean_up(current_dir, image_path)


    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("standards", standards))
    app.add_handler(CommandHandler("repo", repo))
    app.add_handler(CommandHandler("developers", emails))
    app.add_handler(CommandHandler("voice_selection", voice_selection))
    app.add_handler(CallbackQueryHandler(handle_voice_selection))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()

if __name__ == '__main__':
    main()
