# -*- coding: utf-8 -*-
"""
Created on Wed May 12 07:10:56 2021

@author: scott
"""

'''
OUTLINE OF THERMAL STORAGE CLASS TO STANDARDIZE CALCULATION METHODOLOGY AND INCREASE EASE OF USE.

- Make plots more obvious or provide better descriptions.
- What the temps look like at any given time. Energy stored at time. FUNCITON
- How will we control for draw pattern? How will draw pattern affect the tank stratification

Define lessons we will learn from this:
- How to make systems more affordable
- How to pipe systems
- Ecosizer field validation

Improvements and priorities
-
- capture UA losses
-

Funding Sources


'''

class ThermalStorage:
    def __init__(self, site, tanks, config,  measData):

        ''' Initial Attributes'''

        self.site = site                # string - location of storage system       
        self.tanks = tanks              # list of StorageTank objects
        self.config = config            # series, parallel, or single tank
        self.measData = measData        # M&V or lab test data in specified format:
                                            # seconds, in_CW_temp, out_CW_temp, in_HW_temp, out_HW_temp,
                                            # flow_heat_pumps, flow_city_water
                                            # temperature sensor values - number depends on sensors.
                                            # exterior air temperature

        self.volume = sum(x.tankVol for x in self.tanks)
        self.sensLoc = []

    def calc_sens:(self):
        
        tanks = self.tanks
        
        # starting variables
        tanks_vol = 0
        sys_vol = []
        
        for i in range(0,len(tanks)):
            
            for j in range(0,len(tanks[i].sensVol)): 
               sys_vol.append(tanks[i].sensVol[j] + tanks_vol) 
           
            tanks_vol = tanks_vol+tanks[i].tankVol

        
        self.sensVol = sys_vol
        self.sensVol = 


    def calc_initVfill():           # calculate initial Vfill, option to specify time slice.
        # this function does not calculate an attribute but is used in strat and Vfill functions.
        return None

    def calc_vfill():               # calculate vfill over time period
        return None

    def plot_vfill():               # creates plot of vfill over time period
        return None

    ## Combine strat functions. Add option to create plot?

    def calc_strat():                # calculate the stratification function, option to specify time slice
        return None

    def plot_strat():               # create stratification plot, option to specify time slice
        return None

    def calc_eff():                 # calculate tank storage efficiency
        return None

    def calc_ua():                  # calculate UA of storage system
        return None
