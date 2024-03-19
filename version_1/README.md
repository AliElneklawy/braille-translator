# Braille Translation

This project utilizes transfer learning to develop a deep learning model capable of translating American Braille characters into English characters. The model is built upon the DenseNet201 architecture, with the final layer removed and only the last 30 layers trainable.

# Project Motivation

Braille is a tactile writing system used by visually impaired individuals. While Braille has proven effective, there remains a need for efficient and accurate Braille-to-English translation tools. This project aims to address this need by employing transfer learning to develop a robust deep learning model for Braille translation.

# Model Architecture

The proposed model employs the DenseNet201 architecture, a convolutional neural network (CNN) known for its parameter efficiency and ability to handle complex tasks. The original DenseNet201 consists of 201 layers, with the final layer responsible for classification. For this project, the final layer is removed, and only the last 30 layers are trainable. This approach allows the model to leverage the pre-learned features from the original DenseNet201 while adapting to the specific task of Braille translation.

# Data Preparation

Link to the [dataset](https://www.kaggle.com/datasets/shanks0465/braille-character-dataset/). 

- Each image is a 28x28 image in BW Scale.
- Each image name consists of the character alphabet and the number of the image and the type of data augmentation it went through. (i.e whs - width height shift, rot - Rotation, dim - brightness).

The Braille images are preprocessed to ensure consistent size and normalization. The images were first resized to 224 * 224 to be consistent with the model requirements. The images were then normalized by dividing the entire image array by 255.0.

# Evaluation Results

The trained model is evaluated on a separate test dataset. The evaluation metric used is accuracy, which measures the proportion of correctly translated Braille characters. The model achieves an accuracy of 93.6%, indicating its ability to effectively translate Braille into English.



<div align="center">

### Test Classification Report

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
|   A   |   0.90    |  1.00  |   0.95   |    9    |
|   B   |   1.00    |  1.00  |   1.00   |    9    |
|   C   |   1.00    |  0.78  |   0.88   |    9    |
|   D   |   0.90    |  1.00  |   0.95   |    9    |
|   E   |   0.89    |  0.89  |   0.89   |    9    |
|   F   |   0.82    |  1.00  |   0.90   |    9    |
|   G   |   1.00    |  1.00  |   1.00   |    9    |
|   H   |   1.00    |  0.89  |   0.94   |    9    |
|   I   |   0.80    |  0.89  |   0.84   |    9    |
|   J   |   1.00    |  1.00  |   1.00   |    9    |
|   K   |   0.90    |  1.00  |   0.95   |    9    |
|   L   |   0.90    |  1.00  |   0.95   |    9    |
|   M   |   1.00    |  1.00  |   1.00   |    9    |
|   N   |   1.00    |  1.00  |   1.00   |    9    |
|   O   |   1.00    |  0.89  |   0.94   |    9    |
|   P   |   1.00    |  0.89  |   0.94   |    9    |
|   Q   |   1.00    |  1.00  |   1.00   |    9    |
|   R   |   1.00    |  0.78  |   0.88   |    9    |
|   S   |   1.00    |  1.00  |   1.00   |    9    |
|   T   |   0.89    |  0.89  |   0.89   |    9    |
|   U   |   1.00    |  0.89  |   0.94   |    9    |
|   V   |   0.90    |  1.00  |   0.95   |    9    |
|   W   |   1.00    |  0.89  |   0.94   |    9    |
|   X   |   1.00    |  1.00  |   1.00   |    9    |
|   Y   |   1.00    |  1.00  |   1.00   |    9    |
|   Z   |   0.90    |  1.00  |   0.95   |    9    |

Accuracy: 0.95

</div>



<p align="center">
  <b>Model Accuracy</b>
</p>

<p align="center">
  <img src="https://github.com/AliElneklawy/braille-translation/blob/main/utils/accuracy.png" alt="Model Accuracy" />
</p>

<p align="center">
  <b>Model Loss</b>
</p>

<p align="center">
  <img src="https://github.com/AliElneklawy/braille-translation/blob/main/utils/loss.png" alt="Model Loss" />
</p>

