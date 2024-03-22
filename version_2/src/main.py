from process_images import *
from inference import *
import os
import shutil

if __name__ == '__main__':
    im_path = input('Enter the path to the scanned image: ')
    model_path = input('Enter the path to the model: ')

    current_dir = os.path.dirname(os.path.abspath(__file__)) # get the current directory
    temp_dir = os.path.join(current_dir, 'temp')

    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir) # create a temporary folder to save the dataset
    
    oImage = ProcessImage(im_path, temp_dir)
    oInference = Inference(model_path, temp_dir)

    print('Creating the dataset......')
    oImage.create_dataset_using_an_image()

    print('Preprocessing......')
    data_dict = oInference.preprocess()

    print('Prediction in process. It may take a while....')
    prediction = oInference.predict(data_dict)
    print(prediction)

    shutil.rmtree(temp_dir) # remove the temporary folder