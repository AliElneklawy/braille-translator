from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, MessageHandler, filters
import os
import shutil
import asyncio
from process_images import *
from inference import *
from spell_checker import *
from TTS import *


TOKEN = 'TOKEN'

async def start(update: Update, context: CallbackContext):
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


async def start_translation(update: Update, context: CallbackContext, current_dir,
                            oProcessImage, oInference, oCorrect, oVoice):

        await update.message.reply_text('Performing some preprocessing steps....')
        oProcessImage.create_dataset_using_an_image()
        data_dict = oInference.preprocess()

        await update.message.reply_text('Translation in progress. It may take up to few minutes.')
        encoded_arr = oInference.predict(data_dict)
        decodede_arr = oInference.decode(encoded_arr)

        await update.message.reply_text('Translation is done. Performing text correction....')
        corrected_txt = oCorrect.correction(decodede_arr)
        await update.message.reply_text(corrected_txt)

        #await update.message.reply_text('Performing text-to-speech....')
        # retry mecahnism
        max_retries = 3 
        retry_delay = 5
        oVoice.save_file(corrected_txt, current_dir)
        voice_path_local = os.path.join(current_dir, 'tts.ogg')
        for attempt in range(max_retries):
            try:
                with open(voice_path_local, 'rb') as voice_file:
                    await update.message.reply_voice(voice_file)
                break # If successful, break out of the loop
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    return


async def clean_up(current_dir, temp_dir, image_path):
    voice_path_local = os.path.join(current_dir, 'tts.ogg')
    if os.path.exists(voice_path_local):
        os.remove(voice_path_local)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    if os.path.exists(image_path):
        os.remove(image_path)


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(current_dir, 'temp')
    model_path = r"path\to\model.h5" # change this path to the path where you saved the model.
    if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)

    oInference = Inference(model_path, temp_dir)
    oCorrect = TextCorrection()
    oVoice = TTS()


    async def handle_photo(update: Update, context: CallbackContext):
        image_path = await get_image(update, context, current_dir)
        oProcessImage = ProcessImage(image_path, temp_dir)
        await start_translation(update, context, current_dir, oProcessImage, oInference, oCorrect, oVoice)
        await clean_up(current_dir, temp_dir, image_path)


    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("standards", standards))
    app.add_handler(CommandHandler("repo", repo))
    app.add_handler(CommandHandler("developers", emails))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()

if __name__ == '__main__':
    main()
