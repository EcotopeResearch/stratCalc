# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 11:54:21 2021

@author: scott
"""

from ThermalStorageData import ThermalStorageData
import pandas as pd
import matplotlib.pyplot as plt

# dataframe imports
import pandas as pd
import numpy as np
import seaborn as sns

# plotly
from plotly import subplots
from plotly import graph_objs as go
from plotly.offline import plot

import plotly.colors

# =============================================================================
# IMPORT DATA
# =============================================================================
# PG&E Data
df = pd.read_csv('H200925_CRT150A10_50W8M_2GPM_DMV_UUT3,A5D3.csv')
#df = df.rolling(7).mean()
# temp columns
nums = range(12)
numsArr = []
numsArr.append([str(x+1).zfill(2) for x in nums])
TcSto = ["TcSto1Tank"+x for x in numsArr[0]]
# flow columns
flow = ["CFMPStoOut", "CHP12In"]
# =============================================================================
# DEFINE TANK SENSOR GEOMETRY
# =============================================================================
pgeVolFract = [0.1332227326847979, 0.19556037100319193, 0.25789800932158596,
 0.32023564763997997, 0.38257328595837403, 0.4449109242767681, 0.507248562595162,
 0.5695862009135562, 0.6319238392319501, 0.6942614775503441, 0.7565991158687382,
 0.8189367541871321]
# =============================================================================
# DEFINE GLOBAL VARS
# =============================================================================
# define target temperature of strat middle
midVal = 120
midLinTol = 5
# =============================================================================
# BUILD NUMPY ARRAYS FROM DATAFRAME
# =============================================================================
# create temperature data
tempsArr = df[TcSto].to_numpy().transpose()
# create flow data
flowArr = df[flow].to_numpy().transpose()
flowArr = flowArr[1]-flowArr[0] # out - in
flowArr = flowArr

volFract = pgeVolFract


pgeData = ThermalStorageData(tempsArr, flowArr, 119, volFract, midVal, midLinTol, 'temp2')


plt.plot(pgeData.clTempArrs[1], pgeData.clPosArrs[1])
plt.show()
plt.savefig('fig.png')

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



# BASICS OF PLOT FUNCTION
# TRANSPOSE OF NOT TRANSPOSE 
# CHOOSE ARRAY TO PLOT

# =============================================================================
# temp_data = pgeData.clTempArrs[1].transpose()
# pos_data = pgeData.clPosArrs[1].transpose()
# 
# fig = go.Figure()
# for i in range(0, len(temp_data)):
#     fig.add_scatter(x=temp_data[i], y=pos_data[i], mode='markers', 
#                     marker = dict(color=get_continuous_color(i/len(temp_data))))
# =============================================================================

fig = pgeData.plot_time(1)
fig.write_html("fig_time.html")


fig = pgeData.plot_pos(1)
fig.write_html("fig_pos.html")




