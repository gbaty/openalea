
import weakref
from openalea.vpltk.qt import QtGui, QtCore
from openalea.oalab.service.applet import new_applet
from openalea.oalab.gui.splitterui import SplittableUI
from openalea.core.plugin.manager import PluginManager
from openalea.oalab.gui.utils import qicon


def obj_icon(obj):
    if hasattr(obj, 'icon'):
        return qicon(obj.icon)
    else:
        return qicon('Crystal_Clear_action_edit_add.png')


class AppletSelector(QtGui.QWidget):

    appletChanged = QtCore.Signal(str)
    addTabClicked = QtCore.Signal()
    removeTabClicked = QtCore.Signal()

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self._layout = QtGui.QHBoxLayout(self)

        self._cb_applets = QtGui.QComboBox()
        self._cb_applets.currentIndexChanged.connect(self._on_current_applet_changed)

        self._pb_new_tab = QtGui.QPushButton('+')
        self._pb_new_tab.clicked.connect(self.addTabClicked)

        self._applet_plugins = []

        self.pm = PluginManager()
        for plugin_class in self.pm.plugins('oalab.applet'):
            self._applet_plugins.append(plugin_class)
            self._cb_applets.addItem(obj_icon(plugin_class), plugin_class.alias)

        self._layout.addWidget(self._cb_applets)
        self._layout.addWidget(self._pb_new_tab)

    def _on_current_applet_changed(self, idx):
        applet_name = self.applet(idx)
        if applet_name:
            self.appletChanged.emit(applet_name)

    def applet(self, idx):
        if 0 <= idx <= len(self._applet_plugins):
            plugin_class = self._applet_plugins[idx]
            return plugin_class.name
        else:
            return None

    def currentApplet(self):
        return self.applet(self._cb_applets.currentIndex())

    def setCurrentApplet(self, name):
        for i, plugin_class in enumerate(self._applet_plugins):
            if plugin_class.name == name:
                self._cb_applets.setCurrentIndex(i)
                break


class AppletTabWidget(QtGui.QTabWidget):

    def __init__(self):
        QtGui.QTabWidget.__init__(self)
        self._applets = {}
        self._name = {}
        self._current = None

    def tabInserted(self, index):
        self.tabBar().setVisible(self.count() > 1)

    def tabRemoved(self, index):
        self.tabBar().setVisible(self.count() > 1)

    def new_tab(self):
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(widget)
        self.addTab(widget, 'TAB')

    def remove_tab(self):
        pass

    def set_applet(self, name):
        # clear view

        idx = self.currentIndex()
        for applet in self._applets.get(idx, {}).values():
            applet.hide()

        if name in self._name.get(idx, {}):
            applet = self._applets[idx][name]
            applet.show()
        else:
            applet = pm.new('oalab.applet', name)
            tab = self.currentWidget()
            tab.layout().addWidget(applet)
            self._applets.setdefault(idx, {})[name] = applet
            self._name[idx] = name

        plugin_class = pm.plugin('oalab.applet', name)
        self.setTabText(idx, plugin_class.alias)
        self.setTabIcon(idx, obj_icon(plugin_class))

    def currentApplet(self):
        try:
            return self._name[self.currentIndex()]
        except KeyError:
            return None


class AppletContainer(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, None)

        self._layout = QtGui.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)

        self._tabwidget = AppletTabWidget()
        self._tabwidget.currentChanged.connect(self._on_tab_changed)

        self._applet_selector = AppletSelector()
        self._applet_selector.appletChanged.connect(self._tabwidget.set_applet)
        self._applet_selector.addTabClicked.connect(self._tabwidget.new_tab)
        self._applet_selector.removeTabClicked.connect(self._tabwidget.remove_tab)

        self._layout.addWidget(self._tabwidget)
        self._layout.addWidget(self._applet_selector)

        self._tabwidget.new_tab()

        applet_name = self._applet_selector.currentApplet()
        if applet_name:
            self._tabwidget.set_applet(applet_name)

    def _on_tab_changed(self, idx):
        applet_name = self._tabwidget.currentApplet()
        if applet_name:
            self._applet_selector.setCurrentApplet(applet_name)


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
