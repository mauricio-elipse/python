.. mspEProcssBasicUCsPrj documentation master file, created by
   sphinx-quickstart on Tue Oct 24 11:40:57 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
   http://www.sphinx-doc.org/pt_BR/stable/tutorial.html
   reStructuredText directives
   toctree é uma diretiva reStructuredText directive, peça muito versátil de marcação. Diretivas podem conter
   argumentos, opções e conteúdos.
   Argumentos são fornecidos diretamente após duplo dois pontos seguidos do nome da diretiva. Cada diretiva decide
   se existem e quantos são os argumentos.
   Opções são fornecidas após os argumentos, na forma de “lista de campos”. Como em maxdepth que é uma opção
   da diretiva toctree.
   Conteúdo segue opções ou argumentos após uma linha em branco. Cada diretiva decide como permite conteúdo
   e como tratá-lo. Um pegadinha comum com diretivas é que a primeira linha do conteúdo precisa estar
   alinhada (com espaços) ao mesmo nível das opções
   Ex.:
   .. directivename:: argument ...
   :option: value
   [ISSO_É_UMA_LINHA_EM_BRANCO]
   Content of the directive.

Documentação do módulo mspEProcssBasicUCs - Casos de Usos básicos do EPM Processor
===================================================================================

Este módulo é utilizado para testar e validar diversos casos de uso do EPM Processor. Ele não deve ser utilizado para
casos de aplicações reais, servindo apenas como referência das possibilidades que o EPM Processor oferece.

**Requisitos**

Os seguintes módulos Python são encessários para utilização de todos os recursos deste módulo:
datetime, pytz, json, numpy, sklearn, matplotlib, selenium, epmprocessor, epmprocessor.


`Elipse Software - EPM <https://www.elipse.com.br/en/produto/elipse-plant-manager/>`_

Canal da Elipse Software no Youtube: `Playlist EPM`_.

.. _Playlist EPM: https://www.youtube.com/watch?v=TSiWcU43rGU&list=PLoCAWpTf0fzUv_b1DThm1pRmdYO0WaEpn

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   code
   glossary




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. centered:: *"A arte da vida consiste em fazer da vida uma obra de arte."*
.. centered:: --  `Mahatma Gandhi <https://pt.wikipedia.org/wiki/Mahatma_Gandhi>`_ --
