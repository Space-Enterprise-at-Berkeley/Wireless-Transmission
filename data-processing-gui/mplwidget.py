from  PyQt5.QtWidgets  import *
from  matplotlib.backends.backend_qt5agg  import  FigureCanvas
from  matplotlib.figure  import  Figure
import sys
import random
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
import scipy as sci
import numpy as np
import ntpath
import matplotlib.pyplot as plt
import pandas as pd
from time import sleep
import os
from numpy.fft import rfft, irfft
from scipy import signal
from scipy.signal import savgol_filter, lfilter
from statistics import mean

class MplWidget(QWidget):
    def __init__(self,parent=QWidget):
        QWidget.__init__(self, parent)
        self.canvas = FigureCanvas(Figure() )
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.setLayout(vertical_layout)
