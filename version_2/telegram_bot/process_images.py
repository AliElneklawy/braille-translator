import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from PIL import Image
import os

class ProcessImage():
    def __init__(self, im_path, save_path) -> None:
        self.row_coordinates = []
        self.column_coordinates = []
        self.symbols_as_images = []
        self.im_path = im_path # path to the scanned image
        self.save_path = save_path # temp folder to save the cropped images

    def read_image_if_found(self, input_image):     
        self.image = cv2.imread(input_image, cv2.IMREAD_GRAYSCALE)
        assert self.image is not None, "file could not be read, check with os.path.exists()"

    def convert_image_to_black_and_white(self):
        blur = cv2.GaussianBlur(self.image,(5,5), 0)
        ret3, th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        self.blacknwhite_image = th3-255

    def filter_BW_image(self):   #BW means Black and white
        kernel = np.ones((3, 3), np.uint8)                      # removing noise 
        self.filtered_image = cv2.morphologyEx(self.blacknwhite_image, cv2.MORPH_OPEN, kernel)
        
    def crop_edges(self): #to minimize error and remove extra noise
        self.filtered_image = self.filtered_image[10:-10, 10:-10]   #cropping image to remove side line noise
        plt.imshow(self.filtered_image, 'binary')
        plt.axis('off')  # Turn off the axis
        plt.savefig(f'filtered_image_B&W.png', bbox_inches='tight', pad_inches=0,dpi=400)  # Save the image without extra whitespace
        plt.close()  # Close the current figure

    def get_resolution_of_the_image(self):
        self.paper_image = Image.open('filtered_image_B&W.png').convert("L")
        try:
            os.remove('filtered_image_B&W.png')
        except FileNotFoundError:
            print("File 'filtered_image_B&W.png' not found.")
        self.width, self.height = self.paper_image.size

    def convert_image_to_2D_array(self):  #assiging pixel values to the arrays 1 if black 0 if white
        self.pixelvaluearray = [[0 for j in range(self.width)] for i in range(self.height)]
        
        for i in range (self.height):   
            for j in range (self.width):
                pixel_value = self.paper_image.getpixel((j, i))
                pixel_value  = int(pixel_value > 0)
                pixel_value ^= 1
                self.pixelvaluearray[i][j] = pixel_value

    def get_sum_of_rows_columns_black_pixels(self):
        transposed_array = zip(*self.pixelvaluearray)
        self.column_sums = [sum(column) for column in transposed_array]  #calculating sum of each column
        self.row_sums = [sum(row) for row in self.pixelvaluearray]       #calculating sum of each row

    def define_the_columns_within_dots(self):
        threshold_column = 10
        for i in range(len(self.column_sums)):              
                if self.column_sums[i] > threshold_column:
                    self.column_sums[i] = 7
                else:
                    self.column_sums[i] = 0

    def define_the_rows_within_dots(self):
        for i in range(len(self.row_sums)):
                if (i < 120):
                    threshold_row = 2
                else:
                    threshold_row = 20
                if self.row_sums[i] > threshold_row:
                    self.row_sums[i] = 8
                else:
                    self.row_sums[i] = 0

    def shortest_sequence_of_zeros(self,arr):  #finds the length of the shortest subsequence
                                                # of zeros for both columns and rows
        min_length = float('inf')                               
        current_sequence = []                                   

        for pixel in arr:
            if pixel == 0:
                current_sequence.append(pixel)
            else:
                if current_sequence:                            # Update min_length only if a sequence of zeros was found
                    min_length = min(min_length, len(current_sequence))
            current_sequence = []                               # Reset current sequence

        if current_sequence:                                    # Check for zeros at the end of the array
            min_length = min(min_length, len(current_sequence))

        return min_length if min_length != float('inf') else 0  # Handle no zeros case

    def determine_distances_within_symbols(self):                       #constant margins surronding the symbol 
        shortest_sequence_length_column = self.shortest_sequence_of_zeros(self.column_sums)
        shortest_sequence_length_row = self.shortest_sequence_of_zeros(self.row_sums)

        self.column_step = math.ceil(shortest_sequence_length_column/2)
        self.row_step = math.ceil(shortest_sequence_length_row/2)

    def define_symbol_column_bouandry(self):
        flag_1 = 0
        for i in range(len(self.column_sums)):          
            if flag_1 == 0:
                if (self.column_sums[i] == 0):
                    flag_1 = 0 
                else:
                    self.column_coordinates.append(i-self.column_step)
                    flag_1 = 1
            else:
                if (self.column_sums[i] ==7):
                    flag_1 = 1
                else: 
                    self.column_coordinates.append(i+self.column_step-1)
                    flag_1 = 0

    def kill_column_imposter(self): #skipping symbol if one dot in the whole column       
        imposter_index_2 = 0

        for i in range(len(self.column_coordinates) - 1):
            difference = self.column_coordinates[i] - self.column_coordinates[i - 1]          
            if (not(i % 2) and (difference > 14)  and (i > 0)):                
                imposter_index_2 = i-2
                self.column_coordinates.pop(imposter_index_2)
                self.column_coordinates.pop(imposter_index_2)
                break

    def define_symbol_row_bouandry(self): #defining the row pixels to be cut 
        flag_2 = 0
        for i in range(len(self.row_sums)):           
            if flag_2 == 0:
                if (self.row_sums[i] == 0):
                    flag_2 = 0 
                else: 
                    self.row_coordinates.append(i - self.row_step)
                    flag_2 = 1
            else:
                if (self.row_sums[i] == 8):
                    flag_2 = 1
                else: 
                    self.row_coordinates.append(i + self.row_step - 1)
                    flag_2 = 0

    def kill_row_imposter(self):       
        imposter_index = 0
        imposter_flag = 1

        while (imposter_flag):
            x = 69            
            for i in range(len(self.row_coordinates)):
                if(not(i % 6) and (i > 0)):
                    x = (self.row_coordinates[i] - self.row_coordinates[i - 1])

                if (x < 8):
                    imposter_index = i

                if (imposter_index != 0):
                    self.row_coordinates.pop(imposter_index)
                    self.row_coordinates.pop(imposter_index) 
                    imposter_index = 0
                    break
                else: 
                    if(i == len(self.row_coordinates) - 1):
                        imposter_flag = 0

    def extract_elements(self,array,last_elements): #updating the coordinates for symbols and not just columns and rows
        new_array = []
        for i in range(0, len(array), last_elements):
            if i + (last_elements-1) < len(array):
                new_array.append(array[i])
                new_array.append(array[i + (last_elements - 1)])
        return new_array
    
    def assign_coordinates_of_elements_in_two_lists(self):       
        self.symbol_column_coordinates = self.extract_elements(self.column_coordinates,4)
        self.symbol_row_coordinates = self.extract_elements(self.row_coordinates,6)

    def save_the_cropped_symbols(self):
        count = 1
        for symbol in self.symbols_as_images:
            #symbol.save(f"{count}.png")
            symbol.save(os.path.join(self.save_path, f"{count}.png"))
            count += 1

    def crop_the_image_into_symbols(self):
        half_column_length = int (len(self.symbol_column_coordinates) / 2)
        half_row_length = int (len(self.symbol_row_coordinates) / 2)
        count = 1
        white_image = Image.new("L", (224, 224), 255)
        #Cropping the image 
        for i in range(half_row_length):
            for j in range(half_column_length):
                cropped_image = self.paper_image.crop(box = (self.symbol_column_coordinates[j*2],self.symbol_row_coordinates[i*2],self.symbol_column_coordinates[(j*2)+1]+2,self.symbol_row_coordinates[i*2+1]+2))
                #inverting to white if all image is black
                min_value, max_value = cropped_image.getextrema()
                if (max_value - min_value < 10):
                    self.symbols_as_images.append(white_image)
                else:
                    cropped_image = cropped_image.resize([224, 224])
                    self.symbols_as_images.append(cropped_image)
                count += 1
            self.symbols_as_images.append(white_image)
            count += 1

    def create_dataset_using_an_image(self):
        self.divide_the_image_return_array_of_images()
        self.save_the_cropped_symbols()

    def divide_the_image_return_array_of_images(self):
        self.read_image_if_found(self.im_path)
        self.convert_image_to_black_and_white()
        self.filter_BW_image()
        self.crop_edges()
        self.get_resolution_of_the_image()
        self.convert_image_to_2D_array()
        self.get_sum_of_rows_columns_black_pixels()
        self.define_the_columns_within_dots()
        self.define_the_rows_within_dots()
        self.determine_distances_within_symbols()
        self.define_symbol_column_bouandry()
        self.kill_column_imposter()
        self.define_symbol_row_bouandry()
        self.kill_row_imposter()
        self.assign_coordinates_of_elements_in_two_lists()
        self.crop_the_image_into_symbols()
        return self.symbols_as_images
