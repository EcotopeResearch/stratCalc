# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 11:54:21 2021

@author: scott
"""

import numpy as np
from ThermalStorageData import ThermalStorageData
import pandas as pd
import matplotlib.pyplot as plt

# =============================================================================
# IMPORT DATA
# =============================================================================
# PG&E Data
df = pd.read_csv('H200925_CRT150A10_50W8M_2GPM_DMV_UUT3,A5D3.csv')
# temp columns
nums = range(12)
numsArr = []
numsArr.append([str(x+1).zfill(2) for x in nums])
TcSto = ["TcSto1Tank"+x for x in numsArr[0]]
# flow columns
flow = ["CFMPStoOut", "CHP12In"]
# =============================================================================
# DEFINE TANK SENSOR GEOMETRY
# =============================================================================
pgeVolFract = [0.1332227326847979, 0.19556037100319193, 0.25789800932158596,
 0.32023564763997997, 0.38257328595837403, 0.4449109242767681, 0.507248562595162,
 0.5695862009135562, 0.6319238392319501, 0.6942614775503441, 0.7565991158687382,
 0.8189367541871321]
# =============================================================================
# DEFINE GLOBAL VARS
# =============================================================================
# define target temperature of strat middle
midVal = 105
midLinTol = 5
# =============================================================================
# BUILD NUMPY ARRAYS FROM DATAFRAME
# =============================================================================
# create temperature data
tempsArr = df[TcSto].to_numpy().transpose()
# create flow data
flowArr = df[flow].transpose()
volFract = pgeVolFract


pgeData = ThermalStorageData(tempsArr, flowArr, volFract, midVal, midLinTol, 'temp1')


