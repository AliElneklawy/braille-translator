# this script will be used to create
# a separate directory for each character 
# while resizing each image to 224 * 224. 


import os
import string
import shutil
import cv2 

num_of_examples = 60  # each character has 60 examples in the dataset
english_alphabets = list(string.ascii_uppercase)
images_dir = './Braille Dataset'
images = os.listdir(images_dir)
chars_dir = './characters'
IM_WIDTH, IM_HEIGHT = 224, 224

if not os.path.exists(chars_dir):
    os.makedirs(chars_dir)

counter = 0

for alpha in english_alphabets:
    dest_folder = os.path.join(chars_dir, alpha)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    # Collect 60 images for each character
    selected_images = images[counter * num_of_examples : (counter + 1) * num_of_examples]
    for im in selected_images:
        source_file = os.path.join(images_dir, im)
        destination_file = os.path.join(dest_folder, im)

        img = cv2.imread(source_file)
        resized_img = cv2.resize(img, (IM_WIDTH, IM_HEIGHT))
        cv2.imwrite(destination_file, resized_img)
    
    counter += 1
