import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from time import sleep
import os

staticPressure = -1
dynamicPressure = -1
droop = -1
staticDynamicTransition = -1
dynamicDepletionTransition = -1
# There may be other things we want to calculate, but start with these.


def processPressureData(currIndex):
    # Your code here
    # I would update those values inside this function.
    # print(currIndex)
    # print(currPressureData)
    return 0


waterflowData = pd.read_csv(os.getcwd() + "/data/WaterFlowTest_08_08_16_42")
tankData = waterflowData['low2'].to_numpy()

amountOfData = len(tankData)
print(amountOfData)
currPressureData = np.asarray([0] * amountOfData)

for i in range(0, amountOfData):
    currPressureData[i] = tankData[i]

    processPressureData(i)

    sleep(0.1)

    print("static pressure: {} psi, dynamic pressure: {} psi, droop: {} psi\nstaticDynamicTransition: {}, dynamicDepletionTransition: {}\n".format(
        staticPressure, dynamicPressure, droop, staticDynamicTransition, dynamicDepletionTransition))
