class TextToBraille():
  def __init__(self) -> None:
    self.character_unicodes = {'a': '\u2801', 'b': '\u2803', 'k': '\u2805', 'l': '\u2807', 'c': '\u2809', 
                               'i': '\u280A', 'f': '\u280B', 'm': '\u280D', 's': '\u280E', 'p': '\u280F', 
                               'e': '\u2811', 'h': '\u2813', 'o': '\u2815', 'r': '\u2817', 'd': '\u2819', 
                               'j': '\u281A', 'g': '\u281B', 'n': '\u281D', 't': '\u281E', 'q': '\u281F', 
                               'u': '\u2825', 'v': '\u2827', 'x': '\u282D', 'z': '\u2835', 'w': '\u283A', 
                               'y': '\u283D', 'NUM': '\u283C', 'CAP': '\u2820', '.': '\u2832', "'": '\u2804', 
                               ',': '\u2802', '-': '\u2824', '/': '\u280C', '!' : '\u2816', '?': '\u2826', 
                               '$': '\u2832', ':': '\u2812', ';': '\u2830', '(': '\u2836', ')': '\u2836', 
                               '1': '\u2801', '2': '\u2803', '3': '\u2809', '4': '\u2819', '5': '\u2811', 
                               '6': '\u280B', '7': '\u281B', '8': '\u2813', '9': '\u280A', '0': '\u281A', 
                               ' ': '\u2800'}
    
    self.number_punctuations = ['.', ',', '-', '/', '$']
    self.escape_characters = ['\n', '\r', '\t']

  def en_to_braille(self, text: str):
    isNumber = False
    braille = ''

    for char in text:
      if char in self.escape_characters:
        braille += char
        continue

      if char.isupper():
        braille += self.character_unicodes['CAP']
        char = char.lower()
    
      if char.isdigit():
        if not isNumber:
          isNumber = True
          braille += self.character_unicodes['NUM']
      else:
        if isNumber and char not in self.number_punctuations:
          isNumber = False

      if char in self.character_unicodes.keys():
        braille += self.character_unicodes[char]
      else:
        braille += ' '
        
    return braille
