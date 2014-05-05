#!/usr/bin/python
# encoding: utf-8
#
#  GUI/Windows version
#  Copyright 2014: Roberto Faga Jr e Dorival Piedade Neto
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
from gui.main_window import Ui_MainWindow

import os
import re
import string

# definir executavel do scriptLattes
if 'win' in sys.platform.lower():
    CMD = 'scriptLattes.exe'
else:
    CMD = './scriptLattes.py'

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

class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.settings = QtCore.QSettings()
        self.ui =  Ui_MainWindow()
        self.ui.setupUi(self)
        #self.print_text('Aguardando entrada de dados...')
        self.ui.filechooser.clicked.connect(self.choose_file)
        self.ui.runner.clicked.connect(self.run)
        self.ui.openLink.clicked.connect(self.open_link)
        self.ui.openFolder.clicked.connect(self.open_folder)
        self.setWindowIcon(QtGui.QIcon('logo.png'))

        last_file = self.settings.value('lastFile', None)
        if last_file:
            self.ui.input.setPlainText(last_file)
            
        self.ui.tableView.setModel(MultiProcessingTableModel(self, [('/path/1', u'Não executado', ''), ('/path/2', u'Não executado', '')]*30, ['Arquivo Config', 'Estado', 'Resultado']))
        self.ui.tableView.resizeColumnsToContents()

        #self.output_folder = '/tmp/teste-01/'
        #self.output_folder = u'C:\\a paça\\exemplo\\teste-01\\'
        #self.ui.resultsWidget.setDisabled(False)

    def print_text(self):
        try:
            s = str(self.process.readAllStandardOutput())
        except:
            s = ""
        try:
            self.ui.out.insertPlainText( s )
        except:
            print_error("(String não capturada)")

    def print_error(self):
        s = str(self.process.readAllStandardError())
        msg = "<br><p style='color: red; font-weight: bold'>%s</p>" % s.replace('\n', '<br>')
        self.ui.errors.insertHtml(msg)

    def clearOutputs(self):
        self.ui.out.setPlainText('');
        self.ui.errors.setPlainText('');
        self.ui.statusbar.clearMessage()
    
    def get_output_folder(self):
        if 'win' in sys.platform.lower():
            return 'file:///' + self.output_folder.replace('\\', '/')
        else:
            return 'file://' + self.output_folder
    
    def open_link(self):
        path = self.get_output_folder() +  'index.html'
        print path
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(path, QtCore.QUrl.TolerantMode))
    
    def open_folder(self):
        path = self.get_output_folder()
        QtGui.QDesktopServices.openUrl(path)
    
    def run(self):
        self.clearOutputs()
        self.ui.resultsWidget.setDisabled(True)
        
        self.current_file = self.ui.input.toPlainText()
        
        self.ui.runner.setDisabled(True)
        self.ui.runner.setText('Aguarde, processando...')
        self.ui.statusbar.showMessage('Aguarde, processando...')
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self.print_text)
        self.process.readyReadStandardError.connect(self.print_error)
        self.process.finished.connect(self.finished)
        self.process.start(CMD,[self.current_file])

    def choose_file(self):
        last_file = self.settings.value('lastFile', None)
        if last_file:
            folder = os.path.abspath(os.path.join(last_file, os.pardir))
        else:
            folder = '.'
        filename = QtGui.QFileDialog.getOpenFileName(self,
            "Open Image", folder, "Text files (*.config)")
        path = filename[0]
        self.settings.setValue('lastFile',  path)
        self.ui.input.setPlainText(path)


    def finished(self):
        self.ui.runner.setDisabled(False)
        self.ui.runner.setText('Executar')
        self.ui.statusbar.showMessage('Processo finalizado!')
        
        s = self.ui.out.toPlainText()
        # getting from output result folder
        results = re.findall(r"\>\'.*?\'\<", s)
        if results:
            self.output_folder = unicode(results[0][2:-2] + os.sep)
            self.ui.resultsWidget.setDisabled(False)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())
