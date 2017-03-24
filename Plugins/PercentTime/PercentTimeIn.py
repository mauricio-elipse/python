# -*- coding: utf-8 -*-
'''Elipse Plant Manager - EPM Dataset Analysis Plugin - Plugin example

Copyright (C) 2015 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
'''

# EPM Plugin modules
import EpmDatasetPlugins as ds
import ScriptRunner as sr
# Numpy, Scypy and Matplotlib modules
import numpy as np
import scipy.stats as st
from scipy.signal import butter
from scipy.signal import lfilter
from scipy import integrate
import matplotlib.pylab as pl
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from matplotlib.widgets import SpanSelector
from matplotlib.widgets import RectangleSelector
from mpl_toolkits.axes_grid1 import make_axes_locatable
import datetime as dtt

# Dialog Tkinter
from Tkinter import *

# Variaveis globais
nodes = -1

@ds.epm_dataset_method_plugin('Percent time in...', 1, 'nodesPercents')
def percentTimeIn():
    """ Funcao que retorna o percentual de tempo em cada intervalo informado.
    """
    if len(ds.EpmDatasetAnalysisPens.SelectedPens) != 1:
        sr.msgBox('EPM Python Plugin - Demo Tools', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ds.EpmDatasetAnalysisPens.SelectedPens[0].values
    global nodes
    runDialogInterval()
    global nodes
    t,y = rmNanAndOutliers2(epmData)
    if len(nodes) < 2:
       minVal = int(np.floor(np.nanmin(y)))
       maxVal = int(np.ceil(np.nanmax(y)))
       step = int((maxVal-minVal)/3)
       nodes = range(minVal,maxVal,step)
    intervNum = np.size(nodes)+1
    totTime = np.empty(intervNum, dtype=object)
    totTime.fill(dtt.timedelta(0,0))
    for i in range(1,np.size(y)):
        dt = t[i] - t[i-1]
        ix = np.digitize([y[i]], nodes)
        totTime[ix] += dt
    nodesPercents = np.zeros([np.size(totTime),2])
    totalPeriod = totTime.sum().total_seconds()
    for i in range(np.size(totTime)):
        if i:
           nodesPercents[i,0] = nodes[i-1]
        else:
           nodesPercents[i,0] = -np.inf
        nodesPercents[i,1] = totTime[i].total_seconds()/totalPeriod
    labels = []
    for item in nodesPercents[:,0]:
        labels.append(str(item))
    pl.pie(nodesPercents[:,1], labels=labels, autopct='%1.1f%%', shadow=True)
    pl.show()
    return nodesPercents

def runDialogInterval():
    raiz = Tk()
    interface = DialogGetInterval(raiz)
    raiz.mainloop()

class DialogGetInterval():

    def __init__(self,raiz):
        self.raiz = raiz
        self.makeScreen()
        self.raiz.title('Elipse Plant Manager - Get Interval')

    def makeScreen(self):
        margin = LabelFrame(self.raiz, bd=0, padx=5,pady=5)
        margin.grid()
        fora = LabelFrame(margin, bd=2, padx=5,pady=5)
        fora.grid()
        self.nodesVector = StringVar()
        cabecalho = LabelFrame(fora, text="User information", bd=2)
        cabecalho.grid(sticky=E+W)
        Label(cabecalho,text='Intervalo ex.: 0  20  50  100').grid(sticky=E)
        self.nodeVecEdit = Entry(cabecalho, width=50, textvariable=self.nodesVector).grid(row=0, column=1, sticky=W)
        self.nodesVector.set(str(nodes))
        frame_botoes = LabelFrame(fora, bd=0)
        frame_botoes.grid(sticky=E)
        Button(frame_botoes, text='OK',width=10,command=self.Action_OK).grid(row=21,column=0,sticky=W,padx=10, pady=8)
        Button(frame_botoes, text='Cancelar',width=10,command=self.Action_Cancel).grid(row=21,column=1,sticky=E,padx=10, pady=8)

    def Action_OK(self):
        global nodes
        tmpStr = self.nodesVector.get()
        nodes = [float(s) for s in tmpStr.split() if s.isdigit()]
        if len(nodes)<1:
            nodes= - 1
        print 'Intervalo carregado'
        self.raiz.destroy()

    def Action_Cancel(self):
        global nodes
        nodes = 0
        self.raiz.destroy()

def rmNanAndOutliers2(epmData, sd = 6):
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