import cv2
import numpy as np
from collections import Counter
import json


class BrailleTranslator:
    def __init__(self):
        self.arr=[]
        self.x_sorted_coordinates=[]
        self.y_sorted_coordinates=[]
        self.Rows_matrix=[]
        self.updated_all_symbols=[]

    def read_dict_from_json(self,json_path):
        # Load the JSON data
        with open(json_path, 'r') as file:
            self.data = json.load(file)

    def extract_dict_from_json(self):
        # Convert string keys representing tuples back to actual tuples
        self.braille_dict_English = {tuple(map(int, k[1:-1].split(', '))): v for k, v in self.data['braille_dict_Arabic'].items()}
        self.braille_dict_English_cap = {tuple(map(int, k[1:-1].split(', '))): v for k, v in self.data['braille_dict_Arabic_cap'].items()}
        self.nums = {tuple(map(int, k[1:-1].split(', '))): v for k, v in self.data['nums'].items()}
   
    def read_image(self,image_path):
        self.img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        assert self.img is not None, "file could not be read, check with os.path.exists()"
    
    def filtering_input_image(self):
        blur = cv2.GaussianBlur(self.img,(3,3),1)
        __,th3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        blur     = cv2.GaussianBlur(th3,(3,3),0)
        thres    = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,3,16)
        self.blur2    = cv2.medianBlur(thres,3)
    
    def crop_image_sides(self):
        self.cropped_image = self.blur2[:,10:-10]
    
    def circles_detection(self):
        edges    = cv2.Canny(self.cropped_image, 250, 251)
        circles  = cv2.HoughCircles(edges,cv2.HOUGH_GRADIENT, dp=0.2, minDist=8, param1=5, param2=4.3, minRadius=2, maxRadius=4)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(self.cropped_image, (x, y), 2, (0, 255, 0), 2)
                self.arr.append((x,y))
    
    def sort_array_x2y(self):

        self.dot_coordinates = sorted(self.arr, key=lambda x: x[1])
        self.dot_coordinates = sorted(self.arr, key=lambda x: x[0])

    def determine_unique_xndy_values_of_great_matrix(self):
        x_values = [coord[0] for coord in self.dot_coordinates]
        y_values = [coord[1] for coord in self.dot_coordinates]
        self.unique_x = sorted(set(x_values))
        self.unique_y = sorted(set(y_values))

    def identify_unique_x(self,x_threshold):
        self.adjusted_unique_x = [self.unique_x[0]]  # Start with the first point
        self.x_threshold=x_threshold
        for i in range(1, len(self.unique_x)):
            if self.unique_x[i] - self.adjusted_unique_x[-1] > self.x_threshold:  # Check the difference
                self.adjusted_unique_x.append(self.unique_x[i])

    def adjust_non_unique_x_values_in_matrix(self):
        for j, x in enumerate(self.adjusted_unique_x):
            for i in range(len(self.dot_coordinates) ):
            
                if ((self.dot_coordinates[i][0]-x)<=self.x_threshold) and ((self.dot_coordinates[i][0]-x)>0) :
                    updated_tuple = (self.adjusted_unique_x[j], self.dot_coordinates[i][1])
                    self.dot_coordinates[i]=updated_tuple

    def identify_unique_y(self,y_threshold):
        self.adjusted_unique_y = [self.unique_y[0]]
        y_threshold=5
        for i in range(1, len(self.unique_y)):
            if self.unique_y[i] - self.adjusted_unique_y[-1] > y_threshold:  # Check the difference
                self.adjusted_unique_y.append(self.unique_y[i])

    def find_closest_less_than(self, arr, val):
        for i in range(len(arr) - 1, -1, -1):
            if arr[i] <= val:
                return arr[i]
        return None  # Return None if there's no value less than or equal to 'val'

    def adjust_non_unique_y_values_in_matrix(self):
        self.dot_coordinates = sorted(self.dot_coordinates, key=lambda x: x[1])
        # Adjusting y values in y_sorted_coordinates
        self.adjusted_coordinates = []
        for x, y in self.dot_coordinates:
            closest_y = self.find_closest_less_than(self.adjusted_unique_y, y)
            self.adjusted_coordinates.append((x, closest_y))
        self.dot_coordinates=sorted(self.adjusted_coordinates, key=lambda x: x[0])

    def remove_unwanted_extra_point(self):
        specific_y_values = [self.unique_y[0], self.unique_y[1], self.unique_y[2]]
        y_values = [coord[1] for coord in self.adjusted_coordinates]
        # Count the frequency of each 'y' value
        y_frequency = Counter(y_values)
        y_to_remove=[]
        for y, frequency in y_frequency.items():   
            if frequency==1 and y not in specific_y_values:
                y_to_remove.append(y)

        self.adjusted_unique_y = [y for y in self.adjusted_unique_y if y not in y_to_remove]

    def  identify_unique_x_coordinates(self):  
        for i in range(1,len(self.adjusted_unique_x)):
            temp=0
            if((self.adjusted_unique_x[i]-self.adjusted_unique_x[i-1]>=30) and (self.adjusted_unique_x[i]-self.adjusted_unique_x[i-1]< 40)):
                temp=self.adjusted_unique_x[i]-10
                
                self.adjusted_unique_x.append(temp)
        self.adjusted_unique_x = sorted(self.adjusted_unique_x)

    def  generate_general_matrix(self):
        for j in range(int(len(self.adjusted_unique_y)/3)):
            symbols=[]    
            for i in range(int(len(self.adjusted_unique_x))):
                symbol=[] 
                if i%2==0:
                    if((i+1)==len(self.adjusted_unique_x)):
                        continue
                    else:
                        for f in range(2):
                            temp=(self.adjusted_unique_x[i+f],self.adjusted_unique_y[3*j])
                            symbol.append(temp)
                            temp=(self.adjusted_unique_x[i+f],self.adjusted_unique_y[3*j+1])
                            symbol.append(temp)        
                            temp=(self.adjusted_unique_x[i+f],self.adjusted_unique_y[3*j+2])
                            symbol.append(temp)

                        symbols.append(symbol)
                        temp=[]
                        symbol=[]
            self.Rows_matrix.append(symbols) 

    def mapping_coordinates_to_binary(self,  all_symbols):
        updated_symbols = []
        for coordinates_list in all_symbols:
            updated_list = []
            for coord in coordinates_list:
                if coord in self.dot_coordinates:
                    updated_list.append(1)
                else:
                    updated_list.append(0)
            updated_symbols.append(updated_list)
        return updated_symbols 

    def mapping_page_to_binary(self):
         for i in range(len(self.Rows_matrix)):
            Row_i= self.mapping_coordinates_to_binary( self.Rows_matrix[i])
            self.updated_all_symbols.append(Row_i) 

    def map_row_to_braille(self,updated_symbols):
        mapped_row_result = ""
        Flag = 'normal'
        prev_char = [0,0,0,0,0,0]
        for symbol_row in updated_symbols:
            if symbol_row == [0,0,0,0,0,1]:
                Flag = 'capital'
                continue
            elif symbol_row == [0,0,1,1,1,1]:
                Flag = 'number'
                continue
            if symbol_row == [0,0,0,0,0,0] and prev_char == [0,0,0,0,0,0]:
                continue
            elif symbol_row == [0,0,0,0,0,0] and prev_char!= [0,0,0,0,0,0]:
                Flag = 'normal'
            prev_char=symbol_row
            if Flag == 'normal':
                braille_char = self.braille_dict_English.get(tuple(symbol_row), '')
            elif Flag == 'capital':
                braille_char = self.braille_dict_English_cap.get(tuple(symbol_row), '')
                Flag = 'normal'
            elif Flag == 'number':
                braille_char = self.nums.get(tuple(symbol_row), '')
                if braille_char not in self.nums.values():
                    braille_char = self.braille_dict_English.get(tuple(symbol_row), '')
                    Flag = 'normal'
                

            mapped_row_result =mapped_row_result + braille_char
        return mapped_row_result

    def mapping_page_to_braille(self):
        mapped_result=""
        for row in self.updated_all_symbols:
            Row_j = self.map_row_to_braille(row)
            mapped_result = mapped_result + Row_j + " "
        return  mapped_result[1:len(mapped_result)]  
       
    def translate_braille_to_text(self, image_path, text_path, json_path, x_threshold=6, y_threshold=5 ):
        self.read_dict_from_json(json_path)
        self.extract_dict_from_json()
        self.read_image(image_path)
        self.filtering_input_image()
        self.crop_image_sides()
        self.circles_detection()
        self.sort_array_x2y()
        self.determine_unique_xndy_values_of_great_matrix()
        self.identify_unique_x(x_threshold)
        self.adjust_non_unique_x_values_in_matrix()
        self.identify_unique_y(y_threshold)
        self.adjust_non_unique_y_values_in_matrix()
        self.remove_unwanted_extra_point()
        self.identify_unique_x_coordinates()
        self.generate_general_matrix()
        self.mapping_page_to_binary()
        translated_text = self.mapping_page_to_braille()
        with open(text_path, "w") as text_file:
            # Write the text string to the file
            text_file.write(translated_text)


# translator = BrailleTranslator()
# translator.translate_braille_to_text('3.jpg','text_file.txt','mappings.json')
