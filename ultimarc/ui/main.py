import sys
from PySide2 import QtCore, QtGui, QtQml

if __name__ == '__main__':

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtGui.QGuiApplication(sys.argv)
    engine = QtQml.QQmlApplicationEngine()
    url = QtCore.QUrl.fromLocalFile('main.qml')

    engine.load(url)
    if not engine.rootObjects():
        raise ValueError('bad')
        sys.exit(-1)

    sys.exit(app.exec_())
