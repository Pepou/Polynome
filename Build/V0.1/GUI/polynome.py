# -*- coding: utf-8 -*-

"""
Module implementing Polynome.
"""

from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtGui import QMainWindow
from PyQt4.QtGui import QInputDialog
from datetime import datetime

from .Ui_polynome import Ui_Polynome

import numpy as np
import scipy.stats as sp
import decimal

from PyQt4.Qwt5 import *
from PyQt4.Qwt5.qplt import *
import PyQt4.Qwt5.iqt
from Package.AccesBdd import AccesBdd

class Polynome(QMainWindow, Ui_Polynome):
    """
    Class documentation goes here.
    """
    def __init__(self,login, password,  parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget (QWidget)
        """
        super().__init__(parent)
        self.setupUi(self)
        
        self.db = AccesBdd(login, password)
        
        self.actionEnregistrer.setEnabled(False)
        self.actionMise_jour.setEnabled(False)
        
        #configuration largeur colonnes tablewidget
        self.tableWidget_table_etalonnage.setColumnWidth(0,200)
        self.tableWidget_table_etalonnage.setColumnWidth(1,200)
        self.tableWidget_table_etalonnage.setColumnWidth(2,200)
        self.tableWidget_table_etalonnage.setColumnWidth(3,200)
        self.tableWidget_table_etalonnage.setColumnWidth(4,200)
        self.tableWidget_table_etalonnage.setColumnWidth(5,200)
        
        self.tableWidget_modelisation.setColumnWidth(0,200)
        self.tableWidget_modelisation.setColumnWidth(1,200)
        self.tableWidget_modelisation.setColumnWidth(2,200)
        self.tableWidget_modelisation.setColumnWidth(3,100)
        self.tableWidget_modelisation.setColumnWidth(4,100)
        self.tableWidget_modelisation.setColumnWidth(5,150)
        self.tableWidget_modelisation.setColumnWidth(6,100)
        self.tableWidget_modelisation.setColumnWidth(7,150)
        
        #gestion graphique
        self.x_array = []
        self.y_array = []
        self.y_modelise = []
        
        
        self.qwtPlot.setCanvasBackground(Qt.gray)
        self.qwtPlot.setAxisTitle(QwtPlot.xBottom, 'Temperature')
        self.qwtPlot.setAxisAutoScale(QwtPlot.xBottom)
        
        self.qwtPlot.setAxisTitle(QwtPlot.yLeft, 'Correction')
        self.qwtPlot.setAxisAutoScale(QwtPlot.yLeft)      
        
        self.curve = QwtPlotCurve('Correction = f(Tlue)')      
        self.curve_2 = QwtPlotCurve('y =  f(x)')
        



    
    @pyqtSlot()
    def on_radioButton_modification_clicked(self):
        """
        Fct qui lorsque qu'on appui sur le radio bouton va chercher l'ensemble des instruments ayant un poly ds la bdd 
        nettoie combobox n° CE
        """
        # TODO: not implemented yet
        self.actionEnregistrer.setEnabled(False)
        self.actionMise_jour.setEnabled(False)
        
        self.comboBox_identification.clear()
        self.comboBox_n_ce.clear()
        self.clear_all()
        
        instruments = set(self.db.resencement_instrument_table_polynome_correction()) #on convertie en set poour eviter les doublons
        list_instruments = list(instruments)
        list_instruments.sort()
        self.comboBox_identification.addItems(list_instruments)
    
    @pyqtSlot()
    def on_radioButton_new_saisie_clicked(self):
        """
        Slot documentation goes here.
        """
        self.actionEnregistrer.setEnabled(False)
        self.actionMise_jour.setEnabled(False)
        
        self.comboBox_identification.clear()
        self.comboBox_n_ce.clear()
        self.clear_all()
        
        instruments = self.db.resencement_instrument() 
        instruments.sort()
        self.comboBox_identification.addItems(instruments)
    
    
    @pyqtSlot(str)
    def on_comboBox_identification_activated(self, p0):
        """
        fct qui en fct du current item va chcher les n° ce de l'intrument et l'affiche combobox n°CE
        Recupere et affiche caracteristique instrument
        """
        #nettoyage
        self.clear_all()
        self.comboBox_n_ce.clear()        
        self.clear_plot()    
        self.textEdit_constructeur.clear()
        self.textEdit_model.clear()
        self.textEdit_n_serie.clear()
        self.clear_plot()
        
        
        #gestion qtextedit
        ident_instrument = self.comboBox_identification.currentText ()
        caracteristique_instrument = self.db.return_caracteristiques_intrument(ident_instrument)
            #constructeur
        self.textEdit_constructeur.append(caracteristique_instrument[0])
            #n°serie
        self.textEdit_n_serie.append(caracteristique_instrument[2])
            #REFERENCE_CONSTRUCTEUR
        self.textEdit_model.append(caracteristique_instrument[1])            
            #resolution
        resolution_instrum = str(caracteristique_instrument[3])
                #mise en forme resolution
        i = len(resolution_instrum) - 1 #cles indices commencent  à 0        
        while resolution_instrum[i - 1] == "0" or resolution_instrum[i - 1] == ".":
            i-=1
        
        self.lineEdit_resolution.setText(resolution_instrum[:i])
        
        
        if self.radioButton_modification.isChecked():            
            #gestion combobox
            list_n_ce = self.db.resencement_ce_ident_instrument_table_polynome_correction(ident_instrument)
            self.comboBox_n_ce.addItems(list_n_ce)
            

    @pyqtSlot(str)
    def on_comboBox_n_ce_activated(self, p0):
        """
        fct gerant apres selection d'un n° 
        l'affichage des caracteristique du poly ainsi que la table d'etalonnage correspondante
        """

        self.clear_onglet_2()
        n_ce = self.comboBox_n_ce.currentText()
        caract_poly = self.db.renvoie_caracteristique_poly_n_ce(n_ce)

        self.dateEdit.setDate(caract_poly[0])
        
        if caract_poly[5] == True: #la question est de savoir si il est archivé : oui il est archivé
            self.comboBox_etat_polynome.setCurrentIndex(0)
        else:
            self.comboBox_etat_polynome.setCurrentIndex(1)
        
        
        #Donnees d'etalonnage
        donnee_table_poly = self.db.recuperation_donnees_table_polynome_table_etalonnage(caract_poly[6])
        
        
        if not donnee_table_poly: #(signifie vide)
            donnees_etal = self.db.recuperation_donnees_etalonnage_n_ce(n_ce)
        else:
            donnees_etal = donnee_table_poly
        
        #nettoyage tableaux donnees
        nbr_ligne = int(self.tableWidget_table_etalonnage.rowCount())
        
        if nbr_ligne !=0:
            for i in range(nbr_ligne):
                self.tableWidget_table_etalonnage.removeRow(0)
        
        nbr_ligne_poly = int(self.tableWidget_polynome.rowCount())
        
        if nbr_ligne_poly !=1:
            for i in range(1, nbr_ligne_poly):
                self.tableWidget_polynome.removeRow(i)
                
        #nettoyage graph
        self.clear_plot()
        
        #Insertions des donnes dans le tableau (donnees)
        i=0
        for ele in donnees_etal:            
            self.tableWidget_table_etalonnage.insertRow(i)
            #colonne ordre apparition CE
            self.tableWidget_table_etalonnage.setItem(i, 0, QtGui.QTableWidgetItem(str(i+1)))
            #Valeurs corrigees etalonnage
            self.tableWidget_table_etalonnage.setItem(i, 1, QtGui.QTableWidgetItem(str(donnees_etal[i][0])))
            #Valeurs instrument
            self.tableWidget_table_etalonnage.setItem(i, 2, QtGui.QTableWidgetItem(str(donnees_etal[i][1])))
            #Corrections
            self.tableWidget_table_etalonnage.setItem(i, 3, QtGui.QTableWidgetItem(str(donnees_etal[i][2])))
            #Erreur
            self.tableWidget_table_etalonnage.setItem(i, 4, QtGui.QTableWidgetItem(str((-1)*donnees_etal[i][2])))
            #Incertitudes
            self.tableWidget_table_etalonnage.setItem(i, 5, QtGui.QTableWidgetItem(str(donnees_etal[i][3])))
                        
            i+=1
        
        #Insertion tableau polynome
        self.tableWidget_polynome.setItem(0, 0, QtGui.QTableWidgetItem(str(caract_poly[1])))
        
        if caract_poly[1] == 1:
            self.tableWidget_polynome.setItem(0, 1, QtGui.QTableWidgetItem(str(caract_poly[2])))
            self.tableWidget_polynome.setItem(0, 2, QtGui.QTableWidgetItem(str(caract_poly[3])))
        else:
            self.tableWidget_polynome.setItem(0, 1, QtGui.QTableWidgetItem(str(caract_poly[2])))
            self.tableWidget_polynome.setItem(0, 2, QtGui.QTableWidgetItem(str(caract_poly[3])))
            self.tableWidget_polynome.setItem(0, 3, QtGui.QTableWidgetItem(str(caract_poly[4])))
        
        if len(donnees_etal) != 0: #permet de pas avoir d'erreur s'il n'y a pas de donnee dans la table etal
            self.courbe_polynome()
            self.gestion_tableWidget_modelisation()
        else:
            pass
        
    
    @pyqtSlot()
    def on_buttton_supp_clicked(self):
        """
        fct qui supprime la ligne selectionné dans le tableau table etalonnage
        """
        
        ligne_selectionnee = self.tableWidget_table_etalonnage.selectionModel().currentIndex().row()
        self.tableWidget_table_etalonnage.removeRow(ligne_selectionnee)
        
        if self.radioButton_modification.isChecked():
            self.actionMise_jour.setEnabled(False)
        else:
            self.actionEnregistrer.setEnabled(False)
        
#        new_poly = self.calcul_polynome()
#        self.courbe_polynome()
   
    @pyqtSlot()
    def on_Button_plus_clicked(self):
        """
        fct qui ajoute une ligne en dessous de la ligne selectionnee.
        """
        
        ligne_selectionnee = self.tableWidget_table_etalonnage.selectionModel().currentIndex().row()
        self.tableWidget_table_etalonnage.insertRow((ligne_selectionnee+1))
        
        if self.radioButton_modification.isChecked():
            self.actionMise_jour.setEnabled(False)
        else:
            self.actionEnregistrer.setEnabled(False)
            
    def calcul_polynome(self):
        '''Fonction qui calcul un polynome depuis le tableau:
        x et y doivent etre des lists et ordre un entier'''
    
        nbr_ligne = self.tableWidget_table_etalonnage.rowCount()

        list_Tlue = []
        list_correction = [] 
        for i in range(nbr_ligne):
            list_Tlue.append(float(self.tableWidget_table_etalonnage.item(i, 2).text()))
            list_correction.append(float(self.tableWidget_table_etalonnage.item(i, 3).text()))
        
        ordre = QInputDialog.getInteger (self, 
                        self.trUtf8("Choix ordre polynome"), 
                        self.trUtf8("Ordres"), 1, 1, 2, 1)
        
        poly = np.polyfit(list_Tlue, list_correction, ordre[0])
        
               
        nbr_ligne_poly = self.tableWidget_polynome.rowCount()
        test_case_vide_coef_a =  self.tableWidget_polynome.item(0, 2)
       
        if test_case_vide_coef_a != None:
            self.tableWidget_polynome.insertRow(nbr_ligne_poly)        
            
            if ordre[0] == 1:
                #arrondissage polynome en 1.10-12:
                resolution = str(0.000000000001)
                coeff_a = decimal.Decimal(str(poly[0])).quantize(decimal.Decimal(resolution), rounding=decimal.ROUND_HALF_EVEN)
                coeff_b = decimal.Decimal(str(poly[1])).quantize(decimal.Decimal(resolution), rounding=decimal.ROUND_HALF_EVEN)
                
                self.tableWidget_polynome.setItem(nbr_ligne_poly, 0, QtGui.QTableWidgetItem(str(ordre[0])))
                self.tableWidget_polynome.setItem(nbr_ligne_poly, 1, QtGui.QTableWidgetItem(str(coeff_a)))
                self.tableWidget_polynome.setItem(nbr_ligne_poly, 2, QtGui.QTableWidgetItem(str(coeff_b)))
            else:
                #arrondissage polynome en 1.10-12:
                resolution = str(0.000000000001)
                coeff_a = decimal.Decimal(str(poly[0])).quantize(decimal.Decimal(resolution), rounding=decimal.ROUND_HALF_EVEN)
                coeff_b = decimal.Decimal(str(poly[1])).quantize(decimal.Decimal(resolution), rounding=decimal.ROUND_HALF_EVEN)
                coeff_c = decimal.Decimal(str(poly[2])).quantize(decimal.Decimal(resolution), rounding=decimal.ROUND_HALF_EVEN)
                
                self.tableWidget_polynome.setItem(nbr_ligne_poly, 0, QtGui.QTableWidgetItem(str(ordre[0])))
                self.tableWidget_polynome.setItem(nbr_ligne_poly, 1, QtGui.QTableWidgetItem(str(coeff_a)))
                self.tableWidget_polynome.setItem(nbr_ligne_poly, 2, QtGui.QTableWidgetItem(str(coeff_b)))
                self.tableWidget_polynome.setItem(nbr_ligne_poly, 3, QtGui.QTableWidgetItem(str(coeff_c)))
            
            item = QtGui.QTableWidgetItem()
            self.tableWidget_polynome.setVerticalHeaderItem(nbr_ligne_poly, item)
            item.setText("Nouveau Polynome")
            return poly
        
        else:
            if ordre[0] == 1:
                self.tableWidget_polynome.setItem(0, 0, QtGui.QTableWidgetItem(str(ordre[0])))
                self.tableWidget_polynome.setItem(0, 1, QtGui.QTableWidgetItem(str(poly[0])))
                self.tableWidget_polynome.setItem(0, 2, QtGui.QTableWidgetItem(str(poly[1])))
            else:
                self.tableWidget_polynome.setItem(0, 0, QtGui.QTableWidgetItem(str(ordre[0])))
                self.tableWidget_polynome.setItem(0, 1, QtGui.QTableWidgetItem(str(poly[0])))
                self.tableWidget_polynome.setItem(0, 2, QtGui.QTableWidgetItem(str(poly[1])))
                self.tableWidget_polynome.setItem(0, 3, QtGui.QTableWidgetItem(str(poly[2])))
            
            
            return poly
            

    def courbe_polynome(self):
        '''fct qui trace la courbe y = f(x) avec x et y des lists'''

        nbr_ligne = self.tableWidget_table_etalonnage.rowCount()

        list_Tlue = []
        list_correction = [] 
        for i in range(nbr_ligne):
            list_Tlue.append(float(self.tableWidget_table_etalonnage.item(i, 2).text().replace(",", ".")))
            list_correction.append(float(self.tableWidget_table_etalonnage.item(i, 3).text().replace(",", ".")))
     

        self.x_array = np.array(list_Tlue)
        self.y_array = np.array(list_correction)
        
        #courbe des pts
       
        self.curve = QwtPlotCurve('Correction = f(Tlue)')
        self.curve.setSymbol(QwtSymbol(QwtSymbol.Rect,
                            QBrush(Qt.white), QPen(Qt.black), QSize(7,7)))

        self.curve.setData(self.x_array, self.y_array)        
        self.curve.attach(self.qwtPlot)        
        self.curve.setPen(QPen(Qt.gray))
        
        
        #courbe poly
        nbr_poly = self.tableWidget_polynome.rowCount() 
    
        ordre = int(self.tableWidget_polynome.item(nbr_poly-1,0 ).text())
        
        list_y_modelise = []
        if ordre > 1:
            a = float(self.tableWidget_polynome.item(nbr_poly-1,1 ).text().replace(",", "."))
            b = float(self.tableWidget_polynome.item(nbr_poly-1,2 ).text().replace(",", "."))
            c = float(self.tableWidget_polynome.item(nbr_poly-1,3 ).text().replace(",", "."))
            self.x_array.sort()
            for ele in self.x_array:
                list_y_modelise.append(a*ele*ele + b*ele + c)
        else:
            a = float(self.tableWidget_polynome.item(nbr_poly-1,1 ).text().replace(",", "."))
            b = float(self.tableWidget_polynome.item(nbr_poly-1,2 ).text().replace(",", "."))
            self.x_array.sort()
            for ele in self.x_array:                
                list_y_modelise.append(a*float(ele) + b)
        
        self.x_array.sort()
        self.y_modelise = np.array(list_y_modelise)

        self.curve_2.setData(self.x_array, self.y_modelise)
        self.curve_2.attach(self.qwtPlot)
        self.curve_2.setPen(QPen(Qt.red))
        
        self.qwtPlot.replot()
        
        
    def gestion_tableWidget_modelisation(self):
        '''fct qui gere le tableau de modelisation'''        
        
        nbr_ligne_tableau_modelisation = int(self.tableWidget_modelisation.rowCount())
        resolution = self.lineEdit_resolution.text()
        if nbr_ligne_tableau_modelisation != 0:
            for i in range(nbr_ligne_tableau_modelisation):
                self.tableWidget_modelisation.removeRow(0)
        
        
        nbr_ligne = self.tableWidget_table_etalonnage.rowCount()

        list_Tlue = []
        list_correction = []
        list_ordre_apparition = []
        list_etalon_corrige = []
        list_incertitude = []
        
        for i in range(nbr_ligne):
            list_ordre_apparition.append(int(self.tableWidget_table_etalonnage.item(i, 0).text().replace(",", ".")))
            list_etalon_corrige.append(float(self.tableWidget_table_etalonnage.item(i, 1).text().replace(",", ".")))
            list_Tlue.append(float(self.tableWidget_table_etalonnage.item(i, 2).text().replace(",", ".")))
            list_correction.append(float(self.tableWidget_table_etalonnage.item(i, 3).text().replace(",", ".")))
            list_incertitude.append(float(self.tableWidget_table_etalonnage.item(i, 5).text().replace(",", ".")))
            
        nbr_poly = self.tableWidget_polynome.rowCount()        
        ordre = int(self.tableWidget_polynome.item(nbr_poly-1,0 ).text())
        
        #gestion donnees polynome
        correction_modelisee = []
        residu = []
        recouvrement = []
        
        if ordre > 1:
            a = float(self.tableWidget_polynome.item(nbr_poly-1,1 ).text().replace(",", "."))
            b = float(self.tableWidget_polynome.item(nbr_poly-1,2 ).text().replace(",", "."))
            c = float(self.tableWidget_polynome.item(nbr_poly-1,3 ).text().replace(",", "."))
            
            i=0
            for ele in list_Tlue:
                correction_modelisee.append(a*ele*ele + b*ele + c)
                residu.append(list_correction[i]-correction_modelisee[i])
                
                resolution_str = str(resolution.replace(",", "."))
                incertitude_str = str(list_incertitude[i])
                valeur_U_arrondie = decimal.Decimal(incertitude_str).quantize(decimal.Decimal(resolution_str), rounding=decimal.ROUND_UP)
                if float(valeur_U_arrondie) - np.abs(residu[i]) >= 0:
                    recouvrement.append("Conforme")
                else:
                    recouvrement.append("Non Conforme")
                i+=1
                
        else:
            a = float(self.tableWidget_polynome.item(nbr_poly-1,1 ).text().replace(",", "."))
            b = float(self.tableWidget_polynome.item(nbr_poly-1,2 ).text().replace(",", "."))
            
            i=0
            for ele in list_Tlue:                
                correction_modelisee.append(a*float(ele) + b)
                residu.append(list_correction[i]-correction_modelisee[i])
                
                resolution_str = str(resolution.replace(",", "."))
                incertitude_str = str(list_incertitude[i])
                valeur_U_arrondie = decimal.Decimal(incertitude_str).quantize(decimal.Decimal(resolution_str), rounding=decimal.ROUND_UP)
                
                if float(valeur_U_arrondie) - np.abs(residu[i]) >= 0:                
                    recouvrement.append("Conforme")
                else:
                    recouvrement.append("Non Conforme")
                i+=1
        
        
        i=0
        for ele in correction_modelisee:
            self.tableWidget_modelisation.insertRow(i)  
                
            self.tableWidget_modelisation.setItem(i, 0, QtGui.QTableWidgetItem(str(list_ordre_apparition[i])))
            self.tableWidget_modelisation.setItem(i, 1, QtGui.QTableWidgetItem(str(list_etalon_corrige[i])))
            self.tableWidget_modelisation.setItem(i, 2, QtGui.QTableWidgetItem(str(list_Tlue[i])))
            self.tableWidget_modelisation.setItem(i, 3, QtGui.QTableWidgetItem(str(list_correction[i])))
            self.tableWidget_modelisation.setItem(i, 4, QtGui.QTableWidgetItem(str(list_incertitude[i])))
            self.tableWidget_modelisation.setItem(i, 5, QtGui.QTableWidgetItem(str(correction_modelisee[i]))            )
            self.tableWidget_modelisation.setItem(i, 6, QtGui.QTableWidgetItem(str(residu[i])))
            self.tableWidget_modelisation.setItem(i, 7, QtGui.QTableWidgetItem(str(recouvrement[i])))
            i+=1
            
        # gestion incertitude max , residu max,....
        
        incertitude_max = np.amax(list_incertitude)
        self.lineEdit_incertitude_max_etal.setText(str(incertitude_max))
        
        residu_max = np.amax(np.abs(residu))
        self.lineEdit_residu_max.setText(str(residu_max))
        
        incertitude_modelisation = residu_max / np.sqrt(3)
        self.lineEdit_incertitude_modelisation.setText(str(incertitude_modelisation))
        
        ecartype_residu = np.std(residu, ddof=1)
        self.lineEdit_ecartype_residus.setText(str(ecartype_residu))
        
        #recherche incertitude par rapport residu max
        abs_residu = list(np.abs(residu))
        index_residu_max = abs_residu.index(residu_max)
        incertitude_residu_max = list_incertitude[index_residu_max]
        self.lineEdit_incertitude_residu_max.setText(str(incertitude_residu_max))
        
        #normalite
        test = sp.shapiro(residu)
        if test[1] > 0.05:
            normalite = "Hypothese de normalite non rejetee"
        else:
            normalite = "Hypothese rejetee"
        self.lineEdit_normalite_residus.setText(normalite)
        
        
    def clear_all(self):
        '''fct qui efface tous les widgets'''
        
        #gestion des tableaux
        
        nbr_ligne_tableau_modelisation = int(self.tableWidget_modelisation.rowCount())             
        if nbr_ligne_tableau_modelisation != 0:
            for i in range(nbr_ligne_tableau_modelisation):
                self.tableWidget_modelisation.removeRow(0)
        
        nbr_ligne_tableau_etal= int(self.tableWidget_table_etalonnage.rowCount())
        if nbr_ligne_tableau_etal !=0:
            for i in range(nbr_ligne_tableau_etal):
                self.tableWidget_table_etalonnage.removeRow(0)
                
        nbr_ligne_tableau_poly= int(self.tableWidget_polynome.rowCount())
        if nbr_ligne_tableau_poly !=1: #:reste une ligne juste nettoyer les cases
            for i in range(nbr_ligne_tableau_poly):
                self.tableWidget_polynome.removeRow(1)
            self.tableWidget_polynome.clearContents()
        else:
            self.tableWidget_polynome.clearContents()
            
        #gestion qedit
        self.dateEdit.clear()
        self.textEdit_constructeur.clear()
        self.textEdit_n_serie.clear()
        self.textEdit_model.clear()
        self.lineEdit_incertitude_max_etal.clear()
        self.lineEdit_residu_max.clear()
        self.lineEdit_incertitude_residu_max.clear()
        self.lineEdit_ecartype_residus.clear()
        self.lineEdit_normalite_residus.clear()
        self.lineEdit_incertitude_modelisation.clear()
    
    def clear_onglet_2(self):
        '''fct qui efface le deuxime onglet'''
        
        #gestion graph
        self.clear_plot()
        
        #gestion de tableau       
        nbr_ligne_tableau_modelisation = int(self.tableWidget_modelisation.rowCount())             
        if nbr_ligne_tableau_modelisation != 0:
            for i in range(nbr_ligne_tableau_modelisation):
                self.tableWidget_modelisation.removeRow(0)
                
        #gestion qedit
        self.lineEdit_incertitude_max_etal.clear()
        self.lineEdit_residu_max.clear()
        self.lineEdit_incertitude_residu_max.clear()
        self.lineEdit_ecartype_residus.clear()
        self.lineEdit_normalite_residus.clear()
        self.lineEdit_incertitude_modelisation.clear()
    
    def clear_plot(self):
        ''' fct pour effacer graph'''

        self.x_array = []
        self.y_array = []
        self.y_modelise = []
  
        self.curve.setData(self.x_array,self.y_array)
        self.curve_2.setData(self.x_array,self.y_array)

        self.qwtPlot.replot()
    
    @pyqtSlot()
    def on_button_actualise_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        self.clear_plot()
        new_poly = self.calcul_polynome()
        self.courbe_polynome()
        self.gestion_tableWidget_modelisation()
        
        if self.radioButton_modification.isChecked():
            self.actionMise_jour.setEnabled(True)
        else:
            self.actionEnregistrer.setEnabled(True)
    
    @pyqtSlot()
    def on_actionMise_jour_triggered(self):
        """
            fct qui fait la mise a jour de la bdd        """
            
        identification = self.comboBox_identification.currentText()
        n_ce = self.comboBox_n_ce.currentText()
        
        etat_polynome = self.comboBox_etat_polynome.currentText()
        if etat_polynome =="Archivé":
            booleen = True
        else:
            booleen = False        
       
        nbr_poly = self.tableWidget_polynome.rowCount()        
        ordre = int(self.tableWidget_polynome.item(nbr_poly-1,0 ).text().replace(",", "."))        
          
        if ordre > 1:
            a = float(self.tableWidget_polynome.item(nbr_poly-1,1 ).text().replace(",", "."))
            b = float(self.tableWidget_polynome.item(nbr_poly-1,2 ).text().replace(",", "."))
            c = float(self.tableWidget_polynome.item(nbr_poly-1,3 ).text().replace(",", "."))
                
        else:
            a = float(self.tableWidget_polynome.item(nbr_poly-1,1 ).text().replace(",", "."))
            b = float(self.tableWidget_polynome.item(nbr_poly-1,2 ).text().replace(",", "."))
            c = 0

        date = self.dateEdit.date()
        date_etal = date.toString('yyyy-MM-dd')
        
        valeurs_saisie = {
        "DATE_ETAL":date_etal, "ARCHIVAGE": booleen, "ORDRE_POLY": ordre, "COEFF_A":a, "COEFF_B":b, "COEFF_C":c}

        self.db. update_table_polynome(identification,  n_ce, valeurs_saisie)
        
        "mise à jour s'il y a lieu table polynome_table etal"
        
        n_ce = self.comboBox_n_ce.currentText()
        caract_poly = self.db.renvoie_caracteristique_poly_n_ce(n_ce)
        id_poly = caract_poly[6] #caract_poly[6] id_poly
        
        #Donnees d'etalonnage
        donnee_table_poly = self.db.recuperation_donnees_table_polynome_table_etalonnage(id_poly) #caract_poly[6] id_poly
        
        if donnee_table_poly:            
            self.db.delete_table_polynome_table_etalonnage(id_poly)
            
            #recuperation des donnees tableau etalonnage  :
            nbr_ligne_tableau_etal = int(self.tableWidget_table_etalonnage.rowCount())
            saisie_tableau_etal = [] 
        
            for i in range (nbr_ligne_tableau_etal):
                ligne_saisie = {}
    
                ligne_saisie["ORDRE_APPARITION"] = self.tableWidget_table_etalonnage.item(i, 0).text().replace(",", ".")
                ligne_saisie["MOYENNE_ETALON_CORRI"] = self.tableWidget_table_etalonnage.item(i, 1).text().replace(",", ".")
                ligne_saisie["MOYENNE_INSTRUM"] = self.tableWidget_table_etalonnage.item(i, 2).text().replace(",", ".")
                ligne_saisie["CORRECTION"] = self.tableWidget_table_etalonnage.item(i, 3).text().replace(",", ".")
                ligne_saisie["ERREUR"] = self.tableWidget_table_etalonnage.item(i, 4).text().replace(",", ".")
                ligne_saisie["INCERTITUDE"] = self.tableWidget_table_etalonnage.item(i, 5).text().replace(",", ".")
                ligne_saisie["ID_POLYNOME"] = id_poly
                saisie_tableau_etal.append(ligne_saisie)

            self.db.insert_polynome_table_etalonnage(saisie_tableau_etal)

        else:
                        #recuperation des donnees tableau etalonnage  :
            nbr_ligne_tableau_etal = int(self.tableWidget_table_etalonnage.rowCount())
            saisie_tableau_etal = [] 
        
            for i in range (nbr_ligne_tableau_etal):
                ligne_saisie = {}
    
                ligne_saisie["ORDRE_APPARITION"] = self.tableWidget_table_etalonnage.item(i, 0).text().replace(",", ".")
                ligne_saisie["MOYENNE_ETALON_CORRI"] = self.tableWidget_table_etalonnage.item(i, 1).text().replace(",", ".")
                ligne_saisie["MOYENNE_INSTRUM"] = self.tableWidget_table_etalonnage.item(i, 2).text().replace(",", ".")
                ligne_saisie["CORRECTION"] = self.tableWidget_table_etalonnage.item(i, 3).text().replace(",", ".")
                ligne_saisie["ERREUR"] = self.tableWidget_table_etalonnage.item(i, 4).text().replace(",", ".")
                ligne_saisie["INCERTITUDE"] = self.tableWidget_table_etalonnage.item(i, 5).text().replace(",", ".")
                ligne_saisie["ID_POLYNOME"] = id_poly
                saisie_tableau_etal.append(ligne_saisie)

            self.db.insert_polynome_table_etalonnage(saisie_tableau_etal)
        
        
        self.clear_all()
        self.comboBox_n_ce.clear()
        self.comboBox_identification.clear()
        self.clear_plot()
    
    @pyqtSlot()
    def on_actionEnregistrer_triggered(self):
       
        """
        fct qui fait l'enregistrement dans la bdd        """
            
        identification = self.comboBox_identification.currentText()
        n_ce = self.comboBox_n_ce.currentText()
        
        etat_polynome = self.comboBox_etat_polynome.currentText()
        if etat_polynome =="Archivé":
            booleen = True
        else:
            booleen = False
        
       
        nbr_poly = self.tableWidget_polynome.rowCount()        
        ordre = int(self.tableWidget_polynome.item(nbr_poly-1,0 ).text().replace(",", "."))        
          
        if ordre > 1:
            a = float(self.tableWidget_polynome.item(nbr_poly-1,1 ).text().replace(",", "."))
            b = float(self.tableWidget_polynome.item(nbr_poly-1,2 ).text().replace(",", "."))
            c = float(self.tableWidget_polynome.item(nbr_poly-1,3 ).text().replace(",", "."))                
        else:
            a = float(self.tableWidget_polynome.item(nbr_poly-1,1 ).text().replace(",", "."))
            b = float(self.tableWidget_polynome.item(nbr_poly-1,2 ).text().replace(",", "."))
            c = 0

        date = self.dateEdit.date()
        date_etal = date.toString('yyyy-MM-dd')        
        creation_poly = datetime.today().strftime('%d-%m-%y')        
        
        valeurs_saisie = { "DATE_ETAL": date_etal, "ARCHIVAGE": booleen, "ORDRE_POLY": ordre, "COEFF_A": a, 
                                    "COEFF_B": b, "COEFF_C": c, "DATE_CREATION_POLY": creation_poly, 
                                    "IDENTIFICATION": identification, "NUM_CERTIFICAT": n_ce}
        
        id_inserre = self.db.insert_table_polynome(valeurs_saisie)
        
        #recuperation des donnees tableau etalonnage  :
        nbr_ligne_tableau_etal = int(self.tableWidget_table_etalonnage.rowCount())
        saisie_tableau_etal = [] 
        
        for i in range (nbr_ligne_tableau_etal):
            ligne_saisie = {}

            ligne_saisie["ORDRE_APPARITION"] = self.tableWidget_table_etalonnage.item(i, 0).text().replace(",", ".")
            ligne_saisie["MOYENNE_ETALON_CORRI"] = self.tableWidget_table_etalonnage.item(i, 1).text().replace(",", ".")
            ligne_saisie["MOYENNE_INSTRUM"] = self.tableWidget_table_etalonnage.item(i, 2).text().replace(",", ".")
            ligne_saisie["CORRECTION"] = self.tableWidget_table_etalonnage.item(i, 3).text().replace(",", ".")
            ligne_saisie["ERREUR"] = self.tableWidget_table_etalonnage.item(i, 4).text().replace(",", ".")
            ligne_saisie["INCERTITUDE"] = self.tableWidget_table_etalonnage.item(i, 5).text().replace(",", ".")
            ligne_saisie["ID_POLYNOME"] = id_inserre[0]
            saisie_tableau_etal.append(ligne_saisie)

        self.db.insert_polynome_table_etalonnage(saisie_tableau_etal)

        
        self.clear_all()
        self.comboBox_n_ce.clear()
        self.comboBox_identification.clear()
        self.clear_plot()
