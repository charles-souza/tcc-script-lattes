#!/usr/bin/python
# encoding: utf-8
#
#  GUI/Windows version
#  Copyright 2014: Roberto Faga Jr
#
#  http://github.com/rfaga/scriptlattesgui
#
#
#  Este programa é um software livre; você pode redistribui-lo e/ou
#  modifica-lo dentro dos termos da Licença Pública Geral GNU como
#  publicada pela Fundação do Software Livre (FSF); na versão 2 da
#  Licença, ou (na sua opinião) qualquer versão.
#
#  Este programa é distribuído na esperança que possa ser util,
#  mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUAÇÂO a qualquer
#  MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
#  Licença Pública Geral GNU para maiores detalhes.
#
#  Você deve ter recebido uma cópia da Licença Pública Geral GNU
#  junto com este programa, se não, escreva para a Fundação do Software
#  Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import sys
from PySide import QtCore, QtGui

import os
import re
import string

from base_panel import BasePanel

class MultiProcessingTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, data_list, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.data_list = data_list
        self.header = header
        
    def rowCount(self, parent):
        return len(self.data_list)
    def columnCount(self, parent):
        return len(self.data_list[0])
    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.data_list[index.row()][index.column()]
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None
    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.data_list = sorted(self.data_list,
            key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.data_list.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))

def finished_signal_factory(panel, index, process):
    def finished():
        try:
            output = str(process.readAllStandardOutput())
        except:
            output = "Error capturing output"
        try:
            errors = str(process.readAllStandardError())
        except:
            errors = "Error capturing output"
        results = re.findall(r"\>\'.*?\'\<", output)
        output_folder = ''
        if results:
            output_folder = unicode(results[0][2:-2] + os.sep)
            o = file(os.path.join(output_folder, 'saida.txt'), 'w')
            o.write(output)
            o.close()
            e = file(os.path.join(output_folder, 'erros.txt'), 'w')
            e.write(errors)
            e.close()
        panel.finish_process(index, output_folder, errors.strip())
    return finished


class MultipleProcessingTabPanel(BasePanel):
    def __init__(self, parent):
        super(MultipleProcessingTabPanel, self).__init__(parent)
        
        self.ui.multipleExecute.clicked.connect(self.run)
        self.ui.folderchooser.clicked.connect(self.choose_folder)
        last_folder = self.settings.value('lastFolder', None)
        self.results = {}
        if last_folder:
            self.ui.input_multiple.setPlainText(last_folder)
            self.make_list()
        self.ui.tableWidget.cellClicked.connect(self.cell_clicked)

    
    def open_link(self, folder):
        path = folder +  'index.html'
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(path, QtCore.QUrl.TolerantMode))
    
    def open_folder(self, folder):
        path = folder
        QtGui.QDesktopServices.openUrl(path)
    
    def cell_clicked(self, row, column):
        if self.results.get(row, False):
            if column == 2:
                self.open_folder(self.results[row])
            elif column == 3:
                self.open_link(self.results[row])
        
    
    def choose_folder(self):
        last_folder = self.settings.value('lastFolder', '.')
        folderpath = QtGui.QFileDialog.getExistingDirectory(self.parent,
            "Abrir pasta com configs", last_folder)
        self.settings.setValue('lastFolder',  folderpath)
        self.ui.input_multiple.setPlainText(folderpath)
        self.make_list()
        
    def make_list(self):
        folderpath = self.ui.input_multiple.toPlainText()
        file_list = []
        for root, subfolders, files in os.walk(folderpath):
            for file in files:
                if ".config" in file: 
                    file_list.append(os.path.join(root,file))
        self.file_list = file_list
        self.file_list.sort()
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setRowCount(len(self.file_list))
        self.ui.tableWidget.setColumnCount(4)
        for index, f in enumerate(self.file_list):
            self.ui.tableWidget.setItem(index, 0, QtGui.QTableWidgetItem(
                f
            ))
            self.ui.tableWidget.setItem(index, 1, QtGui.QTableWidgetItem(
                u"Não executado"
            ))
        
        hheader = QtGui.QHeaderView(QtCore.Qt.Orientation.Horizontal)
        hheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.ui.tableWidget.setHorizontalHeader(hheader)
        self.ui.tableWidget.setHorizontalHeaderLabels(
            ['Arquivo Config', 'Estado', 'Resultado Pasta', 'Resultado Browser']
        )
        
        return
        
    def run(self):
        self.ui.multipleExecute.setDisabled(True)
        self.ui.runner.setText('Aguarde, processando...')
        self.ui.statusbar.showMessage('Aguarde, processando...')
        self.processes = [(i, f) for i,f in enumerate(self.file_list)]
        self.results = {}
        for i in range(4):
            self.run_process()

    def run_process(self):
        if not self.processes:
            return None
        index, filepath = self.processes.pop(0)
        self.ui.tableWidget.setItem(index, 1, QtGui.QTableWidgetItem("Processando..."))
        process = QtCore.QProcess(self.parent)
        process.finished.connect(finished_signal_factory(self, index, process))
        process.start(self.parent.CMD,[filepath])
    
    def finish_process(self, index, output_folder, errors):
        self.results[index] = output_folder
        if errors:
            self.ui.tableWidget.setItem(index, 1, QtGui.QTableWidgetItem("ERRO"))
        else:
            self.ui.tableWidget.setItem(index, 1, QtGui.QTableWidgetItem("Finalizado!"))
        if output_folder:
            self.ui.tableWidget.setItem(index, 2, QtGui.QTableWidgetItem("Abrir"))
            self.ui.tableWidget.setItem(index, 3, QtGui.QTableWidgetItem("Abrir"))
        #open_folder = QtGui.QTableWidgetItem("Abrir Pasta")
        #self.ui.tableWidget.itemClicked()
        #self.ui.tableWidget.setItem(index, 2, open_folder)
        if len(self.processes) == 0:
            self.ui.multipleExecute.setDisabled(False)
            self.ui.runner.setText('Executar lote')
            self.ui.statusbar.showMessage('Tudo finalizado!') 
        else:
            self.run_process()
    