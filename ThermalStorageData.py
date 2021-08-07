#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 12:02:17 2021

@author: scott
"""
import numpy as np
from plotly import graph_objs as go
import plotly.colors

def get_continuous_color(intermed, colorscale = plotly.colors.PLOTLY_SCALES["Bluered"]):
    """
    Plotly continuous colorscales assign colors to the range [0, 1]. This function computes the intermediate
    color for any value in that range.

    Plotly doesn't make the colorscales directly accessible in a common format.
    Some are ready to use:
    
        colorscale = plotly.colors.PLOTLY_SCALES["Greens"]

    Others are just swatches that need to be constructed into a colorscale:

        viridis_colors, scale = plotly.colors.convert_colors_to_same_type(plotly.colors.sequential.Viridis)
        colorscale = plotly.colors.make_colorscale(viridis_colors, scale=scale)

    :param colorscale: A plotly continuous colorscale defined with RGB string colors.
    :param intermed: value in the range [0, 1]
    :return: color in rgb string format
    :rtype: str
    """
    if len(colorscale) < 1:
        raise ValueError("colorscale must have at least one color")

    if intermed <= 0 or len(colorscale) == 1:
        return colorscale[0][1]
    if intermed >= 1:
        return colorscale[-1][1]

    for cutoff, color in colorscale:
        if intermed > cutoff:
            low_cutoff, low_color = cutoff, color
        else:
            high_cutoff, high_color = cutoff, color
            break

    # noinspection PyUnboundLocalVariable
    return plotly.colors.find_intermediate_color(
        lowcolor=low_color, highcolor=high_color,
        intermed=((intermed - low_cutoff) / (high_cutoff - low_cutoff)),
        colortype="rgb")

class ThermalStorageData:
    def __init__(self, tempArr, flowArr, totalVolume, volFract,  midVal, midLinTol, method):
        '''
        

        Parameters
        ----------
        tempArr : TYPE
            DESCRIPTION.
        flowArr : TYPE
            DESCRIPTION.
        totalVolume : TYPE
            DESCRIPTION.
        volFract : TYPE
            DESCRIPTION.
        midVal : TYPE
            DESCRIPTION.
        midLinTol : TYPE
            DESCRIPTION.
        method : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''

        self.tempArr = tempArr
        self.flowArr = flowArr
        self.totalVolume = totalVolume
        self.volFract = volFract
        self.midVal = midVal
        self.midLinTol = midLinTol
        self.method = method

        self.clTempArrs = None # list of arrays
        self.clFlowArrs = None # list of arrays
        self.clPosArrs = None # list of arrays
        self.clBoolArr = None # array
        self.avgSlps = None # list of floats
        self.datum = None # fill line array
        
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
        flowArr = self.flowArr
        clBoolArr = self.clBoolArr
        method = self.method
        
        if method=='temp2' or method=='pos':
            ## split array into list of arrays that contain value
            # index where value exists
            idx = np.where(clBoolArr!=False)[0]
            # split into arrays that each contain value
            self.clTempArrs=np.split(tempArr[:,idx],np.where(np.diff(idx)!=1)[0]+1, axis=1)
            self.clFlowArrs=np.split(flowArr[idx],np.where(np.diff(idx)!=1)[0]+1)
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
        clFlowArrs = self.clFlowArrs
        volFract = self.volFract
        midVal = self.midVal
        method = self.method
        avgSlps = self.avgSlps
        vol = self.totalVolume
        
        posArrs = []
        datums = []
        
        for i in range(0,len(clTempArrs)):
            
            if method=='temp1' or method=='temp2':
                
                arr = clTempArrs[i]
                slp = -avgSlps[i]
                
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
                
            elif method=='pos':
                
                arr = clTempArrs[i]
                slp = -avgSlps[i]
                flows = clFlowArrs[i]
                
                idx_d0 = np.abs(arr-midVal).argmin(axis=0) # index row with temperatures closest to value = v
                idx_d1 = np.arange(0,len(idx_d0)) # create index for each colum
                
                # locate the closest value as base point for datum array
                temps_idx = arr[[idx_d0],[idx_d1]] # array of temperatures at each step closest to mid_value
                d1 = np.abs(temps_idx-midVal).argmin()
                d0 = np.abs(arr[:,d1][:]-midVal).argmin()
                
                # create cummulative flow array moving out from d1
                flow_sums = []
                for i in range(0,len(flows)):
                    if i<d1:
                        flow_sums.append(flows[i:d1].sum())
                    elif i==d1:
                        flow_sums.append(0)
                    elif i>d1:
                        flow_sums.append(flows[d1:i].sum())
                sumsArr = np.asarray(flow_sums)/vol
                
                # create starting point array
                posArr = np.flip(np.array(volFract)).reshape((len(volFract),1))*np.ones((1,arr.shape[1]))
                
                # alter datum array to zero out starting point at [d0,d1]
                init_val = posArr[d0,d1]
                closest_temp = arr[d0,d1]
                diff = init_val-(midVal-closest_temp)*slp
                datum = sumsArr-diff
                
                add = np.ones(posArr.shape)-1+datum
                posArrs.append(posArr+add)
                
                datums.append(datum)
            
            else:
                
                raise 'Please provide a method input of temp1, temp2, or pos'
            
        self.clPosArrs=posArrs
        self.datum=datums

    def plot_time(self, arr):
        '''
        

        Parameters
        ----------
        arr : TYPE
            DESCRIPTION.

        Returns
        -------
        fig : TYPE
            DESCRIPTION.

        '''
        
        temp_data = self.clTempArrs[arr].transpose()
        pos_data = self.clPosArrs[arr].transpose()
        
        fig = go.Figure()
        for i in range(0, len(temp_data)):
            fig.add_scatter(x=temp_data[i], y=pos_data[i], mode='markers', 
                            marker = dict(color=get_continuous_color(i/len(temp_data))))
        
        return fig
        
    def plot_pos(self, arr):
        '''
        

        Parameters
        ----------
        arr : TYPE
            DESCRIPTION.

        Returns
        -------
        fig : TYPE
            DESCRIPTION.

        '''
        
        temp_data = self.clTempArrs[arr]
        pos_data = self.clPosArrs[arr]
        
        fig = go.Figure()
        for i in range(0, len(temp_data)):
            fig.add_scatter(x=temp_data[i], y=pos_data[i], mode='markers', 
                            marker = dict(color=get_continuous_color(1-(i/len(temp_data)))))
            
        return fig
        