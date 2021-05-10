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
[sum(nodeWeights[i::2]) for i in range(len(nodeWeights) // 2)]
# =============================================================================
# Functions
# =============================================================================
# V fill using the temperature method
def interpWrap(dft, TcNames, volFracts):
    xp = dft[TcNames].sort_values()
    return np.interp(dft["FillTemp"], xp, volFracts)
def vfill_temperature_method(dft, TcNames, volFracts = sensorVolFractHeights, vol = tankVol):
    """

    Args:
        dft (pandas data frame): data frame we're working on, I hope it passes a copy and not a pointer.
        TcNames (TYPE): The names of the thermocouples to operate on in the data frame.

    Returns:
        TYPE: Panda Series. The calcualed fill temperature.
        TYPE: Panda Series. The calculated vfill datum based referenced as a fraction of tank vol.
        TYPE: Panda Series. The calculated vfill datum based on the total tank volume, height from bottom.

    """
    dft["FillTemp"] =  (dft[TcNames].max(axis=1) - dft[TcNames].min(axis=1)) / 2 + dft[TcNames].min(axis=1)
    dft["VFillTempFract"] = dft.apply(interpWrap, TcNames=TcNames, volFracts=volFracts, axis=1) 
    dft["VFillTemp"] = dft["VFillTempFract"]  * vol
    return dft["FillTemp"], dft["VFillTempFract"], dft["VFillTemp"]

# =============================================================================
# #### Import data
# =============================================================================
df = pd.read_csv('H200925_CRT150A10_50W8M_2GPM_DMV_UUT3,A5D3.csv')

#Normal all 12
nums = range(12)
numsArr = []
numsArr.append([str(x+1).zfill(2) for x in nums])
TcSto = ["TcSto1Tank"+x for x in numsArr[0]]

# The other stuff to keep
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
# Process to find V_Fill for 12 and 6 nodes
# =============================================================================
if operateOnSmooth:
    TcSto = TcStoS
    
# Get string columns for oddds
TcSto6Odd = TcSto[0::2]
sensorVolFractHeights6Odd = sensorVolFractHeights[0::2]

# Get string columns for evens
TcSto6Even = TcSto[1::2]
sensorVolFractHeights6Even = sensorVolFractHeights[1::2]

# V fill using the volume method
df["dVFillVol"] =  df['CFMPStoOut'] - df['CHP12In']
df["VFillVol"] = df["dVFillVol"].cumsum()
df["VFillVol0ed"] = df['dVFillVol']
df["VFillVol0edFract"] = df['dVFillVol'] / tankVol

for ii in range(1, len(df['dVFillVol'])):
    df['VFillVol0ed'].iloc[ii] = max( 0, df['VFillVol0ed'].iloc[ii-1] + df['dVFillVol'].iloc[ii] )

df["FillTemp12"], df["VFillTemp12Fract"], df["VFillTemp12"] = \
    vfill_temperature_method(df, TcSto, sensorVolFractHeights)
df["FillTemp6Odd"], df["VFillTemp6OddFract"], df["VFillTemp6Odd"] = \
    vfill_temperature_method(df, TcSto6Odd, sensorVolFractHeights6Odd)
df["FillTemp6Even"], df["VFillTemp6EvenFract"], df["VFillTemp6Even"] = \
    vfill_temperature_method(df, TcSto6Even, sensorVolFractHeights6Even)

# np.interp(df["FillTemp"][420], df[TcSto].loc[420], sensorVolFractHeights)
# Plots!
fig = go.Figure()
fig.add_scatter(x=df['Minutes'], y=df['VFillVol'], mode='lines',
                name = "Default VFill based of Volume in and out")
fig.add_scatter(x=df['Minutes'], y=df['VFillVol0ed'], mode='lines', 
                name = "VFill based of Volume Zeroed to Avoid Negatives")
fig.add_scatter(x=df['Minutes'], y=df['VFillTemp12'], mode='lines', 
                name = "Vfill based off 12 Temperatures")
fig.add_scatter(x=df['Minutes'], y=df['VFillTemp6Odd'], mode='lines', 
                name = "Vfill based off 6 Temperatures Odd Nodes")
fig.add_scatter(x=df['Minutes'], y=df['VFillTemp6Even'], mode='lines', 
                name = "Vfill based off 6 Temperatures Even Nodes")

#plot(fig)
fig.write_html("VFill_with_time.html")

# =============================================================================
# What's next, we get those scatter plots
# =============================================================================
vfill = "VFillTempFract" #"VFillVol0edFract"

# Create figure
fig = go.Figure()
# Add traces, one for each slider step
for step in np.arange(00, 1440, 3):
    datum = df[vfill].iloc[step]
    dat = np.array(df[TcSto].iloc[step])
    dat = np.flipud(dat)
    fig.add_scatter( x=dat, # horizontal axis
            y=sensorVolFractHeights - datum, # vertical axis
            #colorscale='Hot',
            name="Minute = " + str(step),
            #reversescale = True,
            visible=False
            )

# Make 10th trace visible
fig.data[90].visible = True

# Create and add slider
steps = []
for i in range(len(fig.data)):
    step = dict(
        method="update",
        args=[{"visible": [False] * len(fig.data)},
              {"title": "Slider switched to minute: " + str(i)}],  # layout attribute
    )
    step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
    steps.append(step)

sliders = [dict(
    active=10,
    currentvalue={"prefix": "Minute: "},
    pad={"t": 50},
    steps=steps
)]
fig.update_layout(
    #title="Plot Title",
    xaxis_title="Temperature (F)",
    yaxis_title="Fraction of Tank Volume",
    sliders=sliders
)
fig.write_html("ScatterPlotSlidderReferencedTo_" + vfill + ".html")
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
# vfill = "VFillTempFract" #"VFillVol0edFract"
# spaceFactor = 4
# fig = go.Figure()
# # Add traces, one for each slider step
# for step in np.arange(00, 1440, 3):
#     datum = df[vfill].iloc[step]
#     dat = np.array(df[TcSto].iloc[step])
#     dat = np.flipud(dat) + step*spaceFactor
#     fig.add_scatter( x=dat, # horizontal axis
#             y=sensorVolFractHeights - datum, # vertical axis
#             #colorscale='Hot',
#             name="Minute = " + str(step), mode='lines', 
#             #reversescale = True,
#             # line = dict(color = "red")
#             #marker  = dict(color=list(map(SetColor, dat-step*spaceFactor)))
#             )
# fig.add_scatter( x=[0,step*spaceFactor], # horizontal axis
#             y=[0,0], # vertical axis
#             name="Minute = " + str(step), mode='lines',
#             #dash = "dash", 
#             line = dict(color = "black"))
# fig.write_html("ScatterPlotForEachStep_zoomin.html")


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
