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



import numpy as np

class ThermalStorage:
    def __init__(self, site, tankConfig, sysConfig, tankVol, tankDia, tankHieght, numTanks, tankWallThick, sensLoc, measData):

        ''' Initial Attributes'''

        self.site = site                # string - location of storage system
        self.tankConfig = tankConfig    # string - configuration of storage system - series, parallel, single_tank
        self.sysConfig = sysConfig      # string - system configuration - temp_main_tank, return_primary
        
        # could be wrapped into tank object. 
        self.tankVol = tankVol                # float - volume of single tank in storage system, gallons
        self.tankDia = tankDia                # float - outer diameter of single tank in storage system, inches
        self.tankHieght = tankHieght             # float - height of cyclindrical portion of tank in storage system, inches
        self.tankWallThick = tankWallThick          # float - thickness of tank wall, inches
        
        self.numTanks = numTanks               # integer - number of tanks in storage system
        
        self.sensLoc = sensLoc          # array - sensor locations within cyclindrical portion of storage tank, [sensor, inches]
        
        self.measData = measData        # M&V or lab test data in specified format:
                                            # seconds, in_CW_temp, out_CW_temp, in_HW_temp, out_HW_temp,
                                            # flow_heat_pumps, flow_city_water
                                            # temperature sensor values - number depends on sensors.
                                            # exterior air temperature

        ''' Calculated Attributes'''
        
        self.sensVol = {}
        self.sensWeight = {}


        ''' Methods '''

    def calc_tankSensors(self):
        
        '''
        Function to calculate volume to each temperature sensor. Store as dictionary [sensor, gals]
        
        This is more of a tank attribute than a TES attribute. 
        '''
        
        # define dictionary for results
        sv = {}
        sw = {}
        
        # variables
        V = self.tankVol
        d = self.tankDia
        h = self.tankHieght
        t = self.tankWallThick
        
        sl = self.sensLoc
        
        # calculate volumes
        r = d/2-t                     # internal radius
        V_cyc = (h*np.pi*r**2)/231      # gals cyclinder
        V_head = (V-V_cyc)/2            # vol head
        V_perInch = V_cyc/h             # vol per inch cyc
        
        for key in sl:
            
            if sl[key] == 'bottom':
                sv[key] = 0
            elif sl[key] == 'top':
                sv[key] = V
            else:
                sv[key] = V_head + V_perInch*sl[key]
        
        for key in sv:
            sw[key] = sv[key]/V
        
        
        self.sensVol = sv
        self.sensWeight = sw

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
