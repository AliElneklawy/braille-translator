from process_images import *
from inference import *
from spell_checker import *
from TTS import *
import shutil


if __name__ == '__main__':
    im_path = input('Enter the path to the scanned image: ')
    model_path = input('Enter the path to the model: ')
    generate_voice = input('Do you want to generate voice? (y/n): ').lower()

    current_dir = os.path.dirname(os.path.abspath(__file__)) # get the current directory.
    temp_dir = os.path.join(current_dir, 'temp')

    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir) # create a temporary folder to save the dataset.
    
    oImage = ProcessImage(im_path, temp_dir)
    oInference = Inference(model_path, temp_dir)
    oCorrect = TextCorrection()

    print('Creating the dataset......')
    oImage.create_dataset_using_an_image()

    print('Preprocessing......')
    data_dict = oInference.preprocess()

    print('Translation in progress. It may take a while depending on your system....')
    encoded_arr = oInference.predict(data_dict)

    print('Decoding.....')
    decodede_arr = oInference.decode(encoded_arr)

    print(f'\nModel output: {decodede_arr}') # Output from the model. Uncorrected text.

    corrected_txt = oCorrect.correction(decodede_arr)
    print(f"\nCorrected text: {corrected_txt}") # Output after text correction.

    if generate_voice == 'y':
        oVoice = TTS()
        oVoice.say(corrected_txt)
        
        save_voice = input('Do you want to save the voice? (y/n): ').lower()
        if save_voice == 'y':
            oVoice.save_file(corrected_txt, current_dir)
            print('File (tts.wav) saved successfuly.')

    shutil.rmtree(temp_dir) # remove the temporary folder
