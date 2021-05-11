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

# =============================================================================
# Parameters
# =============================================================================
tankVol = 119.
operateOnSmooth = True
nodes = 12
topBottom_factor = 0.
    
vfill = "VFillTempFract" #"VFillVol0edFract"
vfill = "VFillVol0edFract" 

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

#Smooth that data
TcStoS = [Tc + "Smooth" for Tc in TcSto]
df[TcStoS] = df[TcSto].rolling(7).mean()

#quick calcs on node weights
nodeWeights = np.array([1/nodes] * nodes)
nodeWeights[0] -= topBottom_factor/2.
nodeWeights[-1] -= topBottom_factor/2.
nodeWeights[1:-1] += topBottom_factor/10.
if sum(nodeWeights) != 1: Exception("nodeWeights doesn't sum to 1.")

sensorVolFractHeights = nodeWeights.cumsum()#The top is 1... should there be an offset to bin centers?

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
for ii in range(1, len(df['dVFillVol'])):
    df['VFillVol0ed'].iloc[ii] = max( 0, df['VFillVol0ed'].iloc[ii-1] + df['dVFillVol'].iloc[ii] )
df["VFillVol0edFract"] = df['VFillVol0ed']/tankVol

df["FillTemp12"], df["VFillTemp12Fract"], df["VFillTemp12"] = \
    vfill_temperature_method(df, TcSto, sensorVolFractHeights)
df["FillTemp6Odd"], df["VFillTemp6OddFract"], df["VFillTemp6Odd"] = \
    vfill_temperature_method(df, TcSto6Odd, sensorVolFractHeights6Odd)
df["FillTemp6Even"], df["VFillTemp6EvenFract"], df["VFillTemp6Even"] = \
    vfill_temperature_method(df, TcSto6Even, sensorVolFractHeights6Even)

# =============================================================================
# Plot those temperatures!
# =============================================================================
# Plot 
fig = go.Figure()
for Tc in TcSto:
    fig.add_scatter(x=df['Minutes'], y=df[Tc], mode='lines')
fig.add_scatter(x=df['Minutes'],y=df["FillTemp12"], name="FillTemp12", line = dict(dash="dash"))
fig.add_scatter(x=df['Minutes'],y=df["FillTemp6Odd"], name="FillTemp6Odd", line = dict(dash="dash"))
fig.add_scatter(x=df['Minutes'],y=df["FillTemp6Even"], name="FillTemp6Even", line = dict(dash="dash"))
fig.write_html("Temperature_with_Time.html")

# Smoothed Plot 
fig = go.Figure()
for Tc in TcStoS:
    fig.add_scatter(x=df['Minutes'], y=df[Tc], mode='lines', name=Tc)
fig.add_scatter(x=df['Minutes'],y=df["FillTemp12"], name="FillTemp12", line = dict(dash="dash"))
fig.add_scatter(x=df['Minutes'],y=df["FillTemp6Odd"], name="FillTemp6Odd", line = dict(dash="dash"))
fig.add_scatter(x=df['Minutes'],y=df["FillTemp6Even"], name="FillTemp6Even", line = dict(dash="dash"))
fig.write_html("Smoothed_Temperature_with_Time.html")

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
# fits
# =============================================================================
from scipy.optimize import curve_fit, basinhopping, dual_annealing

def tan_fit(x, thickness, width, offset, tempAtVFill):
    # Really we need to fit the width and slope at 0, this is a proxy for 
    # the thickness of thermocline
    # Period is pi/ width
    # Will have to worry about bounds
    # x is the temperature
    # y is the tank heights
    return thickness * np.tan(np.pi / width * x + tempAtVFill ) + offset

def x3_fit(x, B, C, D, offset, tempAtVFill):
    return B * (x - tempAtVFill)**3 + \
        C * (x - tempAtVFill)**5  + D * (x - tempAtVFill)**7 + offset #is this right? double check it.
def logit_fit(x, A, middle, maxVal, minVal ):
    return A * np.log((x-minVal) / ((maxVal-minVal) - (x-minVal) )) + middle
def genLogistic(x, lowAsym, upAsym, growthRate, intercept, nu):
    #https://en.wikipedia.org/wiki/Generalised_logistic_function
    return lowAsym + (upAsym - lowAsym) /\
        ( 1 + intercept * np.exp(-growthRate * x) )**(1/nu)


def functx3(x):
    yfit = x3_fit(xdata, *x)
    return sum((ydata - yfit)**2) #least squares
def function(x):
    yfit = tan_fit(xdata, *x)
    return sum((ydata - yfit)**2) #least squares
def functlogistic(x): # note ydta and xdata switch
    yfit = genLogistic(ydata, *x)
    return sum((xdata - yfit)**2) #least squares

# def func(x, a, b, c):
#     return a * np.exp(-b * x) + c
#popt, pcov = curve_fit(func, xdata, ydata, bounds=(0, [3., 1., 0.5]))
firstInd = 7
length = df[TcSto][firstInd:].size
# get the temperatures flattened out
#xdata = np.resize(df[TcSto][firstInd:],(1,length))[0] #gotta kill that extra dimension
# get the all the heights flattened out. note the differenece between tile (array by array) and repeat (element by element)
#ydata = np.tile(sensorVolFractHeights, int(length/12)) - np.repeat(df[vfill][firstInd:],12)
# Fudge brute force it
xdata = []
ydata = []
for step in np.arange(firstInd, 1440):
    tempT = np.array(df[TcSto].iloc[step])
    tempT = np.flipud(tempT)
    xdata = np.append(xdata, tempT)
    
    datum = df[vfill].iloc[step]
    ydata = np.append(ydata, sensorVolFractHeights-datum)
    
#def tan_fit(x, thickness, width, offset, tempAtVFill)
boundstan = ([0., -200., -1.,-500],[10., 500., 1., 500.])
boundsx3 = ([-10., -5.,-5., -1.,0.],[10., 5., 5., 4., 200.])
boundslogit = ([0.1, 0., 0.,0.],[100., 100., 200., 200.])
boundslogistic = ([50, 120., 0., .1, 0.1],[80., 160., 30., 10., 6.])
x0tan = [.1, 60., .04, 100.]
x0x3 = [0.0001, 0.00008, 0.00000001, -0.004, 110.]
x0logit = [.2, .2, 150, 60 ]
#def genLogistic(x, lowAsym, upAsym, growthRate, nu, intercept): 
x0logistic = [65., 140., 15., 0.1, 1.] 

popt, pcov = curve_fit(x3_fit, xdata, ydata, bounds=boundsx3, #method="dogbox",
                        p0=x0x3)# initila guess
#ValueError: Residuals are not finite in the initial point. can cause these infite fits some issues...
poptlog, pcovlog = curve_fit(genLogistic, ydata, xdata, bounds=boundslogistic, 
                        p0=x0logistic)# initila guess


callnum = 0
def printf(x, f, context):
    global callnum
    callnum += 1
    #if callnum%10 == 0:
    print("at call %d, f: %.4f context %d" % (callnum, f, int(context)))

# =============================================================================
# More advanced fitting methods
# =============================================================================
# callnum = 0
# rettan = dual_annealing(function, x0 = x0tan,
#                      bounds = list(zip(boundstan[0],boundstan[1])),
#                      maxiter=1000, 
#                      initial_temp=5230.0, # If temperature is low less likely to jump
#                      restart_temp_ratio=2e-05, # Restarts temperature when it's low. 
#                      visit=3, # Visit controls how far we look out. 
#                      no_local_search = True, # with no_local_search = True this is traditional Generalized Simulated Annealing we'll get to this next
#                      callback=printf
#                      )

# callnum = 0
# retlogistic = dual_annealing(functlogistic, x0 = x0logistic,
#                      bounds = list(zip(boundslogistic[0],boundslogistic[1])),
#                      maxiter=1000, 
#                      initial_temp=5230.0, # If temperature is low less likely to jump
#                      restart_temp_ratio=2e-05, # Restarts temperature when it's low. 
#                      visit=3000, # Visit controls how far we look out. 
#                      no_local_search = False, # with no_local_search = True this is traditional Generalized Simulated Annealing we'll get to this next
#                      callback=printf
#                      )
# =============================================================================
# Plots...
# =============================================================================
# xline = np.linspace(62, 145, 100)
# yline =  np.linspace(-.5, 1, 100)
# plt.plot(xdata, ydata, 'b.', label='data')
# plt.plot(xline, x3_fit(xline, *popt), 'g--')
# #plt.plot(genLogistic(yline, *x0logistic), yline, 'k--')
# plt.plot(genLogistic(yline, *poptlog), yline, 'r--')
# # plt.plot(genLogistic(yline, *retlogistic.x), yline, 'm--')


# =============================================================================
# What's next, we get those scatter plots
# =============================================================================
if False:
    # Create figure
    fig = go.Figure()
    # Add traces, one for each slider step
    for step in np.arange(00, 1440, 4):
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
def SetColorTemp(x):
    if(x >= 140):
        return "red"
    elif( 130 <= x < 140):
        return "orange"
    elif( 120 <= x < 130):
        return "yellow"
    elif( 110 <= x < 120):
        return "green"
    elif( x < 110):
        return "blue"

spaceFactor = 4
fig = go.Figure()
# Add traces, one for each slider step
for step in np.arange(60, 1440, spaceFactor):
    datum = df[vfill].iloc[step]
    dat = np.array(df[TcSto].iloc[step])
    dat = np.flipud(dat)
    fig.add_scatter( x=dat, # horizontal axis
            y=sensorVolFractHeights - datum, # vertical axis
            mode='markers',
            name="Minute = " + str(step), 
            #reversescale = True,
            # line = dict(color = "red")
            #marker  = dict(color=list(map(SetColorTemp, dat)))
            marker = dict(color=get_continuous_color(step/1440))
            )
# add the fit
xline = np.linspace(62, 145, 100)
fig.add_scatter( x=genLogistic(yline, *poptlog), y=yline, mode="lines",
                name = "Best fit logistic", 
                line = dict(color="black", 
                           # dash='dash',
                            width=4))        
fig.update_layout(
    showlegend=False,
   # title="Plot Title",
    xaxis_title="Tank Temperatures (F)",
    yaxis_title="Fraction of Tank Above/Below Fill Line",
)               
fig.write_html("ScatterPlotWith_"+vfill+".html")
