# -*- coding: utf-8 -*-
"""
Created on Wed May 12 07:10:56 2021

@author: scott
"""

'''
OUTLINE OF THERMAL STORAGE CLASS TO STANDARDIZE CALCULATION METHODOLOGY AND INCREASE EASE OF USE. 
'''

class ThermalStorage:
    def __init__(self, site, tankVol, tankDia, cyclHieght, numTanks, tankConfig, sysConfig, sensors,
                 measData, volFract, strat, eff, ua):
        
        #defin attributes
        self.site = site                # location of storage system               
        self.tankVol = tankVol          # volume of single tank in storage system
        self.tankDia = tankDia          # diameter of single tank in storage system
        self.cyclHieght = cyclHieght    # height of cyclindrical portion of tank in storage system
        self.numTanks = numTanks        # number of tanks in storage system
        self.tankConfig = tankConfig    # configuration of storage system - series, parallel, single_tank
        self.sysConfig = sysConfig      # system configuration - temp_main_tank, return_primary
        self.sensors = sensors          # sensor locations within cyclindrical portion of storage tank - list or dictionary
        self.measData = measData        # M&V or lab test data in specified format:
                                            # seconds, in_CW_temp, out_CW_temp, in_HW_temp, out_HW_temp, 
                                            # flow_heat_pumps, flow_city_water
                                            # temperature sensor values - number depends on sensors. 
        
        # Define functions
        def calc_volFract():            # calculate the volume fraction at each sensor in the tank system
            return None
        
        ## Combine vfill functions. Add option to create plot?

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
        
        
        
        
        
        
        