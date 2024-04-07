from process_images import *
from inference import *
from spell_checker import *
from TTS import *
from tqdm import tqdm


if __name__ == '__main__':
    im_path = input('Enter the path to the scanned image: ')
    model_path = input('Enter the path to the model: ')
    generate_voice = input('Do you want to generate voice? (y/n): ').lower()

    current_dir = os.path.dirname(os.path.abspath(__file__)) # get the current directory.
    
    oImage = ProcessImage(im_path)
    oInference = Inference(model_path)
    oCorrect = TextCorrection()

    print('Processing the image......')
    images_arr = oImage.divide_the_image_return_array_of_images()
    images_arr_preprocessed = oInference.preprocess(images_arr)

    print('Translation in progress. It may take a while depending on your system....')
    encoded_arr: list = []
    for im in tqdm(images_arr_preprocessed): # show progress bar
            encoded_arr.append(oInference.predict(im))

    print('Decoding.....')
    text = oInference.decode(encoded_arr)

    print(f'\nModel output: {text}') # Output from the model. Uncorrected text.

    corrected_txt = oCorrect.correction(text)
    print(f"\nCorrected text: {corrected_txt}") # Output after text correction.

    if generate_voice == 'y':
        oVoice = TTS()
        oVoice.say(corrected_txt)
        
        save_voice = input('Do you want to save the voice? (y/n): ').lower()
        if save_voice == 'y':
            oVoice.save_file(corrected_txt, current_dir)
            print('File (tts.wav) saved successfuly.')
