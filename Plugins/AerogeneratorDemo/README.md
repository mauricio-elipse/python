# EPM Dataset Analysis - Python Plugin
Exemplo Plugins no EPM Dataset Analysis - versão 3.

Exemplo utilizado para exemplificar a utilização dos módulos numpy e scipy:

[Scipy: optimize, interpolate and integrate - Aerogenerator Example](https://www.youtube.com/watch?v=GyT8-38ItBc)

Para migrar códigos de Plugins Python do EPM Studio versão 2.x para a 3.x, as seguintes alterações devem ser feitas:

**Substituir**

``
import EpmDatasetPlugins as ds
``

``
import ScriptRunner as sr
``

por

``
import Plugins as ep
``

---
``
@ds.epm_dataset_method_plugin
``

por

``
@ep.DatasetFunctionPlugin
``

---
``
sr.msgBox
``

por

``
ep.showMsgBox
``

---
``
ds.EpmDatasetAnalysisPens
``

por

``
ep.EpmDatasetPens
``

---
``
sr.plot
``

por

``
ep.plotValues
``

---
``
.values
``

por

``
.Values
``

---
``
.name
``

por

``
.Name
``
