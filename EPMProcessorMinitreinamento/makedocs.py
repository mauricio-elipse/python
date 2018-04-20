# -*- coding: utf-8 -*-
"""Elipse Plant Manager - EPM Processor - Basic functions
Copyright (C) 2017 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
"""

__author__ = u"Maurício"
__copyright__ = "Copyright 2018, Elipse Software"
__credits__ = [u"Renan", u"Lucas"]
__license__ = "MIT"
__version__ = "0.0.7"
__maintainer__ = u"Maurício"
__email__ = "mauricio@elipse.com.br"
__status__ = "Production"

import shutil
import subprocess

_NGINXPATH = r'C:\nginx\html\epmprocessorminitreinamento'
_SPHINXPATH = r'c:\Anaconda3\Scripts'
_DOCSSOURCE = r'F:\GDrive\Projects\EPMProcessorMinitreinamento\doc\source'
_DOCSBUILD = r'F:\GDrive\Projects\EPMProcessorMinitreinamento\doc\build'


def move2nginx():
    #Primeiro é preciso remover todo o diretóroi para colocar o conteúdo novo
    shutil.rmtree(_NGINXPATH, ignore_errors=True, onerror=None)
    shutil.copytree(_DOCSBUILD, _NGINXPATH, symlinks=False, ignore=None, copy_function=shutil.copy2,
                    ignore_dangling_symlinks=False)

if __name__ == '__main__':
    print('Gerando documentação...')
    commandStr = _SPHINXPATH + r'\sphinx-build -b html ' + _DOCSSOURCE + ' ' + _DOCSBUILD
    subprocess.run(commandStr, shell=True, check=True)
    print('Iniciando copia...')
    move2nginx()
    print('Arquivos de documentação já disponíveis no servidor!')
