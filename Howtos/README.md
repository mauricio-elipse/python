How to's...
=======

#Exemplos de gr�ficos polares

Aplicando as fun��es do arquivo windPlots a s�ries temporais de dire��o do vento e sua velocidade.
Polar Scatter Wind Direction
![polarScatterWindDirection](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/polarScatterWindDirection.PNG)
Wind Direction Pie Chart
![windDirectionPieChart](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/windDirectionPieChart.PNG)


#Exemplos de Interpola��o, ajuste de curvas e c�lculo de �reas

Exemplo pr�tico de utiliza��o de diversas fun��es do scipy: interpola��o, ajuste de curvas e c�lculos de �reas (integra��o).
Neste exemplo s�o comparadas as curvas da velocidade do vento com a corrspondente pot�ncia gerada por um aerogerador e calculada a �rea entre elas.
A curva de refer�ncia � obtida a partir de dados em um arquivo .CSV, enquanto a outra � determinada a partir de dados medidos.
As fun��es foram implementadas para fins did�ticos, exemplificando  passo a passo este caso pr�tico. A fun��o showResults apresenta os resultados ao final.
![windDirectionPieChart](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/aerogeneratorSpeedPower.png)
A sequ�ncia de execu��o sugerida � a seguinte:
>>> import AerogeneratorSample as aero
>>> minSpeed = 4.0
>>> nominalPower = 3000.0
>>> speed, power = aero.removeOutliers(WindSpeedAvg, PowerAvg, minSpeed, nominalPower) # WindSpeedAvg e PowerAvg s�o as medidas de campo
>>> plt.scatter(speed, power, c='b')
>>> plt.show()
>>> speedAvg, powerAvg = aero.windPowerAverage(speed, power)
>>> plt.scatter(speed, power, c='b')
>>> plt.scatter(speedAvg, powerAvg, c='r', alpha=0.5)
>>> plt.show()
>>> speedEst, powerEst = aero.bestFitSpeedPower(speedAvg, powerAvg)
>>> plt.scatter(speedAvg, powerAvg, c='r')
>>> plt.plot(speedEst, powerEst, 'g', linewidth=3)
>>> plt.show()
>>> speedRaw, powerRaw = aero.readFromCsv(fileName='refdata.csv', delimiter=';')  # O arquivo .csv est� em: misc/refdata.csv
>>> speedRef, powerRef = aero.genRefCurve(speedRaw, powerRaw, binSpeed = 0.5)
>>> plt.scatter(speedRaw, powerRaw, c='b')
>>> plt.scatter(speedRef, powerRef, c='r', alpha=0.5)
>>> plt.show()
>>> lost = aero.energyLost(powerRef, powerEst, binSpeed = 0.5)
>>> refData = (speedRef, powerRef)
>>> stData = (speedEst, powerEst)
>>> xpData = (speed, power)
>>> aero.showResults(refData, estData, expData, lost)
