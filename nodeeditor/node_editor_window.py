import json
import os

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QLabel, QApplication

from nodeeditor.node_editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.filename = None

        self.initUI()




    def createActions(self, name, shortcut, tooltip, callback):
        action = QAction(name, self)
        action.setShortcut(shortcut)
        action.setStatusTip(tooltip)
        action.triggered.connect(callback)
        return action

    def initUI(self):
        menubar = self.menuBar()
        # initialize Menu

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.createActions('&New', 'Ctrl+N', 'New file', self.newFile))
        fileMenu.addAction(self.createActions('&Open', 'Ctrl+O', 'Open file', self.openFile))
        fileMenu.addAction(self.createActions('&Save', 'Ctrl+S', 'Save file', self.saveFile))
        fileMenu.addAction(self.createActions('Save &As', 'Ctrl+Shift+S', 'Save file as', self.saveAsFile))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createActions('&Exit', 'Ctrl+Q', 'Exit application', self.close))

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.createActions('&Undo', 'Ctrl+Z', 'Undo', self.editUndo) )
        editMenu.addAction(self.createActions('&Redo', 'Ctrl+Y', 'Redo', self.editRedo) )
        editMenu.addSeparator()
        editMenu.addAction(self.createActions('&Cut', 'Ctrl+X', 'Cut', self.editCut) )
        editMenu.addAction(self.createActions('&Copy', 'Ctrl+C', 'Copy', self.editCopy) )
        editMenu.addAction(self.createActions('&Paste', 'Ctrl+V', 'Paste', self.editPaste) )
        editMenu.addSeparator()
        editMenu.addAction(self.createActions('&Select All', 'Ctrl+A', 'Select all', self.passed) )
        editMenu.addSeparator()
        editMenu.addAction(self.createActions('&Delete', 'Del', 'Delete', self.editDelete) )
        editMenu.addSeparator()
        editMenu.addAction(self.createActions('&Settings', 'Ctrl+P', 'Settings', self.passed) )
        editMenu.addSeparator()
        editMenu.addAction(self.createActions('&Run', 'F5', 'Run', self.passed) )
        editMenu.addAction(self.createActions('&Run Selected', 'F6', 'Run selected', self.passed) )
        editMenu.addAction(self.createActions('&Run All', 'F7', 'Run all', self.passed) )
        editMenu.addSeparator()
        editMenu.addAction(self.createActions('&Clear Console', 'Ctrl+L', 'Clear console', self.passed) )
        editMenu.addSeparator()
        editMenu.addAction(self.createActions('&Check for Errors', 'F8', 'Check for errors', self.passed) )
        editMenu.addSeparator()
        editMenu.addAction(self.createActions('&Check for Warnings', 'F9', 'Check for warnings', self.passed) )

        viewMenu = menubar.addMenu('&View')
        helpMenu = menubar.addMenu('&Help')

        nodeeditor = NodeEditorWidget(self)
        nodeeditor.scene.addHasBeenModifiedListener(self.changeTitle)
        self.setCentralWidget(nodeeditor)

        # status bar
        self.statusBar().showMessage("Ready", 2000)
        self.status_mouse_bar = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_bar)
        nodeeditor.view.scenePosChanged.connect(self.scenePosChanged)
        # self.statusBar().setStyleSheet("QStatusBar{background-color: #333333;}")
        self.statusBar().setSizeGripEnabled(False)




        # Set window properties
        self.setGeometry(1600, 500, 800, 600)
        self.changeTitle()
        self.show()

    def changeTitle(self):
        title = 'Node Editor - '
        if self.filename is None:
            title += 'New graph'
        else:
            title += os.path.basename(self.filename)

        if self.centralWidget().scene.has_been_modified:
            title += '*'

        self.setWindowTitle(title)

    def scenePosChanged(self, x, y):
        self.status_mouse_bar.setText("Scene Pos: (%d, %d)" % (x, y))

    def newFile(self):
        if self.maybeSave():
            self.centralWidget().scene.clear()
            self.filename = None
            self.changeTitle()
            self.statusBar().showMessage("New graph created", 2000)


    def openFile(self):
        if self.maybeSave():
            fname, filter = QFileDialog.getOpenFileName(self, 'Open file', '../')
            if fname == '':
                return
            if os.path.isfile(fname):
                self.centralWidget().scene.loadFromFile(fname)
                self.filename = fname
                self.changeTitle()
                self.statusBar().showMessage("File loaded from " + self.filename, 2000)

    def saveFile(self):
        if self.filename is None: return self.saveAsFile()
        self.centralWidget().scene.saveToFile(self.filename)
        self.changeTitle()
        self.statusBar().showMessage("Saved to " + self.filename, 2000)
        return True

    def saveAsFile(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'Save file', '../')
        if fname == '':
            return False
        self.filename = fname
        self.saveFile()
        return True

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

        # reply = QMessageBox.question(self, 'Message',
        #                              "Are you sure to quit?", QMessageBox.Yes |
        #                              QMessageBox.No, QMessageBox.No)
        # if reply == QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()
    def isModified(self):
        return self.centralWidget().scene.has_been_modified

    def maybeSave(self):
        if not self.isModified():
            return True

        reply = QMessageBox.question(self, 'Are you sure to quit?',
                                     "The document has been modified\nDo want to save your changes?",
                                     QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save )
        if reply == QMessageBox.Save:
            return self.saveFile()
        elif reply == QMessageBox.Cancel:
            return False

        return True

    def editUndo(self):
        self.centralWidget().scene.history.undo()
        self.statusBar().showMessage("Undo", 2000)

    def editRedo(self):
        self.centralWidget().scene.history.redo()
        self.statusBar().showMessage("Redo", 2000)

    def editDelete(self):
        self.centralWidget().scene.grScene.views()[0].deleteSelected()
        self.statusBar().showMessage("Delete", 2000)

    def editCut(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=True)
        str_data = json.dumps(data, indent=4)
        QApplication.clipboard().setText(str_data)
        self.statusBar().showMessage("Cut", 2000)

    def editCopy(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=False)
        str_data = json.dumps(data, indent=4)
        QApplication.clipboard().setText(str_data)
        self.statusBar().showMessage("Copy", 2000)

    def editPaste(self):
        raw_data = QApplication.instance().clipboard().text()
        try:
            data = json.loads(raw_data)
        except ValueError as e:
            print("Pasting of non-valid JSON data has been denied.", e)
            return

        # check if the JSON data are correct
        if 'nodes' not in data:
            print("JSON does not contain any nodes!")
            return

        self.centralWidget().scene.clipboard.deserializeFromClipboard(data)
        self.statusBar().showMessage("Pasted", 2000)

    def passed(self):
        pass



