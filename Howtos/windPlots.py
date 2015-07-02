# -*- coding: utf-8 -*-
'''Elipse Plant Manager - EPM Dataset Analysis - wind plots examples

Copyright (C) 2015 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
'''

# Numpy, Scipy and Matplotlib modules
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt


def windDirectionPieChart(epmWindDirection):
    '''Plots a wind directions pie chart.

    >>> windDirectionPieChart(epmWindDirection)
    
    '''
    nodesPercents, nodesLabels = percentTimeIn(epmWindDirection)
    colors = ['blue','yellowgreen', 'cyan', 'gold', 'lightskyblue', 'magenta', 'green', 'lightcoral']
    plt.pie(nodesPercents[:,1], labels=nodesLabels, colors=colors,autopct='%1.1f%%', shadow=False, startangle=90)
    plt.axis('equal')
    plt.show()


def polarScatterWindDirection(epmWindDirection, epmWindSpeed):
    '''Plots a polar scatter with the wind speed and direction.

    >>> polarScatterWindDirection(epmWindDirection, epmWindSpeed)
    
    '''
    ax1 = plt.subplot(111, polar=True)
    ax1.set_theta_zero_location('N')
    ax1.set_theta_direction(-1)
    ax1.grid(True)
    ax1.xaxis.set_ticklabels(['N',r"$45^{o}$",'E',r"$135^{o}$",'S',r"$225^{o}$",'W', r"$315^{o}$"])
    ax1.set_title("Wind direction", va='bottom')
    ax1.plot(epmWindDirection['Value'], epmWindSpeed['Value'], 'bo')
    plt.show()

##################################################################################################
# Auxiliary Functions
##################################################################################################

def percentTimeIn(epmData):
    '''Returns the percentual duration in each wind direction.

    >>>nodesPercents, nodesLabels = percentTimeIn(epmData)

    '''
    t,y = rmNanAndOutliers(epmData)
    minVal = 0
    maxVal = 360
    step = int((maxVal-minVal)/8)
    nodes = range(minVal,maxVal,step)
    intervNum = np.size(nodes)+1
    totTime = np.empty(intervNum, dtype=object)
    totTime.fill(dt.timedelta(0,0))
    for i in range(1,np.size(y)):
        deltaT = t[i] - t[i-1]
        ix = np.digitize([y[i]], nodes)
        totTime[ix] += deltaT
    nodesPercents = np.zeros([np.size(totTime),2])
    totalPeriod = totTime.sum().total_seconds()
    for i in range(np.size(totTime)):
        if i:
           nodesPercents[i,0] = nodes[i-1]
        else:
           nodesPercents[i,0] = -np.inf
        nodesPercents[i,1] = totTime[i].total_seconds()/totalPeriod
    nodesLabels = []
    for item in nodesPercents[:,0]:
        nodesLabels.append(angle2cardinal(item))
    return nodesPercents, nodesLabels

def rmNanAndOutliers(epmData, sd = 6):
    '''Removes missing data and outliers.

    >>>t,y = rmNanAndOutliers(epmData)

    '''
    y = epmData['Value']
    t = epmData['Timestamp']
    nanPos = np.argwhere(np.isnan(y))
    y = np.delete(y,nanPos)
    t = np.delete(t,nanPos)
    s3 = np.floor(sd * np.sqrt(y.std()))
    smin = y.mean() - s3
    smax = y.mean() + s3
    outPos = np.argwhere(y<smin)
    y = np.delete(y,outPos)
    t = np.delete(t,outPos)
    outPos = np.argwhere(y>smax)
    y = np.delete(y,outPos)
    t = np.delete(t,outPos)
    return t,y

def angle2cardinal(degAngle):
    '''Converts degrees to cardinal directions.

    >>>cardinalDirStr = angle2cardinal(degAngle)

    '''
    cardList = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    degBaseList = range(0, 360, 360/8)
    degBand = 360/16.
    dir = 0
    if degAngle> degBaseList[1]-degBand and degAngle<= degBaseList[2]-degBand:
        dir = 1
    elif degAngle> degBaseList[2]-degBand and degAngle<= degBaseList[3]-degBand:
        dir = 2
    elif degAngle> degBaseList[3]-degBand and degAngle<= degBaseList[4]-degBand:
        dir = 3
    elif degAngle> degBaseList[4]-degBand and degAngle<= degBaseList[5]-degBand:
        dir = 4
    elif degAngle> degBaseList[5]-degBand and degAngle<= degBaseList[6]-degBand:
        dir = 5
    elif degAngle> degBaseList[6]-degBand and degAngle<= degBaseList[7]-degBand:
        dir = 6
    elif degAngle> degBaseList[7]-degBand and degAngle<= 360-degBand:
        dir = 7
    return cardList[dir]
