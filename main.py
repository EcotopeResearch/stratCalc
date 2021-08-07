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
mid_value = 105
spread = 5

# =============================================================================
# BUILD NUMPY ARRAYS FROM DATAFRAME
# =============================================================================

# create temperature data
tempsArr = df[TcSto].to_numpy().transpose()
# create flow data
flowArr = df[flow].transpose()

volFract = pgeVolFract


def temp_profile(temps_arr, mid_value, spread, volFract):

    ## CALCULATE AVERAGE GRADIENT AT VALUE OF INTEREST
    grd = np.gradient(temps_arr, axis=0) # np gradient function for axis=0 to find slop of temperature different
    
    # filter for values within +/- 5F of value (v)
    less = temps_arr>mid_value-spread
    greater = temps_arr<mid_value+spread
    both = np.logical_and(less, greater) # create boolean array True where close to value (v)
    avg_grad = np.average(grd[both]) # pull gradient values at True, take average
    
    '''THIS ONLY WORKS WITH EVENLY DISTRIBUTED SENSORS.'''
    # find slope relative to volFract, 
    slope_grad = (pgeVolFract[2] - pgeVolFract[1])/avg_grad
    
    
    ## CALCULATE DATUM AS FRACTION OF TANK VOLUME
    # create indices for d0(row) and d1(column) to feed into array
    idx_d0 = np.abs(temps_arr-mid_value).argmin(axis=0) # index row with temperatures closest to value = v
    idx_d1 = np.arange(0,len(idx_d0)) # create index for each colum
    
    temps_idx = temps_arr[[idx_d0],[idx_d1]] # array of temperatures at each step closest to value (v)
    temps_diff = ((mid_value-temps_idx)*slope_grad)[0][:] # calculate volume offset based on average slope.
    
    # loop through idx_d0 (contains indices for temp sensor closet to value (v))
    # pull volFract at that temperature sensor.
    # add the difference calculated by temperature offset from value and average slope.
    datumArr = 1-(np.array([volFract[x] for x in idx_d0])+temps_diff)
    
    ## CREATE POSITION ARRAY, WHERE IS EACH TEMP SENSOR RELATIVE TO THE DATUM
    # flip vol fract array so that highest fraction lines up with temp.
    # reshape for matrix math to make 12x1
    # multiply by 1xn array to create array where datum is always at tank bottom.
    # subtract datum array so that v 
    posArr = np.flip(np.array(volFract)).reshape(12,1)*np.ones((1,len(datumArr)))-datumArr

    ## RETURN LIST
    # position array
    # slop at mid_value
    # datum array
    return posArr, slope_grad, datumArr

def temp_profile_avg(tempsArr, mid_value, spread, volFract):

    '''
    Simplest strat calc. Cleans data. Linear around average slope. 
    '''

    ## CLEAN DATA, TRIM SO EACH TIME STEP CONTAINS VALUE OF INTEREST (V) 
    mn = np.amin(tempsArr, axis=0) # find min of d0
    mx = np.amax(tempsArr, axis=0) # find max of d0
    trim = np.all([mn<mid_value, mx>mid_value],axis=0) # boolean array True if value contained in d0 boundaries
    # delete rows that do not include value = v
    tempsArr = np.delete(tempsArr, np.invert(trim), axis=1)
    
    results = temp_profile(tempsArr, mid_value, spread, volFract)
    
    return tempsArr, results

def temp_profile_split(tempsArr, mid_value, spread, volFract):
    
    ## create boolean array for if timestep contains value
    # find min and max
    mn = np.amin(tempsArr,axis=0)
    mx = np.amax(tempsArr,axis=0)
    # determine if temp value falls withing data
    trim = np.all([mn<mid_value, mx>mid_value],axis=0)
    
    ## split array into list of arrays that contain value
    # index where value exists
    idx = np.where(trim!=False)[0]
    # split into arrays that each contain value
    arrs = np.split(tempsArr[:,idx],np.where(np.diff(idx)!=1)[0]+1, axis=1)

    results = []
    
    for i in range(0,len(arrs)):
        results.append(temp_profile(arrs[i], mid_value, spread, volFract))
    
    return arrs, results


# =============================================================================
# pge_temp = temp_profile_split(tempsArr, value, 5, pgeVolFract)
# plt.plot(pge_temp[0][0], pge_temp[1][0][0])
# plt.show()
# plt.savefig('fig.png')
# 
# import plotly.express as px
# fig = px.scatter(x=pge_temp[0][0].flatten(), y=pge_temp[1][0][0].flatten())
# fig.write_html("pge_scatter.html")
# =============================================================================


## create boolean array for if timestep contains value
# find min and max
mn = np.amin(tempsArr,axis=0)
mx = np.amax(tempsArr,axis=0)
# determine if temp value falls withing data
trim = np.all([mn<mid_value, mx>mid_value],axis=0)

## split array into list of arrays that contain value
# index where value exists
idx = np.where(trim!=False)[0]
# split into arrays that each contain value
arrs = np.split(tempsArr[:,idx],np.where(np.diff(idx)!=1)[0]+1, axis=1)

temps_arr = arrs[0]


## CALCULATE AVERAGE GRADIENT AT VALUE OF INTEREST
grd = np.gradient(temps_arr, axis=0) # np gradient function for axis=0 to find slop of temperature different

# filter for values within +/- 5F of value (v)
less = temps_arr>mid_value-spread
greater = temps_arr<mid_value+spread
both = np.logical_and(less, greater) # create boolean array True where close to value (v)
avg_grad = np.average(grd[both]) # pull gradient values at True, take average

'''THIS ONLY WORKS WITH EVENLY DISTRIBUTED SENSORS.'''
# find slope relative to volFract, 
slope_grad = (pgeVolFract[2] - pgeVolFract[1])/avg_grad

    

idx_d0 = np.abs(temps_arr-mid_value).argmin(axis=0) # index row with temperatures closest to value = v
idx_d1 = np.arange(0,len(idx_d0)) # create index for each colum

# locate the closest value as base point for datum array
temps_idx = temps_arr[[idx_d0],[idx_d1]] # array of temperatures at each step closest to mid_value
d1 = np.abs(temps_idx-mid_value).argmin()
d0 = np.abs(temps_arr[:,d1][:]-mid_value).argmin()


x0 = np.flip(np.array(pgeVolFract)).reshape((len(pgeVolFract),1))*np.ones((1,temps_arr.shape[1]))
pos_grd = np.gradient(x0,axis=0)

slp = np.average(pos_grd[both]/grd[both])


init_val = x0[d0,d1]
closest_temp = temps_arr[d0,d1]
diff = init_val-(mid_value-closest_temp)*slp # subtract datum array to get starting array




add = np.ones(x0.shape)*-diff+flowArr
