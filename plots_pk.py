# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 14:38:52 2021

@author: paul
"""

# dataframe imports
import pandas as pd
import numpy as np

# plotly
from plotly import subplots
from plotly import graph_objs as go
import plotly.express as px
import matplotlib.pyplot as plt


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


plt.figure()
plt.scatter(df["Minutes"], df['CFMPStoOut'], c="b")
plt.scatter(df["Minutes"], df['CHP12In'], c="b")
plt.show()

# =============================================================================
# Slider plots
# =============================================================================
minute = 950
def plot_contour_frame(minute):
    dat = np.array([df.iloc[minute, 3:15],df.iloc[minute, 3:15]]).T
    fig = go.Figure(data =
        go.Contour(
            z=dat,
            x=[0, 1], # horizontal axis
            y=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], # vertical axis
            colorscale='Hot',
            contours=dict(
                start=40,
                end=150,
                size=10,
            ),
            reversescale = True,
        ))
    fig.update_yaxes(tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    fig.update_xaxes(tickvals=[])
    
    fig.show()

# Create figure
fig = go.Figure()
# Add traces, one for each slider step
for step in np.arange(00, 1440, 2):
    dat = np.array([df.iloc[step, 3:15],df.iloc[step, 3:15]]).T
    dat = np.flipud(dat)
    fig.add_trace(
        go.Contour(
            z=dat,
            x=[0, 1], # horizontal axis
            y=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], # vertical axis
            colorscale='Hot',
            contours=dict(
                start=40,
                end=150,
                size=10,
            ),
            name="Minute = " + str(step),

            reversescale = True,
            visible=False,
        ))

# Make 10th trace visible
fig.data[10].visible = True

# Create and add slider
steps = []
for i in range(len(fig.data)):
    step = dict(
        method="update",
        args=[{"visible": [False] * len(fig.data)},
              {"title": "Slider switched to step: " + str(i)}],  # layout attribute
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
    sliders=sliders
)
fig.write_html("output.html")

#fig.show()

