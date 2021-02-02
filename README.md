# Coolambury

# NN Model

In our project neuron network model has a role of an additional player in every game who only tries to guess an answer. He can't draw but anyway "he" scores his points if he forestall other users.

We used a Convolutional Neuron Network architecture.
Network has been trained on subset of data which comes from quickdraw dataset which contains more than 50 milion drawings across 345 categories.
Data which is recognised are simplified drawings stored in Numpy bitmaps. Bitmaps are 28x28 grayscale images.

The model is created from folowing layers:
Conv2D(32, (5,5), activation='relu')
MaxPooling2D(pool_size=(2, 2))
Conv2D(128, (3, 3), activation='relu')
MaxPooling2D(pool_size=(2, 2))
Dropout(0.2)
Flatten()
Dense(512, activation='relu')
Dense(256, activation='relu')
Dense(num_classes, activation='softmax')

Every category has been trained on 5000 examples of drawings.

Here is the result of training process:
![alt text](https://github.com/jtheiner/SketchRecognition/blob/master/SketchRecognition/recognition/models/345/5000/training_process.png?raw=true)

The network accuracy shows following confusion matrix:
![alt text](https://github.com/jtheiner/SketchRecognition/raw/master/SketchRecognition/recognition/models/20/10000/confusion_matrix.png)
