# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

## import data
df = pd.read_csv('H200925_CRT150A10_50W8M_2GPM_DMV_UUT3,A5D3.csv')

#Normal all 12
nums = range(12)
numsArr = []
numsArr.append([str(x+1).zfill(2) for x in nums])
TcSto = ["TcSto1Tank"+x for x in numsArr[0]]

# The other stuff to keep
#keep = ["Minutes", "CFMPStoOut", "CHP12In"]
keep=[]
keep.extend(TcSto)

df = df[keep].to_numpy()

# constants
#value = (np.amin(df)+np.amax(df))/2
value = 100

'''
Need to understand slope around the value with relation to volume. Allow to accurately fix each point set.
Use np.gradient. Index value closest to 'value'. Pull slopes.
Toss first and last rows. Find what temperature lines up with the max. 
- This part may have to be observational

'''

# finding the average from each tank sensor
#avg_data = np.average(df[:,:,:],axis=0)
avg_data = df.transpose()

## Now is where function would start

## create boolean array for if timestep contains value
# find min and max
mn = np.amin(avg_data[1:10,:],axis=0)
mx = np.amax(avg_data[1:10,:],axis=0)
# determine if temp value falls withing data
tf = np.all([mn<value, mx>value],axis=0)

## split array into list of arrays that contain value
# index where value exists
idx = np.where(tf!=False)[0]
# split into arrays that each contain value
arrs = np.split(avg_data[:,idx],np.where(np.diff(idx)!=1)[0]+1, axis=1)

a1 = arrs[1].flatten()
a2 = np.gradient(arrs[1], axis=0).flatten()
a = np.array([a1,a2])

plt.scatter(a1,a2)
plt.show

'''
For each timestep, find the nearease value and extrapolate to a volume array. 
'''
# volume fraction placeholder
#quick calcs on node weights
nodes = 12
topBottom_factor = 0
nodeWeights = np.array([1/nodes] * nodes)
nodeWeights[0] -= topBottom_factor/2.
nodeWeights[-1] -= topBottom_factor/2.
nodeWeights[1:-1] += topBottom_factor/10.
if sum(nodeWeights) != 1: Exception("nodeWeights doesn't sum to 1.")
volFract = nodeWeights.cumsum()#The top is 1... should there be an offset to bin centers?

# slope - fract of tank per degree
slope = -nodeWeights[3]/30


# index of closest
idx = np.abs(arrs[0]-value).argmin(axis=0)




## loop through each array and calcualte points
# start at close coords and work both directions.
# first work forward then, backward. 
# two loops or one loop. ()

# calculate length of each segment
arrs_len = [len(arrs[x][0,:]) for x in range(0,len(arrs))]

# find closest to 120 in each section for starter

