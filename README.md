# Coolambury

*Coolambury* is a word guessing and drawing game - commonly known as *charades*. The game was created by a group of 4 Masters Degree students from the University of Technology and Science in Poland, Kraków (AGH). The goal of the project was to create an application using web communication between clients. In order to satisfy the requirements, we have chosen to create a Socket based Server alongside the Client written mainly in PyQt5.

## Game Flow
The client allows the user to specify his/her nickname used in the game as well as choose the desired game room from the list or using a game room code. Users can also create a room, therefore becoming a host. BOT joins every room by default. When a sufficient amount of players (2 + BOT) join the room, the game can be started by the game host. An artist is chosen by the game server and is presented with three word options to choose from and later draw it. Both the artist and the person who will have guessed are awarded points. As time passes users are given hints of the words (subsequent letters are being unveiled). The game finishes when any of the players gather 500 points.  

## Authors and Responsibilities:

Michał Loska - @michalloska
  - Client Communication with Server (Sockets)
  - Partial PyQt5 implementation
  - PyTest
  - Pre-commit package configuration

Michał Zbrożek - @Atloas
  - Client Implementation in PyQt

Adrian Wysocki - @theratty
  - Server Implementation
  - Game Communication 

Piotr Witkoś - @Witkod
  - QuickDraw Bot Implementation

## Main Packages Used: 
- PyQt5
- PyTest
- QuickDraw
- Pre-commit

## Setup

### Running the Server
Server can be run using a simple command:

> make server

### Running the Client
Client can be run with a command:

> make client <_config_file_._json_>

or when using powershell with the following commands:

> env:PYTHONPATH = "./Client"

> python .\Client\RunClient.py .\configRemote.json

### Config File

Config file stores Connection setup data which allows the Client to connect to the game server

example config file:
```
{
    "PORT": 5050,
    "HEADER_LEN": 256,
    "SERVER": "localhost",
    "model_path": "./Server/resources/model.h5",
    "labels_path": "./Server/resources/labels.csv"
}
```
where *labels_path* is a list of existing game phrases and *model_path* is a pre-supplied bot model (should remain untouched) 

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
