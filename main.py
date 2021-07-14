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

def temp_profile(arr, volFract, v):

    '''
    Simplest strat calc. Cleans data. Linear around average slope. 
    '''

    ## CLEAN DATA, TRIM SO EACH TIME STEP CONTAINS VALUE OF INTEREST (V) 
    mn = np.amin(arr, axis=0) # find min of d0
    mx = np.amax(arr, axis=0) # find max of d0
    trim = np.all([mn<v, mx>v],axis=0) # boolean array True if value contained in d0 boundaries
    # delete rows that do not include value = v
    temps = np.delete(arr, np.invert(trim), axis=1)
    
    
    ## CALCULATE AVERAGE GRADIENT AT VALUE OF INTEREST
    grd = np.gradient(temps, axis=0) # np gradient function for axis=0 to find slop of temperature different
    # filter for values within +/- 5F of value (v)
    less = temps>v-5
    greater = temps<v+5
    both = np.logical_and(less, greater) # create boolean array True where close to value (v)
    avg_grad = np.average(grd[both]) # pull gradient values at True, take average
    
    # find slope relative to volFract, THIS ONLY WORKS WITH EVENLY DISTRIBUTED SENSORS.
    slope_grad = (pgeVolFract[2] - pgeVolFract[1])/avg_grad
    
    
    ## CALCULATE DATUM AS FRACTION OF TANK VOLUME
    # create indices for d0(row) and d1(column) to feed into array
    idx_d0 = np.abs(temps-v).argmin(axis=0) # index row with temperatures closest to value = v
    idx_d1 = np.arange(0,len(idx_d0)) # create index for each colum
    
    temps_idx = temps[[idx_d0],[idx_d1]] # array of temperatures at each step closest to value (v)
    temps_diff = ((value-temps_idx)*slope_grad)[0][:] # calculate volume offset based on average slope.
    
    # loop through idx_d0 (contains indices for temp sensor closet to value (v))
    # pull volFract at that temperature sensor.
    # add the difference calculated by temperature offset from value and average slope.
    datum = 1-(np.array([volFract[x] for x in idx_d0])+temps_diff)
    
    ## CREATE POSITION ARRAY, WHERE IS EACH TEMP SENSOR RELATIVE TO THE DATUM
    # 
    v = np.flip(np.array(volFract)).reshape(12,1)*np.ones((1,len(datum)))-datum

    return temps, slope_grad, datum, v

# =============================================================================
# pge_temp = temp_profile(tempsArr, pgeVolFract, value)
# plt.plot(pge_temp[0], pge_temp[3])
# plt.show()
# plt.savefig('fig.png')
# 
# import plotly.express as px
# fig = px.scatter(x=pge_temp[0].flatten(), y=pge_temp[3].flatten())
# fig.write_html("pge_scatter.html")
# =============================================================================

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
slope_grad = (pgeVolFract[2] - pgeVolFract[1])/avg_grad


# =============================================================================
# 
# =============================================================================

# create indices for d0(row) and d1(column) to feed into array
idx_d0 = np.abs(arrs[0]-value).argmin(axis=0) # index row with temperatures closest to value = v
idx_d1 = np.arange(0,len(idx_d0)) # create index for each colum

temps_idx = a1[[idx_d0],[idx_d1]] # 
temps_diff = ((value-temps_idx)*slope_grad)[0][:]


datum = np.array([pgeVolFract[x] for x in idx_d0])+temps_diff


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







