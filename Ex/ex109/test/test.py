import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

from Ex.ex109.ui.MyMainWindowEx import MyMainWindowEx

app = QApplication(sys.argv)
myui = MyMainWindowEx()
myui.setupUi(QMainWindow())
myui.show_window()
app.exec()
