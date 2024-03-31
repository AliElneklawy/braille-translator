from tensorflow.keras.models import load_model
import numpy as np
from itertools import product
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.densenet import preprocess_input
import re
import os

class Inference():
    def __init__(self, model_path, data_path) -> None:
        
        self.mappings = {'100000': ['a', '1'], '110000': ['b', '2'], '100100': ['c', '3'], 
            '100110': ['d', '4'], '100010': ['e', '5'], '110100': ['f', '6'], 
            '110110': ['g', '7'], '110010': ['h', '8'], '010100': ['i', '9'], 
            '010110': ['j', '0'], '101000': 'k', '111000': 'l', '101100': 'm', 
            '101110': 'n', '101010': 'o', '111100': 'p', '111110': 'q', 
            '111010': 'r', '011100': 's', '011110': 't', '101001': 'u',
            '111001': 'v', '010111': 'w', '101101': 'x', '101111': 'y',
            '101011': 'z', '000000': ' ', '011001': '?','011010': '!', 
            '001000': '\'', '010000': ',', '001001': '-', '010011': '.', 
            '010010': ':', '011000': ';', '001111': '#', '011011': '=', 
            '001010': '*', '001011': ')', '000001': 'CAP'}

        self.combinations = list(product([0, 1], repeat=6))
        self.class_names = [''.join(map(str, comb)) for comb in self.combinations]
        self.predictions_arr_zeros_ones, self.predictions_arr = [], []
        self.preprocessed_images = []
        self.data_names = {}
        self.next_is_num, self.next_is_cap = False, False

        self.model_path = model_path
        self.data_path = data_path
        self.model = load_model(self.model_path)


    def preprocess(self) -> dict:       
        for im in os.listdir(self.data_path):
            img_path = os.path.join(self.data_path, im)
            im_number = int(im.split('.')[0]) # will be used to sort the images dictionary
            img = image.load_img(img_path, target_size=(224, 224))  
            x = image.img_to_array(img)
            x = preprocess_input(x)
            x /= 255.0
            x = np.expand_dims(x, axis=0)           
            self.data_names[im_number] = x

        data_names_ordered = dict(sorted(self.data_names.items()))

        return data_names_ordered


    def predict(self, data_dict: dict) -> list:
        for im_arr in data_dict.values():
            predictions = self.model.predict(im_arr, verbose=0)
            predicted_class_index = np.argmax(predictions)
            predicted_class_label = self.class_names[predicted_class_index]
            self.predictions_arr_zeros_ones.append(predicted_class_label) 
            
        return self.predictions_arr_zeros_ones
    

    def decode(self, encoded_arr: list) -> str: # Mapping encoded characters to their values in the mappings dict
        for encoded_char in encoded_arr:
            if encoded_char in self.mappings:
                if self.mappings[encoded_char] == '#': 
                    self.next_is_num = True
                    num_str = ''
                elif self.mappings[encoded_char] == 'CAP': 
                    self.next_is_cap = True
                else:
                    if self.next_is_num:
                        if self.mappings[encoded_char] != ' ' and isinstance(self.mappings[encoded_char], list):
                            num_str += self.mappings[encoded_char][1]
                        else:
                            self.predictions_arr.append(num_str)
                            self.predictions_arr.append(self.mappings[encoded_char])
                            self.next_is_num = False
                    elif self.next_is_cap:
                        self.predictions_arr.append(self.mappings[encoded_char][0].upper())
                        self.next_is_cap = False
                    else:
                        self.predictions_arr.append(self.mappings[encoded_char][0])

        predicted_txt_ext_spaces = ''.join(self.predictions_arr)
        clean_txt = re.sub(r'\s+', ' ', predicted_txt_ext_spaces) #remove extra spaces

        return clean_txt
