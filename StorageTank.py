# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 17:42:34 2021

@author: scott
"""

import numpy as np

class StorageTank:
    def __init__(self, tankVol, tankDia, tankHieght, tankWallThick, sensLoc):

        ''' Initial Attributes'''
        
        # could be wrapped into tank object. 
        self.tankVol = tankVol                # float - volume of single tank in storage system, gallons
        self.tankDia = tankDia                # float - outer diameter of single tank in storage system, inches
        self.tankHieght = tankHieght             # float - height of cyclindrical portion of tank in storage system, inches
        self.tankWallThick = tankWallThick          # float - thickness of tank wall, inches
        
        self.sensLoc = sensLoc          # array - sensor locations within cyclindrical portion of storage tank, [top/ bottom/ or inches]
                
        self.sensVol = []
        self.sensWeight = []
        self.headVolume = None

    def calc_sens(self):
        
        '''
        Function to calculate volume to each temperature sensor. Store as dictionary [sensor, gals]
        
        This is more of a tank attribute than a TES attribute. 
        '''
        
        # define lists for results
        sv = []
        sw = []
        
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
        
        for x in sl:
            
            if x == 'bottom':
                sv.append(0)
            elif x == 'top':
                sv.append(V)
            else:
                sv.append(V_head + V_perInch*x)
        
        for x in sv:
            sw.append(x/V)
              
        self.headVolume = V_head
        self.sensVol = sv
        self.sensWeight = sw