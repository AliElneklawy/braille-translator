import re
from itertools import product

import numpy as np
from tensorflow.keras.applications.densenet import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image


class Inference:
    """
    Class to map 6-bit Braille patterns to characters and decode image-derived predictions.

        - Uses a mappings dict for braille-to-char and special tokens (CAP, #).
        - Builds class_names from all 6-bit combinations for model output.
        - Provides preprocess, predict, and decode to convert images to text.
    """
    def __init__(self, model_path) -> None:
        self.mappings = {
            "100000": ["a", "1"],
            "110000": ["b", "2"],
            "100100": ["c", "3"],
            "100110": ["d", "4"],
            "100010": ["e", "5"],
            "110100": ["f", "6"],
            "110110": ["g", "7"],
            "110010": ["h", "8"],
            "010100": ["i", "9"],
            "010110": ["j", "0"],
            "101000": "k",
            "111000": "l",
            "101100": "m",
            "101110": "n",
            "101010": "o",
            "111100": "p",
            "111110": "q",
            "111010": "r",
            "011100": "s",
            "011110": "t",
            "101001": "u",
            "111001": "v",
            "010111": "w",
            "101101": "x",
            "101111": "y",
            "101011": "z",
            "000000": " ",
            "011001": "?",
            "011010": "!",
            "001000": "'",
            "010000": ",",
            "001001": "-",
            "010011": ".",
            "010010": ":",
            "011000": ";",
            "001111": "#",
            "011011": "=",
            "001010": "*",
            "001011": ")",
            "000001": "CAP",
        }

        self.combinations = list(product([0, 1], repeat=6))
        self.class_names = ["".join(map(str, comb)) for comb in self.combinations]
        self.next_is_num, self.next_is_cap = False, False

        self.model_path = model_path
        self.model = load_model(self.model_path)

    def preprocess(self, images_arr: list) -> list:
        for i, im in enumerate(images_arr):
            im = im.convert("RGB")
            x = image.img_to_array(im)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)
            x /= 255.0
            images_arr[i] = x

        return images_arr

    def predict(self, im: list) -> list:
        predictions = self.model.predict(im, verbose=0)
        predicted_class_index = np.argmax(predictions)
        predicted_class_label = self.class_names[predicted_class_index]

        return predicted_class_label

    def FormatText(self, text: str) -> str:
        formatted_text = ""
        words = re.findall(
            r"\S+|\s+", text
        )  # Split text into words and preserve consecutive spaces
        consecutive_spaces = 0
        is_dot = 0
        for word in words:
            if word.isspace():
                consecutive_spaces += len(word)
            elif consecutive_spaces > 0:
                if (
                    len(word) <= consecutive_spaces - 1
                ) and is_dot:  # Check if word fits in consecutive spaces
                    formatted_text += "\n" + word
                else:
                    formatted_text += " " + word
                consecutive_spaces = 0
            else:
                formatted_text += " " + word.strip()
            if not (word.isspace()):
                is_dot = word[-1] == "."
        return formatted_text.lstrip()  # Remove leading space from the result

    def decode(
        self, encoded_arr: list
    ) -> str:  # Mapping encoded characters to their values in the mappings dict
        predictions_arr = []
        for encoded_char in encoded_arr:
            if encoded_char in self.mappings:
                if self.mappings[encoded_char] == "#":
                    self.next_is_num = True
                    num_str = ""
                elif self.mappings[encoded_char] == "CAP":
                    self.next_is_cap = True
                else:
                    if self.next_is_num:
                        if self.mappings[encoded_char] != " " and isinstance(
                            self.mappings[encoded_char], list
                        ):
                            num_str += self.mappings[encoded_char][1]
                        else:
                            predictions_arr.append(num_str)
                            predictions_arr.append(self.mappings[encoded_char])
                            self.next_is_num = False
                    elif self.next_is_cap:
                        predictions_arr.append(self.mappings[encoded_char][0].upper())
                        self.next_is_cap = False
                    else:
                        predictions_arr.append(self.mappings[encoded_char][0])

        predicted_txt_ext_spaces = "".join(predictions_arr)
        txt_inParagraphs = self.FormatText(predicted_txt_ext_spaces)
        return txt_inParagraphs
