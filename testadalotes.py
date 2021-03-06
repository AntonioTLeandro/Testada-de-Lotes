# -*- coding: utf-8 -*-
"""
/***************************************************************************
 testadalotes
                                 A QGIS plugin
 Gerar testada de lotes
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-03-01
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Antônio Teles / Gloria Santos
        email                : antoniot.leandro@gmaill.com/mdgss.gloria@gmail.com
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
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.PyQt import QtCore
from qgis.gui import *
from PyQt5 import QtCore, QtGui
import pdb
from qgis.core import *

from qgis.gui import QgsMessageBar, QgsMapCanvas, QgsMapCanvasItem
import qgis.utils
import os
from collections import defaultdict

from shapely.wkb import loads
from osgeo import ogr
import processing

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QDialog

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .testadalotes_dialog import testadalotesDialog
import os.path

class testadalotes:
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
            'testadalotes_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.dlg = testadalotesDialog()
        self.actions = []
        self.menu = self.tr(u'&Testada de Lotes')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('testadalotes', message)


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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/testadalotes/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Gerar testada de lotes'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

        self.dlg.caminho.clear()
        self.dlg.select_caminho.clicked.connect(self.selecione_caminho)

        self.dlg.salvememoria.clicked.connect(self.verificar_salvememeoria)



    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Testada de Lotes'),
                action)
            self.iface.removeToolBarIcon(action)

    def verificar_salvememeoria(self):
        verificar = self.dlg.salvememoria.isChecked()
        if verificar: 
            self.dlg.select_caminho.setEnabled(False)
            self.dlg.caminho.setEnabled(False)
            self.dlg.label_5.setEnabled(False)
        else: 
            self.dlg.select_caminho.setEnabled(True)
            self.dlg.caminho.setEnabled(True)
            self.dlg.label_5.setEnabled(True)



    def selecione_caminho(self):
        # Abri janela para escolher caminho onde vai salvar o shape
        filtering="Shapefiles (*.shp *.SHP)"
        settings = QSettings()
        dirName = settings.value("/UI/lastShapefileDir")
        encode = settings.value("/UI/encoding")
        fileDialog = QgsEncodingFileDialog(None, QCoreApplication.translate("fTools", "Save output shapefile"), dirName, filtering, encode)
        fileDialog.setDefaultSuffix("shp")
        fileDialog.setFileMode(QFileDialog.AnyFile)
        fileDialog.setAcceptMode(QFileDialog.AcceptSave)
        #fileDialog.setConfirmOverwrite(True)
        if not fileDialog.exec_() == QDialog.Accepted:
            return None, None

        files = fileDialog.selectedFiles()
        settings.setValue("/UI/lastShapefileDir", QFileInfo(unicode(files[0])).absolutePath())
        self.outFilePath = unicode(files[0])
        self.encoding = unicode(fileDialog.encoding())
        self.dlg.caminho.setText(self.outFilePath)
        self.nomeshape = files

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        
        #Limpa o caminho pra salvar o arquivo
        self.dlg.caminho.clear() 

        # Carrega os Layer que corresponde somente a Shp de polylines
        layers = QgsProject.instance().mapLayers().values()
        self.dlg.select_layer.clear()
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                self.dlg.select_layer.addItem( layer.name(), layer )  

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            if not self.dlg.salvememoria.isChecked() and not self.dlg.caminho.text():
                self.iface.messageBar().pushMessage("Alerta", "Existe campos obrigatório sem preenchimento.", level=Qgis.Warning) 
            else:    
                
                # Do something useful here - delete the line containing pass and
                # substitute with your code.
                for selectlayer in QgsProject.instance().mapLayers().values():
                    if selectlayer.name() == self.dlg.select_layer.currentText():
                        pr_lotes = selectlayer.dataProvider()
                        sRs = selectlayer.crs()

                        diretorio_file = os.getcwd()
                        arquivo_lixo = 'arquivo_lixo.shp'
                        self.Fields_lixo = QgsFields()
                        self.outputPolygonShape = QgsVectorFileWriter(diretorio_file + '/' + arquivo_lixo, "utf-8", self.Fields_lixo, QgsWkbTypes.Polygon, sRs, "ESRI Shapefile")

                        poligono = QgsVectorLayer(diretorio_file + '/' + arquivo_lixo, "poligono", "ogr" )
                        p_poligono = poligono.dataProvider()
                        for selectLay in QgsProject.instance().mapLayers().values():
                            if selectLay.name() == self.dlg.select_layer.currentText():
                                for featLay in selectLay.getFeatures():
                                    geom_featLay = featLay.geometry()
                                    featL = QgsFeature()
                                    featL.setGeometry(geom_featLay)
                                    p_poligono.addFeature(featL)
                        poligono.commitChanges()

                        parameter_dissolve = { 'COMPUTE_AREA' : False, 'COMPUTE_STATISTICS' : False, 'COUNT_FEATURES' : False, 'EXPLODE_COLLECTIONS' : False, 'FIELD' : '', 'GEOMETRY' : 'geometry', 'INPUT' : diretorio_file + '/' + arquivo_lixo, 'KEEP_ATTRIBUTES' : False, 'OPTIONS' : '', 'OUTPUT' : 'TEMPORARY_OUTPUT', 'STATISTICS_ATTRIBUTE' : '' }
                        shape_dissolve = processing.run('gdal:dissolve', parameter_dissolve)         
                        break

                shape_face = QgsVectorLayer(shape_dissolve['OUTPUT'], 'face', 'ogr')
                
                layer_line = QgsVectorLayer("LineString?", "layer_line", "memory" )
                pr = layer_line.dataProvider()
                for feat in shape_face.getFeatures():
                    geom_feat = feat.geometry()
                    geom_feat_m = geom_feat.asMultiPolygon()
                    for geom_listi in geom_feat_m:
                        for geom_list_ti in geom_listi:
                            feature_line = QgsFeature()

                            geom_line =  QgsGeometry.fromPolylineXY(geom_list_ti)
                            feature_line.setGeometry(geom_line)
                            pr.addFeature(feature_line)  

                corrdsList = []
                for selectlayer in QgsProject.instance().mapLayers().values():
                    if selectlayer.name() == self.dlg.select_layer.currentText(): 

                        for feature in selectlayer.getFeatures():
                            geom_Verif = feature.geometry()
                            attr = feature.attributes()    
                            for features_t in layer_line.getFeatures():
                                geom_Verif_t = features_t.geometry()
                                geom_t = geom_Verif_t.asPolyline()
                                intersect = geom_Verif.intersection(geom_Verif_t)

                                if intersect:
                                    wkb = intersect.asWkb() 
                                    geom_ogr = ogr.CreateGeometryFromWkb(wkb)
                                    tipo_line = intersect.wkbType()
                                    d = 0
                                    coords = []
                                    coords_i = []
                                    if tipo_line == 1002 or tipo_line == 2:
                                        coords.append(QgsPointXY(geom_ogr.GetX(0), geom_ogr.GetY(0)))
                                        coords.append(QgsPointXY(geom_ogr.GetX(1), geom_ogr.GetY(1)))  
                                        corrdsList.append([coords, attr])
                                    else:
                                        for items in geom_ogr:
                                            if d == 0:
                                                if items.GetX(0) != items.GetX(1) and items.GetY(0) != items.GetY(1):
                                                    coords_i.append(QgsPointXY(items.GetX(0), items.GetY(0)))
                                                    coords_i.append(QgsPointXY(items.GetX(1), items.GetY(1)))
                                                    item_anterior = items
                                                    d += 1
                                            else:
                                                if items.GetX(0) != items.GetX(1) and items.GetY(0) != items.GetY(1):
                                                    if item_anterior.GetX(1) != items.GetX(0) and item_anterior.GetY(1) != items.GetY(0):
                                                        corrdsList.append([coords_i, attr])
                                                        coords_i = []
                                                        coords_i.append(QgsPointXY(items.GetX(0), items.GetY(0)))
                                                        coords_i.append(QgsPointXY(items.GetX(1), items.GetY(1)))
                                                        item_anterior = items
                                                    else:
                                                        coords_i.append(QgsPointXY(items.GetX(1), items.GetY(1)))
                                                        item_anterior = items
                                                d += 1 
                                    if coords_i:
                                        corrdsList.append([coords_i, attr])
                                    break  
                field_names = pr_lotes.fields()
                field_names.append(QgsField('TAM_TESTADA',QVariant.Double))
                
                if not self.dlg.salvememoria.isChecked(): 
                    self.Fields = QgsFields()
                    for field_attr in field_names:
                        self.Fields.append(QgsField(field_attr.name(),field_attr.type()))
                    
                    global SHPCaminho
                    SHPCaminho = self.outFilePath
                    self.outputlineShape = QgsVectorFileWriter(SHPCaminho, self.encoding, self.Fields, QgsWkbTypes.LineString, sRs, "ESRI Shapefile")
                            
                    for item in corrdsList:   
                        self.feature_lineg = QgsFeature()
                        geom_lineg =  QgsGeometry.fromPolylineXY(item[0])
                        tam = geom_lineg.length()
                        item[1].append(round(tam, 3))
                        if tam < 100000:
                            self.feature_lineg.setGeometry(geom_lineg)
                            self.feature_lineg.setAttributes(item[1])
                            self.outputlineShape.addFeature(self.feature_lineg)
                    
                    pegarNome = self.outFilePath
                    Nomes = pegarNome.split( '/' )
                    contNomes = len(Nomes) - 1
                    nomefinalshp = Nomes[contNomes]
                    nomefinalshp =  nomefinalshp.replace('.shp','')
                    nomefinalshp =  nomefinalshp.replace('.SHP','')

                    self.layer = QgsVectorLayer(self.outFilePath, nomefinalshp, "ogr")
                    if not self.layer.isValid():
                        raise ValueError("Failed to open the layer")
                    self.canvas = QgsMapCanvas()
                    QgsProject.instance().addMapLayer(self.layer)
                    self.canvas.setExtent(self.layer.extent())
                    self.canvas.setLayers([self.layer])
                    del self.outputlineShape
                    QgsProject.instance().removeMapLayer(self.layer)
                    self.layer = QgsVectorLayer(self.outFilePath, nomefinalshp, "ogr")
                    QgsProject.instance().addMapLayer(self.layer) 
                else:
                    
                    testada_lotes = QgsVectorLayer("LineString?crs=" + sRs.authid(), "TESTADA_DE_LOTES", "memory" )
                    pr_testada_lotes = testada_lotes.dataProvider()

                    for field_attr in field_names:
                        pr_testada_lotes.addAttributes([QgsField(field_attr.name(),field_attr.type())])
                        testada_lotes.updateFields()

                    for item in corrdsList:   
                        self.feature_lineg = QgsFeature()
                        geom_lineg =  QgsGeometry.fromPolylineXY(item[0])
                        tam = geom_lineg.length()
                        item[1].append(round(tam, 3))
                        if tam < 100000:
                            self.feature_lineg.setGeometry(geom_lineg)
                            self.feature_lineg.setAttributes(item[1])
                            pr_testada_lotes.addFeature(self.feature_lineg)
                    QgsProject.instance().addMapLayer(testada_lotes) 


                del self.outputPolygonShape
                del poligono
                list_dados = os.listdir(diretorio_file + '/')      
                for item_list in list_dados:
                    arq = arquivo_lixo.split('.')
                    if arquivo_lixo.split('.')[0] == item_list.split('.')[0]:
                        os.remove(diretorio_file + '/' + item_list)
