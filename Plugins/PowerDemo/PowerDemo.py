# -*- coding: utf-8 -*-
'''Elipse Plant Manager - EPM Dataset Analysis Plugin - Plugin sample
Copyright (C) 2016 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
'''

# EPM Plugin modules
import Plugins as ep

# Numpy, Matplotlib, etc. modules
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
from matplotlib.colors import colorConverter
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import datetime as dt


@ep.DatasetFunctionPlugin('Power Surface', 2)
def thirtyDaysProfilePlugin():
    """
    Gera uma superfície para avaliar a variação diária e ao longo do mês (30 dias).
    Dados devem corresponder a uma consulta com 30 dias e serem interpolados (ProcessingInterval < 1h).
    """
    if len(ep.EpmDatasetPens.SelectedPens) != 1:
        ep.showMsgBox('EPM Python Plugin - Demo Power', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    epmData = ep.EpmDatasetPens.SelectedPens[0].Values
    sampling = 30
    pHours = 24
    iniPeriod = epmData['Timestamp'][0]
    endPeriod = epmData['Timestamp'][-1]
    dTotal = endPeriod - iniPeriod
    totDays = dTotal.days
    evalPeriod = dt.timedelta(hours = pHours)
    nextPeriod = iniPeriod + evalPeriod
    profileList = []
    for i in range(totDays+1):
        iniP = epmData['Timestamp'] >= iniPeriod
        endP = epmData['Timestamp'] < nextPeriod
        epmDataValue = epmData['Value']
        dataPeriod = epmDataValue[iniP * endP]
        profileList.append( dataPeriod )
        iniPeriod = iniPeriod + dt.timedelta( 1 )
        nextPeriod = iniPeriod + evalPeriod
    profileMatrix = np.array(profileList)
    days  = np.arange(totDays)+1
    hours = np.arange(0,pHours*60,sampling)
    meshTime, indices = np.meshgrid(hours, days)
    meshProfile = np.zeros(meshTime.shape)
    for i in range( indices.shape[0] ):
        for j in range( indices.shape[1] ):
            meshProfile[i,j] = profileMatrix[i,j]
    fig = plt.figure(figsize=(15, 8))
    ax = fig.gca(projection='3d')
    X = meshTime
    Y = indices
    Z = meshProfile
    ax.plot_surface(X/60., Y, Z, rstride=1, cstride=1, cmap='coolwarm', alpha=0.8)
    ax.set_xlabel('hour')
    ax.set_ylabel('day')
    ax.set_zlabel('Power')
    plt.show()

@ep.DatasetFunctionPlugin('Power Avg. Profile', 4)
def fiveDaysProfilePlugin():
    """
    Gráfico de área do perfil diário médio da variável a partir de dados de 5 dias.
    Dados devem corresponder a uma consulta de 5 dias (úteis) com valores médios a cada hora.
    """
    if len(ep.EpmDatasetPens.SelectedPens) != 1:
        ep.showMsgBox('EPM Python Plugin - Demo Power', 'Please select a single pen before applying this function!', 'Warning')
        return 0
    def cc(arg): return colorConverter.to_rgba(arg, alpha=0.6)
    epmDataValue = ep.EpmDatasetPens.SelectedPens[0].Values['Value']
    epmAvg = np.vstack((epmDataValue[0:24], epmDataValue[24:2*24], epmDataValue[2*24:3*24], epmDataValue[3*24:4*24], epmDataValue[4*24:5*24]))
    epmAvg = epmAvg.mean(axis=0)
    epmAvg[0], epmAvg[-1] = 0,0
    ys = np.arange(1, 25)
    zs = [0., 1., 2., 3., 4., 5.]
    profileList = []
    profileList.append( list(zip(ys, epmAvg)))
    ini = 0
    end = 24
    for i in range(5):
        dataPeriod = epmDataValue[ini:end]
        dataPeriod[0], dataPeriod[-1] = 0,0
        profileList.append( list(zip(ys, dataPeriod)))
        ini += 24
        end += 24
    poly = PolyCollection(profileList, facecolors=[cc('k'), cc('r'), cc('g'), cc('b'), cc('y'), cc('c')])
    fig = plt.figure(figsize=(15, 8))
    ax = fig.gca(projection='3d')
    poly.set_alpha(0.7)
    ax.add_collection3d(poly, zs=zs, zdir='y')
    ax.set_xlabel('hour')
    ax.set_xlim3d(1, 24)
    ax.set_ylabel('day')
    ax.set_ylim3d(-1, 6)
    ax.set_zlabel('power')
    ax.set_zlim3d(epmDataValue.min(), epmDataValue.max())
    plt.show()


@ep.DatasetFunctionPlugin('Scatter 3 variables', 6)
def xyzScatter3DPlugin():
    """
    Apresenta gráficos de dispersão comparando 3 variáves entre si duas a duas e as 3 simultaneamente.
    Os dados das 3 variáveis devem estar igualmente espaçados.
    """
    if len(ep.EpmDatasetPens.SelectedPens) != 3:
        ep.showMsgBox('EPM Python Plugin - Demo Power', 'Please select 3 pens before applying this function!', 'Warning')
        return 0

    epmDataX = ep.EpmDatasetPens.SelectedPens[0].Values['Value']
    Xlabel = ep.EpmDatasetPens.SelectedPens[0].Name
    epmDataY = ep.EpmDatasetPens.SelectedPens[1].Values['Value']
    Ylabel = ep.EpmDatasetPens.SelectedPens[1].Name
    epmDataZ  = ep.EpmDatasetPens.SelectedPens[2].Values['Value']
    Zlabel = ep.EpmDatasetPens.SelectedPens[2].Name
    fig = plt.figure(figsize=(15, 8))
    ax1 = plt.subplot2grid((3, 3), (0, 0))
    ax2 = plt.subplot2grid((3, 3), (0, 1))
    ax3 = plt.subplot2grid((3, 3), (0, 2))
    ax4 = plt.subplot2grid((3, 3), (1, 0), colspan=3, rowspan=3,  projection='3d')
    x = (epmDataX-epmDataX.mean())/epmDataX.std()
    y = (epmDataY-epmDataY.mean())/epmDataY.std()
    z = (epmDataZ-epmDataZ.mean())/epmDataZ.std()
    ax1.scatter(x, y)
    ax1.set_xlabel(Xlabel, fontsize=10)
    ax1.set_ylabel(Ylabel, fontsize=10)
    ax2.scatter(x, z)
    ax2.set_xlabel(Xlabel, fontsize=10)
    ax2.set_ylabel(Zlabel, fontsize=10)
    ax3.scatter(y, z)
    ax3.set_xlabel(Ylabel, fontsize=10)
    ax3.set_ylabel(Zlabel, fontsize=10)
    #ax4.scatter(x, y, z, cmap='hot')
    ax4.scatter(x, y, z)
    ax4.set_xlabel(Xlabel, fontsize=10)
    ax4.set_ylabel(Ylabel, fontsize=10)
    ax4.set_zlabel(Zlabel, fontsize=10)
    plt.tight_layout(pad=0.5, w_pad=0.5, h_pad=1.0)
    plt.show()
