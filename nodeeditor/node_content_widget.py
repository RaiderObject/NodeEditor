from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from collections import OrderedDict
from nodeeditor.node_serializable import Serializable

DEBUG = False

class QDMNodeContentWidget(QWidget, Serializable):
    def __init__(self, node, parent=None):
        self.node = node
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.wdg_label = QLabel("Some Title")
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QDMTextEdit("Some Text"))

    def setEditingFlag(self, value):
        self.node.scene.getView().editingFlag = value

    def serialize(self):
        return OrderedDict([

        ])

    def deserialize(self, data, hashmap={}):
        return True

''' set editing flag for key Delete '''
class QDMTextEdit(QTextEdit):
    def focusInEvent(self, event):
        print('FOCUS IN')
        self.parentWidget().setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        print('FOCUS OUT')
        self.parentWidget().setEditingFlag(False)
        super().focusOutEvent(event)
