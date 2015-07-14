How to's...
=======

#Exemplos de gráficos polares

Aplicando as funções do arquivo windPlots a séries temporais de direção do vento e sua velocidade.
Polar Scatter Wind Direction
![polarScatterWindDirection](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/polarScatterWindDirection.PNG)
Wind Direction Pie Chart
![windDirectionPieChart](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/windDirectionPieChart.PNG)


#Exemplos de Interpolação, ajuste de curvas e cálculo de áreas

Exemplo prático de utilização de diversas funções do scipy: interpolação, ajuste de curvas e cálculos de áreas (integração).
Neste exemplo são comparadas as curvas da velocidade do vento com a corrspondente potência gerada por um aerogerador e calculada a área entre elas.
A curva de referência é obtida a partir de dados em um arquivo .CSV, enquanto a outra é determinada a partir de dados medidos.
As funções foram implementadas para fins didáticos, exemplificando  passo a passo este caso prático. A função showResults apresenta os resultados ao final.
![windDirectionPieChart](https://github.com/mauricio-elipse/python/tree/master/Howtos/figs/aerogeneratorSpeedPower.png)
A sequência de execução sugerida é a seguinte:
<p>import AerogeneratorSample as aero</p>
<p>minSpeed = 4.0</p>
<p>nominalPower = 3000.0</p>
<p>speed, power = aero.removeOutliers(WindSpeedAvg, PowerAvg, minSpeed, nominalPower) # WindSpeedAvg e PowerAvg são as medidas de campo</p>
<p>plt.scatter(speed, power, c='b')</p>
<p>plt.show()</p>
<p>speedAvg, powerAvg = aero.windPowerAverage(speed, power)</p>
<p>plt.scatter(speed, power, c='b')</p>
<p>plt.scatter(speedAvg, powerAvg, c='r', alpha=0.5)</p>
<p>plt.show()</p>
<p>speedEst, powerEst = aero.bestFitSpeedPower(speedAvg, powerAvg)</p>
<p>plt.scatter(speedAvg, powerAvg, c='r')</p>
<p>plt.plot(speedEst, powerEst, 'g', linewidth=3)</p>
<p>plt.show()</p>
<p>speedRaw, powerRaw = aero.readFromCsv(fileName='refdata.csv', delimiter=';')  # O arquivo .csv está em: misc/refdata.csv</p>
<p>speedRef, powerRef = aero.genRefCurve(speedRaw, powerRaw, binSpeed = 0.5)</p>
<p>plt.scatter(speedRaw, powerRaw, c='b')</p>
<p>plt.scatter(speedRef, powerRef, c='r', alpha=0.5)</p>
<p>plt.show()</p>
<p>lost = aero.energyLost(powerRef, powerEst, binSpeed = 0.5)</p>
<p>refData = (speedRef, powerRef)</p>
<p>stData = (speedEst, powerEst)</p>
<p>xpData = (speed, power)</p>
<p>aero.showResults(refData, estData, expData, lost)</p>
