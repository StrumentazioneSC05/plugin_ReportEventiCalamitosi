# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EsportaAtlanteHailDialog
                                 A QGIS plugin
 EsportaAtlanteHail
                             -------------------
        begin                : 2016-10-17
        git sha              : $Format:%H$
        copyright            : (C) 2016 by ar_gaeta@yahoo.it
        email                : ar_gaeta@yahoo.it
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

#recupero la versione di QGis dell'utente:
global qgis_version
try:
    from qgis.core import Qgis #versione qgis 3.x
except ImportError:
    from qgis.core import QGis as Qgis #versione qgis 2.x
qgis_version = Qgis.QGIS_VERSION

if (int(qgis_version[0]) < 3):
    from PyQt4 import QtGui, uic
    qgs_dialog = QtGui.QDialog
else:
    from qgis.PyQt.QtWidgets import QFileDialog, QInputDialog, QDialog, QLineEdit
    qgs_dialog = QDialog

from qgis.PyQt import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'EsportaAtlanteHail_dialog_base.ui'))


class EsportaAtlanteHailDialog(qgs_dialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(EsportaAtlanteHailDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
