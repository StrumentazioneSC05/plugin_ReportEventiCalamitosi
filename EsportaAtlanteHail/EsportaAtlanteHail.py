# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EsportaAtlanteHail
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
#from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
#from PyQt4.QtGui import QAction, QIcon
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
#from qgis.utils import *

import plugin_utils as Utils

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from EsportaAtlanteHail_dialog import EsportaAtlanteHailDialog
import os.path

#importo DockWidget
from EsportaAtlanteHailDock_dockwidget import EsportaAtlanteHailDockDockWidget

class EsportaAtlanteHail:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'EsportaAtlanteHail_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = EsportaAtlanteHailDialog()
                
        #Definisco alcune variabili globali:
        global filename
        filename = None
        
        #Aggiungo DockWidget
        self.pluginIsActive = False
        self.dockwidget = None
        
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&EsportaAtlanteHail')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'EsportaAtlanteHail')
        self.toolbar.setObjectName(u'EsportaAtlanteHail')
        
        '''#Implemento alcune azioni sui miei pulsanti -- posso riportare questa parte anche nella sezione initGui e all'interno dei rispettivi "run" nel caso li voglia ridefinire
        self.dlg.pageBar.setValue(0)
        self.dlg.select_btn.clicked.connect(self.seleziona)
        self.dlg.radio_pdf.clicked.connect(self.activate_export)
        self.dlg.radio_png.clicked.connect(self.activate_export)
        self.dlg.atlas_btn.clicked.connect(self.export_atlas)
        #SALVA FILE con nome
        self.dlg.fileBrowse_txt.clear()
        self.dlg.fileBrowse_btn.clicked.connect(self.select_output_file)'''
        
        
    #--------------------------------------------------------------------------
    
    def pageProcessed(self):
        """Increment the page progressbar."""
        self.dlg.pageBar.setValue(self.dlg.pageBar.value() + 1)
        
    def export_atlas(self):
        #finalmente esporto l'Atlante secondo le opzioni specificate.
        self.get_Atlas_filter() #riaggiorno eventualmente le informazioni sull'Atlas e Composition
        global filename
        filename = self.dlg.fileBrowse_txt.text()
        #folder = r"C:\Users\riccardo\Desktop"
        title = "Atlas"
        #title = myComposition.composerWindow().windowTitle()
        #filename = os.path.join(folder, title + '.pdf')
        printer = QPrinter()
        painter = QPainter()
        radiocheck_pdf = self.dlg.radio_pdf.isChecked()
        radiocheck_png = self.dlg.radio_png.isChecked()
        self.dlg.pageBar.setValue(0)
        msg = QMessageBox()
        # Generate atlas
        try:
            # Set page progressbar maximum value possible for atlases once the rendering has begun
            if myAtlas.enabled():
                myAtlas.beginRender()
                previous_mode = myComposition.atlasMode()
                myComposition.setAtlasMode(QgsComposition.ExportAtlas)
                myAtlas.setFilenamePattern(u"'{}_'||$feature".format(title))
                all_items = myComposition.items()
                pagine = myComposition.pages()
                copertina = pagine[0]
                copertina.show()
                if (radiocheck_pdf):
                    maxpages = myAtlas.numFeatures()
                else:
                    maxpages = myAtlas.numFeatures() * myComposition.numPages()
            else:
                if (radiocheck_pdf): maxpages = 1
                else: 
                    maxpages = myComposition.numPages()
            self.dlg.pageBar.setMaximum(maxpages)
            Utils.logMessage("Numero di pagine max = " + str(maxpages))
                    
            if myAtlas.enabled():
                #PDF:
                if (radiocheck_pdf):
                    filename_path = os.path.join(filename + '.pdf')
                    myComposition.setUseAdvancedEffects(False)
                    for i in range(0, myAtlas.numFeatures()):
                        myAtlas.prepareForFeature( i )
                        Utils.logMessage("Numero di feature="+str(myAtlas.numFeatures()))
                        '''questa parte funziona stampa tutto l'Atlas
                        myComposition.beginPrintAsPDF(printer, filename_path)
                        myComposition.beginPrint(printer)
                        printReady = painter.begin(printer)
                        #Stampa TUTTO l'Atlante - ok:
                        if i > 0:
                            printer.newPage()
                        myComposition.doPrint(printer, painter)
                        '''
                        
                        #Nel mio caso specifico ho inserito una copertina: non la voglio stampare ogni volta! Ma esportando in PDF non riesco ad escluderla dalla stampa...
                        #L'unico metodo che parrebbe funzionare e' nascondere la prima pagina e tutti i suoi elementi al "secondo giro" di stampa.
                        myComposition.beginPrintAsPDF(printer, filename_path)
                        myComposition.refreshItems() #provo a fare il refresh dell'Atlas per aggiornare il WMS...inutile lo sfondo non si ridisegna
                        myComposition.beginPrint(printer)
                        printReady = painter.begin(printer)
                        if i>0:
                            #printer.newPage() #in questo caso NON creo una nuova pagina perche' voglio proprio che la copertina, svuotata, si SOVRAPPONGA alla seconda pagina
                            #copertina.setExcludeFromExports(True)
                            copertina.hide()
                            #copertina.setVisibility(False)
                            copertina.update()
                            for item in all_items:
                              #provo a fare il refresh dell'item mappa? non cambia nulla per il WMS di sfondo della regione che non riesce ad aggiornarsi
                              '''if (item.type()==65641 and item.id()==2):
                                  Utils.logMessage("faccio update")   
                                  item.updateItem()
                                  item.update()
                              '''
                              if (item.type()==3 or item.type()==65642): #escludo 65642=QgsPaperItem e 3=QGraphicsRectItem. Tutti gli altri valori sembrano essere validi
                                continue
                              else:
                                if item.page()==1:
                                  item.hide()
                            myComposition.update()
                        myComposition.refreshItems() #provo a fare il refresh dell'Atlas per aggiornare il WMS...inutile lo sfondo non si ridisegna
                        myComposition.doPrint(printer, painter)
                        
                        self.pageProcessed() #increase progressbar
                    
                    #Riabilito la copertina e gli elementi eventualmente nascosti:
                    copertina.show()
                    #copertina.setVisibility(True)
                    #copertina.setExcludeFromExports(False)
                    for item in all_items:
                        if (item.type()==3 or item.type()==65642): #escludo 65642=QgsPaperItem e 3=QGraphicsRectItem. Tutti gli altri valori sembrano essere validi
                          continue
                        else:
                          if item.page()==1:
                            item.show()
                        
                #PNG:
                elif (radiocheck_png):
                    myComposition.setUseAdvancedEffects(True)
                    for i in range(0, myAtlas.numFeatures()):
                        myAtlas.prepareForFeature( i )
                        for j in range(0, myComposition.numPages()):
                            progressivo = '_' + str(i) + str(j) + '_'
                            #Nel mio caso specifico ho inserito una copertina: non la voglio stampare ogni volta!
                            if ( i>0 and j==0):
                                continue
                            filename_path = os.path.join(filename + progressivo +'.png')
                            myImage = myComposition.printPageAsRaster(j) #(page, imageSize, dpi)
                            myImage.save(filename_path)
                            self.pageProcessed() #increase progressbar
                
                myAtlas.endRender()
                painter.end()
                myComposition.setAtlasMode(previous_mode)
            
            # if the composition has no atlas
            else:
                if (radiocheck_pdf):
                    myComposition.exportAsPDF(filename_path)
                    self.pageProcessed() #increase progressbar
                elif (radiocheck_png):
                    for j in range(0, myComposition.numPages()):
                        progressivo = '_' + str(i) + str(j) + '_'
                        filename_path = os.path.join(filename + progressivo +'.png')
                        myImage = myComposition.printPageAsRaster(j) #(page, imageSize, dpi)
                        myImage.save(filename_path)
                        self.pageProcessed() #increase progressbar

        except NameError as err:
            if myAtlas.enabled():
                myAtlas.endRender()
                painter.end()
            msg.setText(err.args[0])
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Errore!")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()
            Utils.logMessage(err.args[0])
            return 0;
        else:
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Tutto bene!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setText("Esportazione Atlante avvenuta con successo!")
            retval = msg.exec_()
    
    
    def activate_export(self):
        #Verifico che alcune condizioni siano rispettate per abilitire il pulsante di esportazione:
        #filename = self.dlg.fileBrowse_txt.text()
        Utils.logMessage("filename: " + str(filename))
        filtro_check = self.dlg.filter_atlas_txt.toPlainText()
        radiocheck_pdf = self.dlg.radio_pdf.isChecked()
        radiocheck_png = self.dlg.radio_png.isChecked()
        if (filename and filtro_check and (radiocheck_pdf or radiocheck_png) ):
            self.dlg.atlas_btn.setEnabled(True);
        else:
            self.dlg.atlas_btn.setEnabled(False);
    
    def select_output_file(self):
        global filename
        filename = QFileDialog.getSaveFileName(self.dlg, "Save file", "", "*")
        #Altre opzioni QFileDialog:
        #filename = QFileDialog.getOpenFileName(self.dlg, "Load PNG file","", '*.png')
        #dirname = QFileDialog.getExistingDirectory(self.dlg, "Open output directory","", QFileDialog.ShowDirsOnly)
        self.dlg.fileBrowse_txt.setText(filename)
        self.activate_export() #controllo che l'atlante abbia un filtro e che sia stato scelto il nome del file e il tipo di file. allora abilito il pulsante di esportazione
    
    def set_Atlas_filter(self, query_string):
        composerlist = self.iface.activeComposers()
        for item in composerlist:
            Utils.logMessage("Nome composer:"+item.composerWindow().windowTitle())
        #Per i fini di questo plugin assumo vi sia UN SOLO composer:
        #myComposition = composerlist[0].composition()
        #myAtlas = item.composition().atlasComposition()
        Utils.logMessage("query_string: " + str(query_string))
        myAtlas.setFilterFeatures(True)
        myAtlas.setCoverageLayer(layer_da_filtrare)
        myAtlas.setFeatureFilter(query_string)
        myAtlas.setFilterFeatures(True)
        self.get_Atlas_filter()
        
    def get_Atlas_filter(self):
        global myComposition
        global myAtlas
        myComposition = None
        myAtlas = None
        composerlist = self.iface.activeComposers()
        #Per i fini di questo plugin assumo vi sia UN SOLO composer:
        myComposition = composerlist[0].composition()
        myAtlas = myComposition.atlasComposition()
        coverage_layer = myAtlas.coverageLayer()
        atlas_filter = myAtlas.featureFilter()
        Utils.logMessage("atlas_filter: " + str(atlas_filter))
        self.dlg.coverage_layer_txt.setText(coverage_layer.name())
        self.dlg.filter_atlas_txt.setPlainText(atlas_filter)
    
    def seleziona(self):
        #Recupero la stringa del filtro completa del campo:
        field_da_filtrare = self.dlg.combo_fields.currentText()
        filtro_txt = self.dlg.filter_txt.toPlainText()
        query_string = u'"%s" %s' % (str(field_da_filtrare), str(filtro_txt))
        Utils.logMessage("Filtro: " + query_string)
        filtra_atlas = self.dlg.atlas_ckbox.isChecked()
        #Applico il filtro al layer scelto:
        msg = QMessageBox()
        try:
            #Testo prima la correttezza dell'espressione:
            #fields_of_layer = layer_da_filtrare.fields()
            #s = QgsExpression.isValid(query_string, fields_of_layer, 'error') #deprecated
            s = QgsExpression.isValid(query_string, None, 'error')
            if (s != True):
                raise NameError("Errore nella query: l'espressione e' corretta?")
            else:
                test_filtro = layer_da_filtrare.setSubsetString( query_string )
                #Questo filtro devo assegnarlo anche all'Atlas?
                if (filtra_atlas==True):
                    self.set_Atlas_filter(query_string)
                
                #Posso attivare il pulsante di esportazione?
                self.activate_export() #controllo che l'atlante abbia un filtro e che sia stato scelto il nome del file e il tipo di file. allora abilito il pulsante di esportazione
                
                '''
                #Se invece di filtrare volessi attuare una selezione:
                select_expression = QgsExpression( query_string )
                #request = QgsFeatureRequest().setFilterExpression( query_string )
                #test_select = layer_da_filtrare.getFeatures( request )
                test_select = layer_da_filtrare.getFeatures( QgsFeatureRequest( select_expression ) )
                #Build a list of feature Ids from the result obtained:
                ids_selected = [i.id() for i in test_select]
                #Select features with the ids obtained in 3.:
                layer_da_filtrare.removeSelection() #ripulisco eventuali selezioni precedenti
                layer_da_filtrare.setSelectedFeatures( ids_selected )
                layer_ids_selezionate = layer_da_filtrare.selectedFeaturesIds()
                layer_feature_selezionate = layer_da_filtrare.selectedFeatures()
                #for j_ids in layer_ids_selezionate: #questo j_ids contiene solo gli ID delle features selezionate
                for j_ids in layer_feature_selezionate:
                    recupera_valore_campo = j_ids[field_da_filtrare]
                    Utils.logMessage("ID: " + str(recupera_valore_campo))
                    #Se volessi modificare l'attributo delle feature selezionate:
                    #layer_da_filtrare.startEditing()
                    #idx_campo_da_modificare=layer_da_filtrare.fieldNameIndex('nome_campo')
                    #nuovo_valore_da_assegnare=None
                    #layer_da_filtrare.changeAttributeValue(j_ids, idx_campo_da_modificare, nuovo_valore_da_assegnare)
                    #layer_da_filtrare.rollBack()
                    #layer_da_filtrare.commitChanges()
                '''
            
        except NameError as err:
            msg.setText(err.args[0])
            #msg.setInformativeText("Descrizione ampliata")
            #msg.setDetailedText("The details are as follows:")
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Errore!")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()
            #if (retval != 1024): #l'utente NON ha cliccato ok
            #if (retval != 16384): #l'utente NON ha cliccato yes
            Utils.logMessage(err.args[0])
            return 0;
        except SystemError, e:
            Utils.logMessage(str(e))
            return 0
        else: #l'espressione e' corretta: ma restituisce effettivamente qualcosa?
            record_filtro = layer_da_filtrare.featureCount()
            #counted_selected = layer_da_filtrare.selectedFeatureCount()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Query corretta!")
            msg.setStandardButtons(QMessageBox.Ok)
            if int(record_filtro>0):
                msg.setText("Trovati " + str(record_filtro) + " record!")
                Utils.logMessage("Trovati " + str(record_filtro) + " record!")
            else:
                msg.setText("Nessuna corrispondenza trovata...")
                Utils.logMessage("Nessuna corrispondenza...")
            retval = msg.exec_()
    
    def inizializza_layer(self):
        legend = self.iface.legendInterface()
        layers_caricati = legend.layers()
        Utils.logMessage("Primo layer: " + layers_caricati[0].name())
        #Altro metodo:
        #registry = QgsMapLayerRegistry.instance()
        #layers_loaded = registry.mapLayers().values()
        #Utils.logMessage("First layer: " + layers_loaded[0].name())
        #O ancora:
        #layers_canvas = self.iface.mapCanvas().layers()
        #Utils.logMessage("First layer canvas: " + layers_canvas[0].name())
        #Per definire un layer specifico:
        #custom_layer = QgsMapLayerRegistry.instance().mapLayersByName('<nome_layer_in_legenda>')[0]
        
        #In ogni caso dobbiamo ciclare dentro i layer per popolare il combobox.
        global default_text
        default_text = '--Scegli un layer--'
        self.dlg.combo_layer.addItem(default_text) #prima opzione non valida
        for layer in layers_caricati:
            #Se raster pero lo esonero, non avendo campi su cui filtrare:
            if (layer.type() == 0): #non ho trovato la decodifica. Per ragionamento induttivo pare sia 0-vector; 1-raster;
                self.dlg.combo_layer.addItem(layer.name())
        #Seleziono la prima opzione:
        idx = self.dlg.combo_layer.findText(default_text)
        self.dlg.combo_layer.setCurrentIndex(idx)
        
        #Altri comandi sui layer:
        #iface.activeLayer() #intercettare il layer attivo nella TOC
        #per caricare un layer:
        #layer = QgsVectorLayer(data_source, layer_name, provider_name) #oppure QgsRasterLayer(path, baseName)
        #layer = iface.addVectorLayer("/path/to/shapefile/file.shp", "layer name you like", "ogr")
        #if not layer.isValid():
        #    print "Layer failed to load!"
        #    return
        #Per intercettare la geometria di un layer:
        #f = iface.activeLayer().selectedFeatures()[0]
        #f.geometry().type()
        #ma la decodifica dove sta?
        
        
    def updateFromSelection_layers(self):
        global layer_da_filtrare
        layer_da_filtrare = None
        layername_da_filtrare = self.dlg.combo_layer.currentText()
        if (layername_da_filtrare != default_text and layername_da_filtrare != ''):
            self.dlg.combo_fields.setEnabled(True)
            Utils.logMessage("Layer da filtrare: " + layername_da_filtrare)
            layer_da_filtrare = QgsMapLayerRegistry.instance().mapLayersByName(layername_da_filtrare)[0]
            #Recupero i campi del layer:
            #fields = layer_da_filtrare.pendingFields() #alias di fields()
            fields_only = layer_da_filtrare.fields()   
            field_names_only = [field.name() for field in fields_only]
            Utils.logMessage("Campi: " + str(field_names_only))
            #Popolo il menu a tendina ma prima lo svuoto:
            self.dlg.combo_fields.clear()
            self.dlg.atlas_ckbox.setChecked(False) #svuoto anche l'opzione per l'Atlas
            for field_name in field_names_only:
                self.dlg.combo_fields.addItem(field_name)
            #Attivo il tasto finale:
            self.dlg.select_btn.setEnabled(True)
        else:
            self.dlg.combo_fields.setEnabled(False)
            self.dlg.select_btn.setEnabled(False)
            
    def get_field_type(self):
        if not(layer_da_filtrare):
            return 0
        field_da_filtrare = self.dlg.combo_fields.currentText()
        idx_field = layer_da_filtrare.fields().indexFromName(field_da_filtrare)
        if (idx_field == -1): #al cambio di combobox non riconosce subito l'indice del campo
            return 0
        type_field = layer_da_filtrare.fields().field(idx_field).typeName()
        Utils.logMessage("idx field: " + str(type_field))
        self.dlg.field_type.setText(str(type_field))
        
        
        
    #--------------------------------------------------------------------------

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('EsportaAtlanteHail', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def disconnetto_pulsanti(self):
        #Avendo definito un dock e volendo sfruttare anche il dialog, devo disconnettere alcuni oggetti per poi riconnetterli onde evitare doppie azioni
        #In realta' anche questa disconnessione e' difficle da gestire...Usare o il Dock o il Dialog!!
        self.dlg.select_btn.clicked.disconnect(self.seleziona)
        self.dlg.radio_pdf.clicked.disconnect(self.activate_export)
        self.dlg.radio_png.clicked.disconnect(self.activate_export)
        self.dlg.atlas_btn.clicked.disconnect(self.export_atlas)
        #SALVA FILE con nome
        self.dlg.fileBrowse_btn.clicked.disconnect(self.select_output_file)        
        #se modifico il drop down faccio partire un'azione:
        QObject.disconnect(self.dlg.combo_layer, SIGNAL("currentIndexChanged(const QString&)"), self.updateFromSelection_layers)
        QObject.disconnect(self.dlg.combo_fields, SIGNAL("currentIndexChanged(const QString&)"), self.get_field_type)
        
    def connetto_pulsanti(self):
        #Avendo definito un dock e volendo sfruttare anche il dialog, richiamo qui le azioni sui pulsanti prima definite sotto initGui()
        self.dlg.pageBar.setValue(0)
        self.dlg.select_btn.clicked.connect(self.seleziona)
        self.dlg.radio_pdf.clicked.connect(self.activate_export)
        self.dlg.radio_png.clicked.connect(self.activate_export)
        self.dlg.atlas_btn.clicked.connect(self.export_atlas)
        #SALVA FILE con nome
        self.dlg.fileBrowse_txt.clear()
        self.dlg.fileBrowse_btn.clicked.connect(self.select_output_file)        
        #se modifico il drop down faccio partire un'azione:
        QObject.connect(self.dlg.combo_layer, SIGNAL("currentIndexChanged(const QString&)"), self.updateFromSelection_layers)
        QObject.connect(self.dlg.combo_fields, SIGNAL("currentIndexChanged(const QString&)"), self.get_field_type)
        
    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/EsportaAtlanteHail/hail.png'
        self.add_action(
            icon_path,
            text=self.tr(u'EsportaAtlanteHail'),
            callback=self.run,
            parent=self.iface.mainWindow())
            
        #Aggiungo DockWidget:
        icon_path = ':/plugins/EsportaAtlanteHail/hail_dock.png'
        self.add_action(
            icon_path,
            text=self.tr(u'EsportaAtlanteHail versione Dock'),
            callback=self.run_dock,
            parent=self.iface.mainWindow())
        
        #Implemento alcune azioni sui miei pulsanti
        self.connetto_pulsanti()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            #self.iface.removePluginDatabaseMenu(
            self.iface.removePluginMenu(
                self.tr(u'&EsportaAtlanteHail'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
        
    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        #print "** CLOSING Core"
        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        # remove this statement if dockwidget is to remain for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe when closing the docked window:
        # self.dockwidget = None
        self.pluginIsActive = False
        
    def clean_elements(self):
        #All'apertura della finestra ripulisco eventuali tracce precedenti:
        self.dlg.combo_layer.clear()
        self.dlg.combo_fields.clear()
        self.dlg.filter_txt.clear()
        self.dlg.fileBrowse_txt.clear()
        self.dlg.pageBar.setValue(0)
        self.dlg.field_type.setText('field type')
        self.dlg.atlas_ckbox.setChecked(False)
        
        self.dlg.buttonGroup.setExclusive(False);
        self.dlg.radio_png.setChecked(False)
        self.dlg.radio_pdf.setChecked(False)
        self.dlg.buttonGroup.setExclusive(True);
    
    def run_dock(self):
        """Run method that loads and starts the plugin"""
        if not self.pluginIsActive:
            self.pluginIsActive = True
            #print "** STARTING Core"
            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = EsportaAtlanteHailDockDockWidget()
            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
            # show the dockwidget
            # TODO: fix to allow choice of dock location        
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)

            #Per non riscrivere tutto il codice precedente, ridefinisco il QDialog per sostituirlo con questo DockWidget, equiparando le 2 variabili:
            self.dlg = self.dockwidget

            #All'apertura della finestra ripulisco eventuali tracce precedenti:
            self.clean_elements()
            
            #Inizializzo i layer presenti in mappa:
            self.inizializza_layer()            
            #Recupero informazioni sull'Atlas:
            self.get_Atlas_filter()
            
            #Ridefinisco le azioni sui pulsanti. Per evitare comportamenti anomali dovuti alla copresenza di Dock e Dialog prima li disconnetto:
            #self.disconnetto_pulsanti() #genera anomalie
            self.connetto_pulsanti()
        
            # show the dock
            self.dockwidget.show()
    
    def run(self):
        #Se ho aggiunto il Dock, riporto il self.dlg al Dialog:
        self.dlg = EsportaAtlanteHailDialog()
        
        #All'apertura della finestra ripulisco eventuali tracce precedenti:
        self.clean_elements()
        
        #Inizializzo i layer presenti in mappa:
        self.inizializza_layer()        
        #Recupero informazioni sull'Atlas:
        self.get_Atlas_filter()
        
        #Ridefinisco le azioni sui pulsanti. Per evitare comportamenti anomali dovuti alla copresenza di Dock e Dialog prima li disconnetto:
        #self.disconnetto_pulsanti() #genera anomalie
        self.connetto_pulsanti()
        
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        '''result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass'''
