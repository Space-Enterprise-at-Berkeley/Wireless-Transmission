import pandas as pd
import numpy as np
import scipy as sc
from scipy.interpolate import interp1d

import os


def initHighPressure():
    data = pd.read_csv(
        os.getcwd() + "/../waterflow_test/high_pt_characterization_10_10")
    highPressureConversionFunc = interp1d(
        data['raw'], data['digital'], kind='quadratic')
    # print(type(highPressureConversionFunc))
    # print(highPressureConversionFunc(900))
    return highPressureConversionFunc


def lowPressureConversion(raw):  # raw is a value from 0 to 1024 (10bit ADC)
    return 1.2258857538273733 * raw * (1024 / pow(2, 23)) - 123.89876445934394
#
#
# def highPressureConversion(raw):  # raw is a value from 0 to 1024 (10bit ADC)
    # return highPressureConversionFunc(raw)
