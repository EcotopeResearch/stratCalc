# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 11:54:21 2021

@author: scott
"""

import numpy as np

from StorageTank import StorageTank

st1_temps=['bottom', 3.375,15.375,27.375,38.625,50.625,62.625, 'top']

st1 = StorageTank(tankVol=257, tankDia=30, tankHieght=66, tankWallThick=0.1875, sensLoc=st1_temps)
st1.calc_sens()

st2 = st1
st3 = st1

tanks = [st1, st2, st3]


total_volume = sum(x.tankVol for x in tanks)


# starting variables
tanks_vol = 0
sys_vol = []

for i in range(0,len(tanks)):
    
    for j in range(0,len(tanks[i].sensVol)): 
       sys_vol.append(tanks[i].sensVol[j] + tanks_vol) 
   
    tanks_vol = tanks_vol+tanks[i].tankVol

# =============================================================================
# 
# def tempLocParallel(tanks):
#     
# =============================================================================


st4_temps = np.linspace(2, 45, 12).tolist()

st4 = StorageTank(tankVol=119, tankDia=24, tankHieght=50, tankWallThick=0.1875, sensLoc=st4_temps)
st4.calc_sens()
