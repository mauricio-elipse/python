# -*- coding: utf-8 -*-
'''Elipse Plant Manager - EPM Dataset Analysis Plugin - Plugin sample

Copyright (C) 2007-2015 Elipse Software. All rights reserverd.
'''

# EPM Plugin modules
import EpmDatasetPlugins as ds
import ScriptRunner as sr

# Numpy, Scipy and Matplotlib modules
import numpy as np
from scipy import integrate
import matplotlib.pylab as pl
import matplotlib as mpl
from matplotlib.widgets import Cursor
from matplotlib.widgets import SpanSelector
from matplotlib.widgets import RectangleSelector
from mpl_toolkits.axes_grid1 import make_axes_locatable


@ds.epm_dataset_method_plugin('Remove NAN and Outliers', 1, 'res')
def rmNanAndOutliers():
    """Plot without NAN and outliers from selected pen.
    """
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) < 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    sd = 6
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
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
    res = vec2epm(t,y)
    penName = ds.EpmDatasetAnalysisPens.SelectedPens[0].name + '_NoOutliers'
    sr.plot(penName, res)
    return res

@ds.epm_dataset_method_plugin('Delta', 2, 'deltaCurves')
def deltaVector():
    """ Plot deltas from selected pen.
    """
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    delta = epmData['Value'][1:] - epmData['Value'][:-1]
    deltaCurves = epmData.copy();
    deltaCurves['Value'][0] = 0
    deltaCurves['Value'][1:] = delta
    penName = ds.EpmDatasetAnalysisPens.SelectedPens[0].name + '_Delta'
    sr.plot(penName, deltaCurves)
    return deltaCurves

@ds.epm_dataset_method_plugin('Remove Mean', 3, 'rmm')
def removeMean():
    """ Plot removed mean data from selected pen.
    """
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    rmMean = epmData.copy();
    rmMean['Value'] = epmData['Value'] - epmData['Value'].mean()
    penName = ds.EpmDatasetAnalysisPens.SelectedPens[0].name + '_ZeroMean'
    sr.plot(penName, rmMean)
    return rmMean

@ds.epm_dataset_method_plugin('Normalize Curve', 4, 'nc')
def normalizeData():
    """ Plot normalized data from selected pen.
    """
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    nc = epmData.copy();
    nc['Value'] = (epmData['Value'] - epmData['Value'].mean())/epmData['Value'].std()
    penName = ds.EpmDatasetAnalysisPens.SelectedPens[0].name + '_Normalized'
    sr.plot(penName, nc)
    return nc

@ds.epm_dataset_method_plugin('Stats Infos', 5, 'nc')
def statsInfos():
    """ Show basic statistics from selected pen.
    """
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    v = epmData['Value']
    vmean = v.mean()
    vstd = v.std()
    statMsg = 'Mean: ' + '%.2f' % (vmean) + '\nStdDev: ' + '%.2f' % (vstd)
    sr.msgBox('EPM PyPlugin!', statMsg, 'Information')
    return (vmean, vstd)


@ds.epm_dataset_method_plugin('Count Changes', 6, 'nc')
def invCountEPMData():
    """ Show count direction changes from selected pen.
    """
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    n = invCount(epmData['Value'])
    msg = 'Number of changes: ' + '%.0f' % (n)
    sr.msgBox('EPM PyPlugin!', msg, 'Information')


@ds.epm_dataset_method_plugin('Integrate Curve', 7, 'curveArea')
def integralData():
    """ Show area from selected pen.
    """
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    v = epmData['Value']
    curveArea = integrate.simps(v)
    statMsg = 'Integral: ' + '%.2f' % (curveArea)
    sr.msgBox('EPM PyPlugin!', statMsg, 'Information')
    return curveArea

@ds.epm_dataset_method_plugin('Plot XY', 8)
def plotXY():
    """ Plot XY from selected pens.
    """
    import ScriptRunner as sr
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 2:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select two interpolated pens before applying this function!', 'Warning')
        return 0
    epmData1 = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    epmData2 = ds.EpmDatasetAnalysisPens.SelectedPens[1].values
    pl.figure
    pl.plot(epmData1['Value'], epmData2['Value'])
    pl.show()

@ds.epm_dataset_method_plugin('Plot Min-Max', 9, 'minmax')
def plotMinMax():
    """ Plot Min-Max lines from selected pen.
    """
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    minValue = epmData['Value'].min();
    maxValue = epmData['Value'].max();
    vmin = epmData.copy()
    vmax = epmData.copy()
    vmin['Value'][:] = minValue
    vmax['Value'][:] = maxValue
    penMin = ds.EpmDatasetAnalysisPens.SelectedPens[0].name + '_Min'
    penMax = ds.EpmDatasetAnalysisPens.SelectedPens[0].name + '_Max'
    sr.plot(penMin, vmin)
    sr.plot(penMax, vmax)
    return (minValue, maxValue)
    
@ds.epm_dataset_method_plugin('Get Points', 10, 'selPoints')
def plotGetPoints():
    """ Get data points from selected pen.
    """
    selPoints = []
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    y = epmData['Value'].copy()
    x = np.arange(len(y))
    fig = pl.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, axisbg='#FFFFFF')
    ax.plot(x, y, '-o')
    def onclick(event):
        selPoints.append((event.xdata, event.ydata))
    cursor = Cursor(ax, useblit=True, color='red', linewidth=1 )
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    pl.show()
    return selPoints

@ds.epm_dataset_method_plugin('Get Data', 11, 'selData')
def plotGetSelection():
    """ Get data range from selected pen.
    """
    selData = []
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    y = epmData['Value'].copy()
    x = np.arange(len(y))
    fig = pl.figure(figsize=(8,6))
    ax = fig.add_subplot(211, axisbg='#FFFFCC')
    ax.plot(x, y, '-')
    ax.set_title('Press left mouse button and drag to test')
    ax2 = fig.add_subplot(212, axisbg='#FFFFCC')
    line2, = ax2.plot(x, y, '-')

    def onselect(xmin, xmax):
        selData.append([xmin, xmax])
        indmin, indmax = np.searchsorted(x, (xmin, xmax))
        indmax = min(len(x)-1, indmax)
        thisx = x[indmin:indmax]
        thisy = y[indmin:indmax]
        line2.set_data(thisx, thisy)
        ax2.set_xlim(thisx[0], thisx[-1])
        ax2.set_ylim(thisy.min(), thisy.max())
        fig.canvas.draw()

    span = SpanSelector(ax, onselect, 'horizontal', useblit=True, rectprops=dict(alpha=0.5, facecolor='red') )
    pl.show()
    return selData

@ds.epm_dataset_method_plugin('Get Retangle', 12, 'selRect')
def plotGetRetangle():
    """ Area selection from selected pen.
    """
    selRect = []
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    y = epmData['Value'].copy()
    x = np.arange(len(y))
    fig, current_ax = pl.subplots()
    pl.plot(x, y, lw=2, c='g', alpha=.3)

    def line_select_callback(eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        print ("\n(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
        selRect.append((int(x1), y1, int(x2), y2))

    def toggle_selector(event):
        if event.key in ['Q', 'q'] and toggle_selector.RS.active:
            toggle_selector.RS.set_active(False)
        if event.key in ['A', 'a'] and not toggle_selector.RS.active:
            toggle_selector.RS.set_active(True)
    toggle_selector.RS = RectangleSelector(current_ax, line_select_callback, drawtype='box', useblit=True, button=[1,3], minspanx=5, minspany=5, spancoords='pixels')
    pl.connect('key_press_event', toggle_selector)
    pl.show()
    return selRect


# *** Extra functions ***
def vec2epm(t, y):
    """ Convert datetime vector and data vector into EPM array (numpy array)
    t: datetime vector
    y: double data vector
    """
    desc = np.dtype([('Value', '>f8'), ('Timestamp', 'object'), ('Quality', 'object')])
    epmY = np.empty([np.size(y)], dtype = desc)
    epmY['Value'] = y
    epmY['Timestamp'] = t
    epmY['Quality'] = 0
    return epmY

def invCount( y ):
    """ Count direction changes
    y: double data vector
    """
    d = y[1:] - y[:-1]
    n = 0
    for i in range(len(d)-1):
        if np.sign(d[i]) != np.sign(d[i+1]):
           n += 1
    return n
