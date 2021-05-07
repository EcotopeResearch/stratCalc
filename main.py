# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 14:38:52 2021

@author: paul
"""

# dataframe imports
import pandas as pd
import numpy as np
import seaborn as sns

# plotly
from plotly import subplots
from plotly import graph_objs as go
import plotly.express as px
import matplotlib.pyplot as plt
from plotly.offline import plot

# =============================================================================
# Parameters
# =============================================================================
tankVol = 119.
operateOnSmooth = False
nodes = 12
topBottom_factor = 0.


nodeWeights = np.array([1/nodes] * nodes)
nodeWeights[0] -= topBottom_factor/2.
nodeWeights[-1] -= topBottom_factor/2.
nodeWeights[1:-1] += topBottom_factor/10.
if sum(nodeWeights) != 1: Exception("nodeWeights doesn't sum to 1.")

sensorVolFractHeights = nodeWeights.cumsum()#The top is 1... should there be an offset to bin centers?
# =============================================================================
# #### Import data
# =============================================================================
df = pd.read_csv('H200925_CRT150A10_50W8M_2GPM_DMV_UUT3,A5D3.csv')

nums = range(12)
numsArr = []
numsArr.append([str(x+1).zfill(2) for x in nums])
TcSto = ["TcSto1Tank"+x for x in numsArr[0]]
keep = ["Minutes", "CFMPStoOut", "CHP12In"]
keep.extend(TcSto)

df = df[keep]

# Plot 
fig = px.line(df, x='Minutes', y=TcSto[0])
for Tc in TcSto[1:]:
    fig.add_scatter(x=df['Minutes'], y=df[Tc], mode='lines')
#plot(fig)    
fig.write_html("Temperature_with_Time.html")

#Smooth that data
TcStoS = [Tc + "Smooth" for Tc in TcSto]
df[TcStoS] = df[TcSto].rolling(7).mean()
# Plot 
fig = px.line(df, x='Minutes', y=TcStoS[0])
for Tc in TcStoS[1:]:
    fig.add_scatter(x=df['Minutes'], y=df[Tc], mode='lines')
#plot(fig)
fig.write_html("Smoothed_Temperature_with_Time.html")

# =============================================================================
# Process to find V_Fill
# =============================================================================
if operateOnSmooth:
    TcSto = TcStoS

# V fill using the volume method
df["dVFillVol"] =  df['CFMPStoOut'] - df['CHP12In']
df["VFillVol"] = df["dVFillVol"].cumsum()
df["VFillVol0ed"] = df['dVFillVol']
df["VFillVol0edFract"] = df['dVFillVol'] / tankVol

for ii in range(1, len(df['dVFillVol'])):
    df['VFillVol0ed'].iloc[ii] = max( 0, df['VFillVol0ed'].iloc[ii-1] + df['dVFillVol'].iloc[ii] )

# V fill using the temperature method
df["FillTemp"] =  (df[TcSto].max(axis=1) - df[TcSto].min(axis=1)) / 2 + df[TcSto].min(axis=1)
def interpWrap(df):
    xp = df[TcSto].sort_values()
    return np.interp(df["FillTemp"], xp, sensorVolFractHeights)
df["VFillTempFract"] = df.apply(interpWrap, axis=1) 
df["VFillTemp"] = df["VFillTempFract"]  * tankVol

# np.interp(df["FillTemp"][420], df[TcSto].loc[420], sensorVolFractHeights)
# Plots!
fig = go.Figure()
fig.add_scatter(x=df['Minutes'], y=df['VFillVol'], mode='lines',
                name = "Default VFill based of Volume in and out")
fig.add_scatter(x=df['Minutes'], y=df['VFillVol0ed'], mode='lines', 
                name = "VFill based of Volume Zeroed to Avoid Negatives")
fig.add_scatter(x=df['Minutes'], y=df['VFillTemp'], mode='lines', 
                name = "Vfill based off the Temperatures")
#plot(fig)
fig.write_html("VFill_with_time.html")

# =============================================================================
# What's next, we get those scatter plots
# =============================================================================

# =============================================================================
# # Create figure
# fig = go.Figure()
# # Add traces, one for each slider step
# for step in np.arange(00, 1440, 2):
#     dat = np.array(df[TcSto].iloc[step])
#     dat = np.flipud(dat)
#     fig.add_scatter( x=dat, # horizontal axis
#             y=sensorVolFractHeights, # vertical axis
#             #colorscale='Hot',
#             name="Minute = " + str(step),
#             #reversescale = True,
#             visible=False
#             )
# 
# # Make 10th trace visible
# fig.data[10].visible = True
# 
# # Create and add slider
# steps = []
# for i in range(len(fig.data)):
#     step = dict(
#         method="update",
#         args=[{"visible": [False] * len(fig.data)},
#               {"title": "Slider switched to step: " + str(i)}],  # layout attribute
#     )
#     step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
#     steps.append(step)
# 
# sliders = [dict(
#     active=10,
#     currentvalue={"prefix": "Minute: "},
#     pad={"t": 50},
#     steps=steps
# )]
# 
# fig.update_layout(
#     sliders=sliders
# )
# fig.write_html("output.html")
# =============================================================================
# function below sets the color based on amount
# =============================================================================
# def SetColor(x):
#     if(x >= 140):
#         return "red"
#     elif( 130 <= x < 140):
#         return "orange"
#     elif( 120 <= x < 130):
#         return "yellow"
#     elif( 110 <= x < 120):
#         return "green"
#     elif( x < 110):
#         return "blue"
#     
# =============================================================================
vfill = "VFillTempFract" #"VFillVol0edFract"
spaceFactor = 4
fig = go.Figure()
# Add traces, one for each slider step
for step in np.arange(00, 1440, 3):
    datum = df[vfill].iloc[step]
    dat = np.array(df[TcSto].iloc[step])
    dat = np.flipud(dat) + step*spaceFactor
    fig.add_scatter( x=dat, # horizontal axis
            y=sensorVolFractHeights - datum, # vertical axis
            #colorscale='Hot',
            name="Minute = " + str(step), mode='lines', 
            #reversescale = True,
           # line = dict(color = "red")
            #marker  = dict(color=list(map(SetColor, dat-step*spaceFactor)))
            )
fig.add_scatter( x=[0,step*spaceFactor], # horizontal axis
            y=[0,0], # vertical axis
            name="Minute = " + str(step), mode='lines',
            #dash = "dash", 
            line = dict(color = "black"))
fig.write_html("ScatterPlotForEachStep_zoomin.html")


# =============================================================================
# fits
# =============================================================================

def tan_fit(x, thickness, width, tempAtVFill):
    # Really we need to fit the width and slope at 0, this is a proxy for 
    # the thickness of thermocline
    # Period is pi/ width
    # Will have to worry about bounds
    return thickness * np.tan(np.pi / width * x - tempAtVFill)

def x3_fit(x, thickness, width, tempAtVFill):
        return thickness / width * (x - tempAtVFill)^3 #is this right? double check it.
