# -*- coding: utf-8 -*-
'''Elipse Plant Manager - EPM Dataset Analysis Plugin - Plugin sample
Copyright (C) 2015 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
'''

# Numpy, Scipy and Matplotlib modules
import numpy as np
import scipy.optimize as optimize
from scipy import interpolate
from scipy import integrate
import matplotlib.pyplot as plt


def removeOutliers(epmSpeed, epmPower, minSpeed, nominalPower):
    """ Removes outliers from data.
    >>> speed, power = removeOutliers(epmSpeed, epmPower, 4.0, 3000.0)
    >>> plt.scatter(speed, power)
    >>> plt.show()
    """
    
    speedData = epmSpeed['Value'].copy()
    powerData = epmPower['Value'].copy()
    pPos = np.argwhere(powerData < 0.)
    speed = np.delete(speedData,pPos)
    power = np.delete(powerData,pPos)
    pPos = np.argwhere(powerData > nominalPower)
    speed = np.delete(speed,pPos)
    power = np.delete(power,pPos)
    pPos = np.argwhere(speed < minSpeed)
    speed = np.delete(speed,pPos)
    power = np.delete(power,pPos)
    return speed, power


def windPowerAverage(speed, power):
    """ Calculates the power average for each speed value.
    >>> speedAvg, powerAvg = windPowerAverage(speed, power)
    >>> plt.scatter(speed, power, c='b')
    >>> plt.scatter(speedAvg, powerAvg, c='r', alpha=0.5)
    >>> plt.show()
    """

    pos = np.argsort(speed)
    x = speed[pos].copy()
    y = power[pos].copy()
    xm = []
    ym = []
    i = 0
    while i < (len(x)):
        p = np.where(x == x[i])
        xm.append(x[p].mean())
        ym.append(y[p].mean())
        i = p[0][-1] + 1
    return np.array(xm), np.array(ym)


def bestFitSpeedPower(speedAvg, powerAvg, binSpeed = 0.5):
    """ Returns the best fit curve based on powerFit function.
    >>> speedEst, powerEst = bestFitSpeedPower(speedAvg, powerAvg)
    >>> plt.plot(speedEst, powerEst, 'g', linewidth=3)
    >>> plt.show()
    """

    par0 = [1500.0, 1.0, 1.0, 1.0]
    old_settings = np.seterr(all='ignore')
    parest,cov,infodict,mesg,ier = optimize.leastsq(residualsSP, par0, args=(speedAvg, powerAvg), full_output=True)
    speedEst = np.arange(speedAvg.min(), speedAvg.max(), binSpeed)
    powerEst = powerFit(parest, speedEst)
    return speedEst, powerEst


def powerFit(par, x):
    """ Theoretical Speed x Power curve
        power = par[0] / (par[1] + exp-(par[2] * speed + par[3]))
    Used by bestFitSpeedPower and residualsSP.
    """

    return par[0] / (par[1] + np.exp(-(par[2] * x + par[3])))


def residualsSP(par, x, y):
    """ Calculates the residuals based on experimental data.
    Used by bestFitSpeedPower.
    """

    return powerFit(par, x) - y


def readFromCsv(fileName=r'c:\Temp\refdata.csv', delimiter=';'):
    """ Reads raw data from a CSV file and returns two numpy arrays.
    >>> speedRaw, powerRaw = readFromCsv(fileName=r'c:\Temp\refdata.csv', delimiter=';')
    >>> plt.scatter(speedRaw, powerRaw, c='b')
    >>> plt.show()
    """

    rawData = np.genfromtxt(fileName, delimiter = delimiter)
    return rawData[:,0], rawData[:,1]


def genRefCurve(speedRaw, powerRaw, binSpeed = 0.5):
    """ Interpolates raw data using splines.
    >>> speedRef, powerRef = genRefCurve(speedRaw, powerRaw, binSpeed = 0.5)
    >>> plt.scatter(speedRaw, powerRaw, c='b')
    >>> plt.scatter(speedRef, powerRef, c='r', alpha=0.5)
    >>> plt.show()
    """

    tckRef = interpolate.splrep(speedRaw, powerRaw, s=0)
    speedRef = np.arange(speedRaw.min(), speedRaw.max(), binSpeed)
    powerRef = interpolate.splev(speedRef, tckRef, der=0)
    return speedRef, powerRef


def energyLost(refData, expData, binSpeed = 0.5):
    """ Returns the difference between two given curves.
    >>> lost = aero.energyLost(powerRef, powerEst, binSpeed = 0.5)
    """

    return integrate.simps(refData, dx=binSpeed) - integrate.simps(expData, dx=binSpeed)


def showResults(refData, estData, expData, lost):
    """ Show the final results.
    >>> refData = (speedRef, powerRef)
    >>> estData = (speedEst, powerEst)
    >>> expData = (speed, power)
    >>> showResults(refData, estData, expData, lost)
    """

    plt.plot(refData[0], refData[1], color='r', linewidth=3)
    plt.plot(estData[0], estData[1], color='g', linewidth=3)
    plt.scatter(expData[0], expData[1], c='b')
    plt.text(15, 1000, 'Lost: ' + str(round(lost/1000,2)) + '(MW)', fontsize=16)
    plt.xlabel(r'$Speed (m/s)$')
    plt.ylabel(r'$Power (KW)$')
    plt.show()
