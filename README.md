# Team Members  
### Machine Learning Team
  - [Ali Elneklawy](https://github.com/AliElneklawy)
  - [Nada Gamal El-Dien](https://github.com/nadagamaall22)
  - [Nada Tarek](https://github.com/NadaTarek54)
### Image Processing Team
  - [Ayman Feteha](https://github.com/Ayman-Feteha)
  - [Abdallah Ashraf](https://github.com/3bdallahai)
  - [Ahmed Abdalal](https://github.com/Asyody)
  - [Adham Hedia](https://github.com/Adham-M0)

# Demo


https://github.com/AliElneklawy/braille-translator/assets/89526026/24d9f843-766a-4796-941c-7c3f804cdb5d






# Braille Image Translation and Text-to-Speech Conversion

## Overview
This repository hosts our graduation project, focused on the development of a system that utilizes image processing and deep learning techniques to facilitate the translation of scanned Braille images into English text. Additionally, the system converts the extracted text into audible speech, enhancing accessibility for visually impaired individuals.

## Project Description
This project aims to bridge the gap between Braille literacy and accessibility through the integration of cutting-edge technologies. Leveraging the power of image processing and deep learning, the system provides a robust solution capable of accurately interpreting Braille characters from scanned images.

Furthermore, the project extends beyond mere text extraction by incorporating a text-to-speech conversion step. By synthesizing the extracted English text into audible speech, the system empowers individuals with visual impairments to access Braille content effortlessly. Our project is focused on translating grade 1, front-only, scanned Braille images. The summary of the project is shown in the figure below.

<p align="center">
  <img src="https://github.com/AliElneklawy/braille-translation/blob/main/utils/project%20summary.jpg" alt="Project Summary" />
</p>

## Repository Structure

There are two main directories in this repository; `version_1` and `version_2`. In `version_1` folder, we tried out several models on a dataset that we got from kaggle. The dataset closely resembles the one that we are going to generate in `version_2`. It turned out that DenseNet201 model was the most suitable model for our task so, we decided to continue with this model. In `version_2`, we generated our own dataset and trained a DenseNet201 model on it. The strucure of the repository is shown below.

```
braille-translator/
├─ README.md
├─ utils/
│  └─ project summary.jpg
├─ version_1/
│  ├─ README.md
│  ├─ input/
│  │  ├─ characters/
│  │  │  ├─ A/
│  │  │  │  ├─ ......
│  │  │  ├─ B/
│  │  │  │  ├─ .....
│  │  │  ├─ C/
│  │  │  │  ├─ .....
│  │  │  ├─ .....
│  │  └─ preprocessed_data.pkl.gz
│  ├─ models/
│  │  └─ final_model.h5
│  ├─ notebooks/
│  │  ├─ analyse-confusion-matrix.ipynb
│  │  ├─ create_data.ipynb
│  │  └─ train_model.ipynb
│  ├─ src/
│  │  └─ organize_chararcters.py
│  └─ utils/
│     ├─ 1st term summary.pdf
│     ├─ Analayzing the confusion matrix.pptx
│     ├─ accuracy.png
│     ├─ loss.png
│     └─ push large files.txt
└─ version_2/
   ├─ input/
   │  ├─ .gitattributes
   │  ├─ dataset.zip
   │  ├─ example_images/
   │  │  ├─ 000110.png
   │  │  ├─ 010111.png
   │  │  ├─ .....
   │  ├─ preprocessed_data.pkl.gz
   │  ├─ saved_data_info.txt
   │  ├─ test_p5/
   │  │  ├─ 1.png
   │  │  ├─ .....
   │  │  ├─ 680.png
   │  │  └─ test.rar
   │  └─ test_p6/
   │     ├─ 1.png
   │     ├─ .....
   │     ├─ 578.png
   │     └─ Page 6.rar
   ├─ models/
   │  └─ grade_1_model.h5
   ├─ notebooks/
   │  ├─ augmentation.ipynb
   │  ├─ inference.ipynb
   │  └─ train-model-custom-data.ipynb
   ├─ requirements.txt
   ├─ src/
   │  ├─ TTS.py
   │  ├─ inference.py
   │  ├─ main.py
   │  ├─ process_images.py
   │  └─ spell_checker.py
   └─ telegram_bot/
      ├─ TTS.py
      ├─ en_to_braille.py
      ├─ inference.py
      ├─ process_images.py
      ├─ speech_to_text.py
      ├─ spell_checker.py
      ├─ telegram_bot.py
      └─ tg_tqdm_v2.py
```
