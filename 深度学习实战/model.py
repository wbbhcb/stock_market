# -*- coding: utf-8 -*-
"""
Created on Fri May 15 09:15:09 2020

@author: hcb
"""
from keras import layers
from keras import models
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv1D, MaxPooling1D, GlobalAveragePooling1D
from config import config

conf = config()

def build_model():
    model = Sequential()
    model.add(Conv1D(16, 6,strides=1, activation='relu',padding="same",input_shape=(conf.day,4)))
    model.add(Conv1D(16, 6,strides=1, activation='relu',padding="same"))
    model.add(MaxPooling1D(2))
    model.add(Conv1D(32, 3,strides=1, activation='relu',padding="same"))
    model.add(Conv1D(32, 3,strides=1, activation='relu',padding="same"))
    model.add(MaxPooling1D(2))
    model.add(Flatten())
    model.add(Dense(1, activation='sigmoid'))
    return model

if __name__ == '__main__':
    model = build_model()
    model.summary()