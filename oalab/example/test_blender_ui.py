
import weakref
from openalea.vpltk.qt import QtGui, QtCore
from openalea.oalab.service.applet import new_applet
from openalea.oalab.gui.splitterui import SplittableUI, BinaryTree
from openalea.core.service.plugin import new_plugin_instance, plugin_instances, plugin_class, plugins
from openalea.oalab.gui.utils import qicon
import openalea.core


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
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QtGui.QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._cb_applets = QtGui.QComboBox()
        self._applet_plugins = []

        self._cb_applets.addItem('Select applet')
        for plugin_class in plugins('oalab.applet'):
            self._applet_plugins.append(plugin_class)
            self._cb_applets.addItem(obj_icon(plugin_class), plugin_class.alias)

        self._layout.addWidget(self._cb_applets)

        self.setCurrentApplet('')
        self._cb_applets.currentIndexChanged.connect(self._on_current_applet_changed)

    def _on_current_applet_changed(self, idx):
        """
        Called when selected applet changes.
        Emit signal appletChanged(name)
        name = '' if applet not found or "select applet"
        """
        applet_name = self.applet(idx)
        if applet_name:
            self.appletChanged.emit(applet_name)
        else:
            self.appletChanged.emit('')

    def applet(self, idx):
        if 1 <= idx <= len(self._applet_plugins):
            plugin_class = self._applet_plugins[idx - 1]
            return plugin_class.name
        else:
            return None

    def currentApplet(self):
        return self.applet(self._cb_applets.currentIndex())

    def setCurrentApplet(self, name):
        self._cb_applets.setCurrentIndex(0)
        for i, plugin_class in enumerate(self._applet_plugins):
            if plugin_class.name == name:
                self._cb_applets.setCurrentIndex(i + 1)
                break


class AppletTabWidget(QtGui.QTabWidget):

    def __init__(self):
        QtGui.QTabWidget.__init__(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.tabCloseRequested.connect(self.remove_tab)

        self._applets = {}
        self._name = {}
        self._current = None

    def tabInserted(self, index):
        self.tabBar().setVisible(self.count() > 1)

    def tabRemoved(self, index):
        self.tabBar().setVisible(self.count() > 1)

    def set_edit_mode(self, mode=True):
        self.setTabsClosable(mode)

    def new_tab(self):
        widget = QtGui.QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        layout = QtGui.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.addTab(widget, '')
        self.setCurrentWidget(widget)

    def remove_tab(self, idx):
        if idx in self._applets:
            for applet in self._applets[idx].values():
                applet.close()
                del applet
            self._applets[idx] = {}
        self.removeTab(idx)

    def set_applet(self, name):
        # clear view

        idx = self.currentIndex()
        for applet in self._applets.get(idx, {}).values():
            applet.hide()

        if not name:
            return

        if name in self._name.get(idx, {}):
            applet = self._applets[idx][name]
            applet.show()
        else:
            applet = new_plugin_instance('oalab.applet', name)
            if applet is None:
                return
            tab = self.currentWidget()
            tab.layout().addWidget(applet)
            self._applets.setdefault(idx, {})[name] = applet
            self._name[idx] = name

        _plugin_class = plugin_class('oalab.applet', name)
        self.setTabText(idx, _plugin_class.alias)
        self.setTabIcon(idx, obj_icon(_plugin_class))

    def currentApplet(self):
        try:
            return self._name[self.currentIndex()]
        except KeyError:
            return None

    def toString(self):
        return self._name.values()


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

        self.menu = QtGui.QMenu(self)

        self.action_add_tab = QtGui.QAction(qicon('Crystal_Clear_action_edit_add.png'), "Add tab", self.menu)
        self.action_add_tab.triggered.connect(self._tabwidget.new_tab)

        self.action_remove_tab = QtGui.QAction(qicon('Crystal_Clear_action_edit_remove.png'), "Remove tab", self.menu)
        self.action_remove_tab.triggered.connect(self._tabwidget.remove_tab)

        self.menu.addAction(self.action_add_tab)
        self.menu.addAction(self.action_remove_tab)

    def _on_tab_changed(self, idx):
        applet_name = self._tabwidget.currentApplet()
        if applet_name:
            self._applet_selector.setCurrentApplet(applet_name)

    def set_edit_mode(self, mode=True):
        if mode:
            self._applet_selector.show()
        else:
            self._applet_selector.hide()
        self._tabwidget.set_edit_mode(mode)

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def toString(self):
        return self._tabwidget.toString()


class OABinaryTree(BinaryTree):

    def toString(self, props=[]):
        filteredProps = {}
        for vid, di in self._properties.iteritems():
            filteredProps[vid] = {}
            for k, v in di.iteritems():
                if k in props:
                    if hasattr(v, 'toString'):
                        filteredProps[vid][k] = v.toString()
                    else:
                        filteredProps[vid][k] = v
        return repr(self._toChildren) + ", " + repr(self._toParents) + ", " + repr(filteredProps)

    @classmethod
    def fromString(cls, rep):
        try:
            tup = eval(rep)
        except:
            return None

        g = cls()
        toCh, toPar, props = tup
        g.__vid = max(props.iterkeys()) + 1
        g._toChildren = toCh.copy()
        g._toParents = toPar.copy()
        g._properties = props.copy()
        return g, tup


class InitContainerVisitor(object):

    """Visitor that searches which leaf id has pos in geometry"""

    def __init__(self, graph, wid):
        self.g = graph
        self.wid = wid

    def _to_qwidget(self, widget):
        if isinstance(widget, list):
            container = AppletContainer()
            for i, name in enumerate(widget):
                if i:
                    container._tabwidget.new_tab()
                container._tabwidget.set_applet(name)
            widget = container
        return widget

    def visit(self, vid):
        """
        """
        if self.g.has_property(vid, 'widget'):
            widget = self.g.get_property(vid, "widget")
            widget = self._to_qwidget(widget)
        else:
            widget = None

        if not self.g.has_children(vid):
            self.wid._install_child(vid, widget)
            return False, False

        direction = self.g.get_property(vid, "splitDirection")
        amount = self.g.get_property(vid, "amount")

        self.wid._split_parent(vid, direction, amount)

        return False, False


class OALabSplittableUi(SplittableUI):

    reprProps = ["amount", "splitDirection", "widget"]

    def __init__(self, parent=None, content=None):
        """Contruct a SplittableUI.
        :Parameters:
         - parent (qt.QtGui.QWidget)  - The parent widget
         - content (qt.QtGui.QWidget) - The widget to display in pane at level 0
        """
        QtGui.QWidget.__init__(self, parent)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.setAcceptDrops(True)
        # -- our backbone: --
        self._g = OABinaryTree()
        # -- contains geometry information (a vid->QRect mapping) --
        self._geomCache = {}
        # -- initialising the pane at level 0 --
        self._geomCache[0] = self.contentsRect()
        self._install_child(0, content)

    def getPlaceHolder(self):
        return AppletContainer()

    def _install_child(self, paneId, widget, **kwargs):
        g = self._g

        # -- get the old content --
        oldWidget = None
        if g.has_property(paneId, "widget"):
            oldWidget = g.get_property(paneId, "widget")
            if isinstance(oldWidget, QtGui.QWidget):
                oldWidget.hide()

        # -- place the new content --
        if widget is not None:
            widget.setParent(self)
            widget.show()
        g.set_property(paneId, "widget", widget)

        if not kwargs.get("noTearOffs", False):
            self._install_tearOffs(paneId)
        return oldWidget

    @classmethod
    def fromString(cls, rep, parent=None):
        g, tup = OABinaryTree.fromString(rep)

        newWid = cls(parent=parent)
        w0 = newWid._uninstall_child(0)
        if w0:
            w0.setParent(None)
            w0.close()

        newWid._g = g
        visitor = InitContainerVisitor(g, newWid)
        g.visit_i_breadth_first(visitor)
        newWid._geomCache[0] = newWid.contentsRect()
        newWid.computeGeoms(0)
        return newWid


class OALabMainWin(QtGui.QMainWindow):

    def __init__(self, layout=None):
        QtGui.QMainWindow.__init__(self)

        menu_names = ('Project', 'Edit', 'Viewer', 'Help')

        # Classic menu
        self.menu_classic = {}
        menubar = QtGui.QMenuBar()

        for menu_name in menu_names:
            self.menu_classic[menu_name] = menubar.addMenu(menu_name)

        self.setMenuBar(menubar)

        if layout is None:
            container = AppletContainer()
            self.splittable = OALabSplittableUi(parent=self)
            self.splittable.setContentAt(0, container)
        else:
            self.splittable = OALabSplittableUi.fromString(str(oalab_conf))

        self.setCentralWidget(self.splittable)

    def set_edit_mode(self, mode=True):
        for widget in self.splittable.getAllContents():
            if hasattr(widget, 'set_edit_mode'):
                widget.set_edit_mode(mode)

    def initialize(self):

        for instance in plugin_instances('oalab.applet'):
            if hasattr(instance, 'initialize'):
                instance.initialize()

        menus = plugin_instances('oalab.applet', 'PanedMenu')
        if menus:
            self.menu = menus[0]
            for plugin_class in self.pm.plugins('oalab.applet'):
                # TODO: support name properly (class name or name attribute)
                print plugin_class
                for instance in self.pm.instances('oalab.applet', plugin_class.name):
                    if hasattr(plugin_class, 'graft'):
                        plugin_class().graft(oa_mainwin=self, applet=instance)

    def add_action_to_existing_menu(self, action, menu_name, sub_menu_name):
        """
        Permit to add in a classic menubar the "action" in the menu "menu_name"
        in the sub_menu "sub_menu_name"
        """
        menubar = self.menuBar()
        if menu_name in self.menu_classic:
            menu = self.menu_classic[menu_name]
        else:
            menu = self.menu_classic[menu_name] = menubar.addMenu(menu_name)

        menu.addAction(action)

    def add_applet(self, *args, **kwds):
        pass


if __name__ == '__main__':
    instance = QtGui.QApplication.instance()

    if instance is None:
        app = QtGui.QApplication([])
    else:
        app = instance

    oalab_conf = ({0: [1, 2], 2: [3, 4], 3: [5, 6], 6: [7, 8]},
                  {0: None, 1: 0, 2: 0, 3: 2, 4: 2, 5: 3, 6: 3, 7: 6, 8: 6},
                  {0: {'amount': 0.1, 'splitDirection': 2},
                   1: {'widget': ['PanedMenu']},
                   2: {'amount': 0.75, 'splitDirection': 2},
                   3: {'amount': 0.2, 'splitDirection': 1},
                   4: {'widget': ['Shell', u'Logger', u'HistoryWidget']},
                   5: {'widget': ['ProjectManager', 'PkgManagerWidget', 'ControlManager', 'World']},
                   6: {'amount': 0.6, 'splitDirection': 1},
                   7: {'widget': ['EditorManager']},
                   8: {'widget': ['Viewer3D', 'VtkViewer', 'HelpWidget']}})

    mw = OALabMainWin(layout=oalab_conf)

    mw.resize(1024, 768)
    mw.show()

    mw.set_edit_mode(False)
    mw.initialize()

    if instance is None:
        app.exec_()
