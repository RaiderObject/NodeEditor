import traceback

from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4).pprint


def dumpException(e=None):
    """
    Prints out an Exception message with traceback to the console

    :param e: Exception to print out
    :type e: Exception
    """
    # print("%s EXCEPTION:" % e.__class__.__name__, e)
    # traceback.print_tb(e.__traceback__)
    traceback.print_exc()



def loadStylesheet(filename):
    print('STYLE loading:', filename)
    file = QFile(filename)
    file.open(QFile.ReadOnly | QFile.Text)
    stylesheet = file.readAll()
    QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))

def loadStylesheets(*args):
    res = ''
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        res += "\n" + str(stylesheet, encoding='utf-8')

    QApplication.instance().setStyleSheet(res)

