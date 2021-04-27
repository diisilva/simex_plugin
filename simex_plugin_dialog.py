# -*- coding: utf-8 -*-
"""
/***************************************************************************
 simex_pluginDialog
                                 A QGIS plugin
 O Plugin SIMEX é uma ferramenta que utiliza imagens de satélite (Landsat e Sentinel 2) integrada à base de dados geoespaciais para o monitoramento de áreas de atividade madeireira. As informações extraídas das imagens contribuem no licenciamento e monitoramento de Planos de Manejo Florestal, além de facilitar na identificação de áreas de exploração não autorizadas. 
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-04-19
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Diego SIlva - Consultor SIG 
        email                : dii.manut@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'simex_plugin_dialog_base.ui'))


class simex_pluginDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(simex_pluginDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)