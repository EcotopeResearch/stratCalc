# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
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

# Block 11 Data

# 23rd and Jackson Data

# Elizabeth James Data

# Bayview Data

# =============================================================================
# DEFINE TANK SENSOR GEOMETRY
# =============================================================================

pgeVolFract = [0.1332227326847979, 0.19556037100319193, 0.25789800932158596,
 0.32023564763997997, 0.38257328595837403, 0.4449109242767681, 0.507248562595162,
 0.5695862009135562, 0.6319238392319501, 0.6942614775503441, 0.7565991158687382,
 0.8189367541871321]

b11volFract = []

j23VolFract = []

ejamesVolFract = []

bviewVolFract = []

# =============================================================================
# DEFINE GLOBAL VARS
# =============================================================================

# define target temperature of strat middle
value = 105

# =============================================================================
# BUILD NUMPY ARRAYS FROM DATAFRAME
# =============================================================================

# create temperature data
tempsArr = df[TcSto].to_numpy().transpose()
# create flow data
flowArr = df[flow].transpose()


def temp_datum(arr, volFract, v):
    
    mn = np.amin(arr, axis=0) # find min of d0
    mx = np.amax(arr, axis=0) # find max of d0
    trim = np.all([mn<v, mx>v],axis=0) # boolean array True if value contained in d0 boundaries
    
    cleanArr = np.delete(arr, np.invert(trim), axis=1)
    
    return cleanArr
    
cleanArr = temp_datum(tempsArr, pgeVolFract, value)

# =============================================================================
# CLEAN DATA FOR PARTIALLY CHARGED TANKS
# =============================================================================

## create boolean array for if timestep contains value
# find min and max
mn = np.amin(tempsArr,axis=0)
mx = np.amax(tempsArr,axis=0)
# determine if temp value falls withing data
trim = np.all([mn<value, mx>value],axis=0)

## split array into list of arrays that contain value
# index where value exists
idx = np.where(trim!=False)[0]
# split into arrays that each contain value
arrs = np.split(tempsArr[:,idx],np.where(np.diff(idx)!=1)[0]+1, axis=1)

# =============================================================================
# FOR EACH SECTION, FIND THE GRADIANT AT THE 
# =============================================================================

a1 = arrs[0][:,:]
a2 = np.gradient(arrs[0][:,:], axis=0)

less = arrs[0]>100
greater = arrs[0]<110
both = np.logical_and(less, greater)

avg_grad = np.average(a2[both])


# function with arrs and VolFract inputs
slope_grad = pgeVolFract[2] - pgeVolFract[1] / avg_grad

# index of closest
idx_d0 = np.abs(arrs[0]-value).argmin(axis=0)
idx_d1 = np.arange(0,len(idx_d0))

temps_idx = a1[[idx_d0],[idx_d1]]
temps_diff = (value-temps_idx)*slope_grad

# =============================================================================
# c = []
# for i in range(0,len(idx)):
#     c.append(arrs[0][idx[i]][i])
# =============================================================================


'''
For each timestep, find the nearease value and extrapolate to a volume array. 
'''

# slope - fract of tank per degree
#slope = -nodeWeights[3]/30





