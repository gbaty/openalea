

from openalea.vpltk.qt import QtGui, QtCore
from openalea.oalab.service.applet import new_applet
from openalea.oalab.gui.splitterui import SplittableUI

if __name__ == '__main__':
    instance = QtGui.QApplication.instance()
    if instance is None:
        app = QtGui.QApplication([])
    else:
        app = instance

    l = []
    for i in range(5):
        l.append(QtGui.QLabel(unicode(i)))

    tab = QtGui.QTabWidget()
    tab.addTab(l[1], '1')
    tab.addTab(l[2], '2')

    mw = QtGui.QMainWindow()
    splittable = SplittableUI(parent=mw)
    splittable.setContentAt(0, l[0])
    splittable.splitPane(tab, 0, QtCore.Qt.Horizontal, 0.8)
    mw.setCentralWidget(splittable)
    mw.show()

    if instance is None:
        app.exec_()
