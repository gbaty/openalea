
import weakref
from openalea.vpltk.qt import QtGui, QtCore
from openalea.oalab.service.applet import new_applet
from openalea.oalab.gui.splitterui import SplittableUI
from openalea.core.plugin.manager import PluginManager


class AppletContainer(QtGui.QTabWidget):

    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self, None)
#         self._layout = QtGui.QVBoxLayout(self)
        self._cb_applets = QtGui.QComboBox()
        self._cb_applets.currentIndexChanged.connect(self._on_current_applet_changed)

        self._applets = {}
        self._applet_plugins = []

        self._container = QtGui.QWidget()
        self._container_layout = QtGui.QVBoxLayout(self._container)

#         self.setContentsMargins(0, 0, 0, 0)
#         self._layout.setContentsMargins(0, 0, 0, 0)
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container_layout.setContentsMargins(0, 0, 0, 0)

        self.pm = PluginManager()
        for plugin_class in self.pm.plugins('oalab.applet'):
            self._applet_plugins.append(plugin_class)
            self._cb_applets.addItem(plugin_class.alias)

        self._container_layout.addWidget(self._cb_applets)

        self.addTab(self._container, 'Tab1')

#     def tabInserted(self, index):
#         self.tabBar().setVisible(self.count() > 1)
#
#     def tabRemoved(self, index):
#         self.tabBar().setVisible(self.count() > 1)

    def add_applet(self, widget_class, name, *args, **kwds):
        print 'add_applet', name, widget_class

    def _on_current_applet_changed(self, idx):
        if 0 <= idx <= len(self._applet_plugins):
            plugin_class = self._applet_plugins[idx]

            # clear view
            for widget in self._applets.values():
                widget.hide()

            if plugin_class in self._applets:
                widget = self._applets[plugin_class]
                widget.show()
            else:
                widget = pm.instance('oalab.applet', plugin_class.name)
                self._applets[plugin_class] = widget
                self._container_layout.insertWidget(0, widget)


class OALabSplittableUi(SplittableUI):

    def getPlaceHolder(self):
        return AppletContainer()

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        action = QtGui.QAction("Add tab", menu)
        menu.addAction(action)
        menu.exec_(event.globalPos())

if __name__ == '__main__':
    instance = QtGui.QApplication.instance()

    pm = PluginManager()
    #pm.debug = True

    if instance is None:
        app = QtGui.QApplication([])
    else:
        app = instance

    l = []
    for i in range(5):
        l.append(QtGui.QLabel(unicode(i)))

    mw = QtGui.QMainWindow()

    container = AppletContainer()
    splittable = OALabSplittableUi(parent=mw)
    splittable.setContentAt(0, container)
    mw.setCentralWidget(splittable)
    mw.show()

    if instance is None:
        app.exec_()
