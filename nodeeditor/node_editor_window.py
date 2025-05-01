import json
import os

from PySide6.QtCore import QSettings, QPoint, QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QLabel, QApplication

from nodeeditor.node_editor_widget import NodeEditorWidget
from nodeeditor.utils import pp


class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.name_company = 'Company Name'
        self.name_product = 'Node Editor'

        self.initUI()

    def initUI(self):
        # initialize Menu
        self.createActions()
        self.createMenus()

        self.nodeeditor = NodeEditorWidget(self)
        self.nodeeditor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.nodeeditor)

        # status bar
        self.createStatusBar()

        # Set window properties
        self.setGeometry(1600, 500, 800, 600)
        self.setTitle()
        self.show()

    def createStatusBar(self):
        self.statusBar().showMessage("Ready", 2000)
        self.status_mouse_bar = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_bar)
        self.nodeeditor.view.scenePosChanged.connect(self.scenePosChanged)
        self.statusBar().setSizeGripEnabled(False)

        # self.statusBar().setStyleSheet("QStatusBar{background-color: #333333;}")

    def createActions(self):
        self.actNew = QAction('&New', self, shortcut='Ctrl+N', statusTip='New file', triggered=self.onFileNew)
        self.actOpen = QAction('&Open', self, shortcut='Ctrl+O', statusTip='Open file', triggered=self.onFileOpen)
        self.actSave = QAction('&Save', self, shortcut='Ctrl+S', statusTip='Save file', triggered=self.onFileSave)
        self.actSaveAs = QAction('&Save As', self, shortcut='Ctrl+Shift+S', statusTip='Save file as', triggered=self.onFileSaveAs)
        self.actExit = QAction('&Exit', self, shortcut='Ctrl+Q', statusTip='Exit application', triggered=self.close)

        self.actUndo = QAction('&Undo', self, shortcut='Ctrl+Z', statusTip='Undo', triggered=self.editUndo)
        self.actRedo = QAction('&Redo', self, shortcut='Ctrl+Y', statusTip='Redo', triggered=self.editRedo)
        self.actCut = QAction('&Cut', self, shortcut='Ctrl+X', statusTip='Cut', triggered=self.editCut)
        self.actCopy = QAction('&Copy', self, shortcut='Ctrl+C', statusTip='Copy', triggered=self.editCopy)
        self.actPaste = QAction('&Paste', self, shortcut='Ctrl+V', statusTip='Paste', triggered=self.editPaste)
        self.actSelectAll = QAction('&Select All', self, shortcut='Ctrl+A', statusTip='Select all', triggered=self.passed)
        self.actDelete = QAction('&Delete', self, shortcut='Del', statusTip='Delete', triggered=self.editDelete)
        self.actSettings = QAction('&Settings', self, shortcut='Ctrl+P', statusTip='Settings', triggered=self.passed)
        self.actRun = QAction('&Run', self, shortcut='F5', statusTip='Run', triggered=self.passed)
        self.actRunAll = QAction('&Run All', self, shortcut='F6', statusTip='Run all', triggered=self.passed)
        self.actClearConsole = QAction('&Clear Console', self, shortcut='Ctrl+L', statusTip='Clear console', triggered=self.passed)
        self.actCheckForErrors = QAction('&Check for Errors', self, shortcut='F8', statusTip='Check for errors', triggered=self.passed)
        self.actCheckForWarnings = QAction('&Check for Warnings', self, shortcut='F9', statusTip='Check for warnings', triggered=self.passed)

    def createMenus(self):
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)

        self.editMenu = menubar.addMenu('&Edit')
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDelete)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actSelectAll)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actSettings)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actRun)
        self.editMenu.addAction(self.actRunAll)
        self.editMenu.addAction(self.actClearConsole)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCheckForErrors)
        self.editMenu.addAction(self.actCheckForWarnings)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actSettings)

        # self.viewMenu = menubar.addMenu('&View')
        # self.helpMenu = menubar.addMenu('&Help')


    def setTitle(self):
        title = 'Node Editor - '
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFileName()

        self.setWindowTitle(title)

    def closeEvent(self, event):
            if self.maybeSave():
                event.accept()
            else:
                event.ignore()

    def isModified(self):
        return self.getCurrentNodeEditorWidget().scene.isModified()

    def getCurrentNodeEditorWidget(self):
        return self.centralWidget()

    def maybeSave(self):
        if not self.isModified():
            return True

        reply = QMessageBox.question(self, 'Are you sure to quit?',
                                     "The document has been modified\nDo want to save your changes?",
                                     QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, QMessageBox.Save )
        if reply == QMessageBox.Save:
            return self.onFileSave()
        elif reply == QMessageBox.Cancel:
            return False

        return True

    def scenePosChanged(self, x, y):
        self.status_mouse_bar.setText("Scene Pos: (%d, %d)" % (x, y))

    def onFileNew(self):
        if self.maybeSave():
            self.getCurrentNodeEditorWidget().fileNew()
            self.setTitle()
            self.statusBar().showMessage("New graph created", 2000)


    def onFileOpen(self):
        if self.maybeSave():
            fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file')
            if fname != '' and os.path.isfile(fname):
                self.getCurrentNodeEditorWidget().fileLoad(fname)
                self.setTitle()
                self.statusBar().showMessage("File loaded from " + fname, 2000)

    def onFileSave(self):
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            if not current_nodeeditor.isFilenameSet(): return self.onFileSaveAs()

            current_nodeeditor.fileSave()
            self.statusBar().showMessage("Successfully saved %s" % current_nodeeditor.filename, 5000)

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()
            return True
        return None


    def onFileSaveAs(self):
        current_nodeeditor = self.getCurrentNodeEditorWidget()
        if current_nodeeditor is not None:
            fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file')
            if fname == '': return False

            current_nodeeditor.fileSave(fname)
            self.statusBar().showMessage("Successfully saved as %s" % current_nodeeditor.filename, 5000)

            # support for MDI app
            if hasattr(current_nodeeditor, "setTitle"):
                current_nodeeditor.setTitle()
            else:
                self.setTitle()
            return True
        return None



    def editUndo(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.undo()
            self.statusBar().showMessage("Undo", 2000)

    def editRedo(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.history.redo()
            self.statusBar().showMessage("Redo", 2000)

    def editDelete(self):
        if self.getCurrentNodeEditorWidget():
            self.getCurrentNodeEditorWidget().scene.grScene.views()[0].deleteSelected()
            self.statusBar().showMessage("Delete", 2000)

    def editCut(self):
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
            str_data = json.dumps(data, indent=4)
            QApplication.clipboard().setText(str_data)
            self.statusBar().showMessage("Cut", 2000)

    def editCopy(self):
        if self.getCurrentNodeEditorWidget():
            data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
            str_data = json.dumps(data, indent=4)
            QApplication.clipboard().setText(str_data)
            self.statusBar().showMessage("Copy", 2000)

    def editPaste(self):
        if self.getCurrentNodeEditorWidget():
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

        self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)
        self.statusBar().showMessage("Pasted", 2000)

    def passed(self):
        pass

    def readSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

