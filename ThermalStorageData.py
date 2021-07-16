#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 12:02:17 2021

@author: scott
"""
import numpy as np

class ThermalStorageData:
    def __init__(self, tempArr, flowArr, volFract,  midVal, midLinTol, method):
        '''
        

        Parameters
        ----------
        tempArr : numpy array
            DESCRIPTION.
        flowArr : numpy array
            DESCRIPTION.
        volFract : numpy array
            DESCRIPTION.
        midVal : float
            DESCRIPTION.
        midLinTol : float
            DESCRIPTION.
        method : string
            DESCRIPTION.

        Returns
        -------
        None.

        '''

        self.tempArr = tempArr
        self.flowArr = flowArr
        self.volFract = volFract
        self.midVal = midVal
        self.midLinTol = midLinTol
        self.method = method

        self.clTempArrs = None # list of arrays
        self.clFlowArrs = None # list of arrays
        self.clPosArrs = None # list of arrays
        self.clBoolArr = None # array
        self.avgSlps = None # list of floats
        
        self.calc_clBool()
        self.calc_clTempArrs()
        self.calc_slope()
        self.calc_clPosArrs()

    def calc_clBool(self):
        '''
        
        
        Returns
        -------
        None.
        '''
        tempArr = self.tempArr
        midVal = self.midVal
        
        mn = np.amin(tempArr, axis=0) # find min of d0
        mx = np.amax(tempArr, axis=0) # find max of d0
        clBoolArr = np.all([mn<midVal, mx>midVal],axis=0) # boolean array True if value contained in d0 boundaries
        
        self.clBoolArr = clBoolArr
        
    def calc_clTempArrs(self):
        '''
        
        
        Returns
        -------
        None.
        '''
        
        tempArr = self.tempArr
        clBoolArr = self.clBoolArr
        method = self.method
        
        if method=='temp2' or method=='position':
            ## split array into list of arrays that contain value
            # index where value exists
            idx = np.where(clBoolArr!=False)[0]
            # split into arrays that each contain value
            self.clTempArrs=np.split(tempArr[:,idx],np.where(np.diff(idx)!=1)[0]+1, axis=1)
        elif method=='temp1':
            # delete rows that do not include value = v
            self.clTempArrs=[np.delete(tempArr, np.invert(clBoolArr), axis=1)]
        else:
            raise 'Please provide a method input of temp1, temp2, or position'
            
    def calc_slope(self):
        '''
        

        Returns
        -------
        None.

        '''
        
        clTempArrs = self.clTempArrs
        volFract = self.volFract
        midVal = self.midVal
        midLinTol = self.midLinTol
        
        slp = []
        
        for i in range(0, len(clTempArrs)):            
            arr = clTempArrs[i]            
            # create boolean area for values withing linear tolerance
            less = arr>midVal-midLinTol
            greater = arr<midVal+midLinTol
            both = np.logical_and(less, greater) # create boolean array True where close to value (v)
            
            # calculate gradient of temperatures
            tempGrd = np.gradient(arr, axis=0) # np gradient function for axis=0 to find slop of temperature different
            
            # calculate gradient of sensor volumes
            x0 = np.flip(np.array(volFract)).reshape((len(volFract),1))*np.ones((1,arr.shape[1])) # starting posistion array
            posGrd = np.gradient(x0,axis=0)
            
            # calculate slope - change in volume over change in temperature
            slp.append(np.average(posGrd[both]/tempGrd[both]))
            
        self.avgSlps = slp
        
    def calc_clPosArrs(self):
        '''
        

        Returns
        -------
        None.
        
        '''
        clTempArrs = self.clTempArrs
        volFract = self.volFract
        midVal = self.midVal
        method = self.method
        avgSlps = self.avgSlps
        
        posArrs = []
        
        for i in range(0,len(clTempArrs)):
            
            if method=='temp1' or method=='temp2':
                
                arr = clTempArrs[i]
                slp = avgSlps[i]
                
                ## CALCULATE DATUM AS FRACTION OF TANK VOLUME
                # create indices for d0(row) and d1(column) to feed into array
                idx_d0 = np.abs(arr-midVal).argmin(axis=0) # index row with temperatures closest to value = v
                idx_d1 = np.arange(0,len(idx_d0)) # create index for each colum
                
                temps_idx = arr[[idx_d0],[idx_d1]] # array of temperatures at each step closest to value (v)
                temps_diff = ((midVal-temps_idx)*slp)[0][:] # calculate volume offset based on average slope.
                
                # loop through idx_d0 (contains indices for temp sensor closet to value (v))
                # pull volFract at that temperature sensor.
                # add the difference calculated by temperature offset from value and average slope.
                datumArr = 1-(np.array([volFract[x] for x in idx_d0])+temps_diff)
                
                ## CREATE POSITION ARRAY, WHERE IS EACH TEMP SENSOR RELATIVE TO THE DATUM
                # flip vol fract array so that highest fraction lines up with temp.
                # reshape for matrix math to make 12x1
                # multiply by 1xn array to create array where datum is always at tank bottom.
                # subtract datum array so that v 
                posArrs.append(np.flip(np.array(volFract)).reshape(12,1)*np.ones((1,len(datumArr)))-datumArr)
                
            elif method=='position':
                
                raise 'position method not yet coded'
            
            else:
                
                raise 'Please provide a method input of temp1, temp2, or position'
            
        self.clPosArrs=posArrs
        