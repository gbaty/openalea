# -*- python -*-
#
#       OpenAlea.OALab: Multi-Paradigm GUI
#
#       Copyright 2013 INRIA - CIRAD - INRA
#
#       File author(s): Julien Coste <julien.coste@inria.fr>
#
#       File contributor(s):
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################
__revision__ = "$Id: "

from openalea.vpltk.qt import QtGui, QtCore
from openalea.core.path import path as path_
from openalea.core import settings
from openalea.core import logger
from openalea.vpltk.project.manager import ProjectManager
from openalea.oalab.project.creator import CreateProjectWidget
from openalea.oalab.project.pretty_preview import ProjectSelectorScroll
from openalea.oalab.gui import resources_rc # do not remove this import else icon are not drawn
from openalea.oalab.gui.utils import qicon

class ProjectManagerWidget(QtGui.QWidget):
    """
    Object which permit to manage projects.

    :Warning: this QWidget is not used like a widget but like the interface between GUI (buttons "newProj", "newScript",...)
    and objects (project, control, ...)

    :TODO: Refactor it
    """

    def __init__(self, session, controller, parent=None):
        super(ProjectManagerWidget, self).__init__(parent)
        self._actions = []
        self.session = session
        self.controller = controller
        self.setAccessibleName("Project Manager")

        self.projectManager = ProjectManager()

        self.actionNewProj = QtGui.QAction(qicon("new.png"), "New", self)
        self.actionNewProj.setShortcut(
            QtGui.QApplication.translate("MainWindow", "Ctrl+N", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpenProj = QtGui.QAction(qicon("open.png"), "Open", self)
        self.actionOpenProj.setShortcut(
            QtGui.QApplication.translate("MainWindow", "Ctrl+O", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSaveProj = QtGui.QAction(qicon("save.png"), "Save", self)
        self.actionSaveProjAs = QtGui.QAction(qicon("save.png"), "Save As", self)
        # self.actionSaveProj.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCloseProj = QtGui.QAction(qicon("closeButton.png"), "Close All", self)
        self.actionEditMeta = QtGui.QAction(qicon("book.png"), "Edit Metadata", self)
        self.actionAddFile = QtGui.QAction(qicon("bool.png"), "Add To Proj", self)

        self.actionNewProj.triggered.connect(self.new)
        self.actionOpenProj.triggered.connect(self.open)
        self.actionSaveProjAs.triggered.connect(self.saveAs)
        self.actionSaveProj.triggered.connect(self.saveCurrent)
        self.actionCloseProj.triggered.connect(self.closeCurrent)
        self.actionEditMeta.triggered.connect(self.edit_metadata)
        self.actionAddFile.triggered.connect(self.add_file_to_project)

        self._actions = [["Project", "Manage Project", self.actionNewProj, 1],
                         ["Project", "Manage Project", self.actionOpenProj, 0],
                         ["Project", "Manage Project", self.actionSaveProj, 0],
                         ["Project", "Manage Project", self.actionSaveProjAs, 1],
                         ["Project", "Manage Project", self.actionCloseProj, 1],
                         ["Project", "Manage Project", self.actionEditMeta, 1],
                         ["Project", "Manage Project", self.actionAddFile, 1],
                         ]


        # Menu used to display all available projects.
        # This menu is filled dynamically each time this menu is opened
        self.menu_available_projects = QtGui.QMenu(u'Available Projects')
        self.menu_available_projects.aboutToShow.connect(self._update_available_project_menu)
        self.action_available_project = {} # Dict used to know what project corresponds to triggered action

        self.defaultProj()

    def defaultProj(self):
        proj = self.projectManager.load_default()
        self.session._project = proj
        self.session._is_proj = True
        if not self.session.project.src:
            txt = '''# -*- coding: utf-8 -*-
"""
OpenAlea Lab editor

This temporary script is saved in temporary project in
%s

You can rename/move this project thanks to the button "Save As" in menu.
"""''' % str(self.session.project.path / self.session.project.name)
            self.session.project.add(category="src", name=".temp.py", value=txt)
        self._project_changed()
        self._load_control()

    def actions(self):
        return self._actions

    def open(self, name=False, path=None):
        """
        If name==false, display a widget to choose project to open.
        Then open project.
        """
        self.session.project_manager.discover()
        projects = self.session.project_manager.projects
        self.proj_selector = ProjectSelectorScroll(projects=projects, open_project=self.openProject)
        self.proj_selector.show()

        # if name is False:
        #     name = showOpenProjectDialog()
        # if name:
        #     proj_path = path_(name).abspath()
        #     proj_name = proj_path.basename()
        #     proj_path = proj_path.dirname()
        #     if path:
        #         proj_path = path_(path)
        #     logger.debug("Open Project named " + proj_name)
        #     if self.session.project:
        #         if self.session.current_is_project():
        #             logger.debug("Close Project named " + self.session.project.name)
        #             self.projectManager.close(self.session.project.name)
        #             logger.debug("Project named " + self.session.project.name + " closed.")
        #
        #     proj = self.projectManager.load(proj_name, proj_path)
        #
        #     logger.debug("Project " + str(proj) + " loaded")
        #
        #     if proj == -1:
        #         logger.warning("Project was not loaded...")
        #         return -1
        #     else:
        #         return self.openProject(proj)


    def openProject(self, project):
        """
        Open a project in application from project

        :param project: opened project from vpltk
        """
        if hasattr(self, "proj_selector"):
            self.proj_selector.hide()
        self.closeCurrent()

        project.start()
        logger.debug("Project " + str(project) + " opened")

        project.world = self.session.world
        self.session._project = project
        self.session._is_proj = True
        self._project_changed()
        self._load_control()

        logger.debug("Project opened: " + str(self.session._project))
        return self.session._project

    def new(self):
        """
        Create an default empty project with a default name.

        Open a window to define metadata of the project.
        """
        self.project_creator = CreateProjectWidget()
        self.project_creator.show()
        self.connect(self.project_creator, QtCore.SIGNAL('ProjectMetadataSet(PyQt_PyObject)'), self.openProject)

    def edit_metadata(self):
        self.project_creator = CreateProjectWidget(self.session._project)
        self.project_creator.show()
        self.connect(self.project_creator, QtCore.SIGNAL('ProjectMetadataSet(PyQt_PyObject)'), self.metadata_edited)

    def metadata_edited(self, proj):
        self.session._project.metadata = proj.metadata
        return self.session._project

    def add_file_to_project(self):
        """
        Add an opened file to the current project (in source for the moment).

        :todo: propose to the user where to add it (not only in source)
        """
        text = self.controller.applet_container.tabText(self.controller.applet_container.currentIndex())
        categories = self.session._project.files.keys()
        self.selector = SelectCategory(filename=text, categories=categories)
        self.selector.show()

        self.selector.ok_button.clicked.connect(self.add_file)

    def add_file(self):
        category = self.selector.combo.currentText()
        self.selector.hide()

        text = self.controller.applet_container.currentWidget().get_text()
        index = self.controller.applet_container.currentIndex()
        filename = self.selector.line.text()
        self.controller.applet_container.setTabText(index, filename)
        self.session._project.add(category=category, name=filename, value=text)

        self.session.update_namespace()
        self._tree_view_change()

    def renameCurrent(self, new_name=None):
        """
        Rename current project.
        """
        if self.session.project:
            name = self.session.project.name
            if not new_name:
                new_name = showNewProjectDialog(default_name=path_(name) / "..",
                                                text='Select new name to save project')
            self.session.project.rename(category="project", old_name=name, new_name=new_name)
            self._project_changed()
        else:
            print(
                "You are not working inside project, so you can't use 'rename project'. Please create or load one first.")

    def saveAs(self):
        """
        Save current project but permit to rename and move it..
        """
        if self.session.current_is_project():
            name = showNewProjectDialog(default_name=None, text="Select name to save project")
            if name:
                self.session.project.rename(category="project", old_name=self.session.project.name, new_name=name)
                self._tree_view_change()
                self.saveCurrent()
        else:
            print "You are not working inside project. Please create or load one first."

    def saveCurrent(self):
        """
        Save current project.
        """
        if self.session.current_is_project():
            container = self.controller.applet_container
            if container is None: # CPL
                return

            for i in range(container.count()):
                container.setCurrentIndex(i)
                name = container.tabText(i)
                wid = container.widget(i)
                if hasattr(wid, "save"):
                    wid.save(name)
            self._update_control()
            self.session.project.save()
            self._project_changed()

        else:
            print "You are not working inside project. Please create or load one first."

    def closeCurrent(self):
        """
        Close current project.
        """
        if self.session.current_is_project():
            if hasattr(self.session, "name"):
                logger.debug("Close Project named %s" % self.session.project.name)
                self.projectManager.close(self.session.project.name)
            else:
                logger.debug("Close empty Project")
            self.session._project = None
            self.session._is_proj = False
            self._clear_control()
            if self.controller.applet_container:
                self.controller.applet_container.closeAll()
            self._project_changed()
        else:
            print "You are not working inside project. Please create or load one first."

    def _project_changed(self):
        """
        Update what is needed when the current project is changed
        """
        logger.debug("Project changed")
        # CPL: CHECK FIRST IF THE OBJECTS EXISTS.
        # This wil be not always the case.

        self.session.update_namespace()
        self._scene_change()
        self._control_change() # do nothing
        if self.controller.applet_container:
            self.controller.applet_container.reset()
        self.open_all_scripts_from_project()
        # self.open_all_files_from_project()
        self._tree_view_change()

    def update_from_widgets(self):
        self._update_control()

    def _load_control(self):
        """
        Get control from project and put them into widgets
        """
        if hasattr(self.controller, "_plugins"):
            if self.controller._plugins.has_key('ControlPanel'):
                self.controller._plugins['ControlPanel'].instance().load()
        else:
            if self.controller.applets.has_key('ControlPanel'):
                self.controller.applets['ControlPanel'].load()
        logger.debug("Load Controls")

    def _update_control(self):
        """
        Get control from widget and put them into project
        """
        if hasattr(self.controller, "_plugins"):
            if self.controller._plugins.has_key('ControlPanel'):
                self.controller._plugins['ControlPanel'].instance().update()
        else:
            if self.controller.applets.has_key('ControlPanel'):
                self.controller.applets['ControlPanel'].update()
        logger.debug("Update Controls")

    def _clear_control(self):
        if hasattr(self.controller, "_plugins"):
            if self.controller._plugins.has_key('ControlPanel'):
                self.controller._plugins['ControlPanel'].instance().clear()
        else:
            if self.controller.applets.has_key('ControlPanel'):
                self.controller.applets['ControlPanel'].clear()
        logger.debug("Clear Controls")

    def _control_change(self):
        pass

    def _tree_view_change(self):
        if hasattr(self.controller, "_plugins"):
            if self.controller._plugins.has_key('ProjectWidget'):
                self.controller._plugins['ProjectWidget'].instance().update()
        else:
            if self.controller.applets.has_key('Project'):
                self.controller.applets['Project'].update()
        logger.debug("Tree View changed")

    def open_all_scripts_from_project(self):
        logger.debug("Script changed")
        if self.session.project:
            project = self.session.project
            for script in project.src:
                language = str(script).split('.')[-1]
                self.controller.applet_container.openTab(language, script, project.src[script])

    def open_all_files_from_project(self):
        logger.debug("Script changed")
        if self.session.project:
            project = self.session.project
            for category in project.files:
                for file_ in project.files[category]:
                    language = str(file_).split('.')[-1]
                    self.controller.applet_container.openTab(language, file_, project.files[category][file_])

    def _scene_change(self):
        logger.debug("Scene changed")
        if self.session.current_is_project():
            self.session.world.reset()
            project = self.session.project
            for w in project.world:
                self.session.world.add(name=w, obj=project.world[w])

    def _update_available_project_menu(self):
        """
        Discover all projects and generate an action for each one.
        Then connect this action to _on_open_project_triggered
        """
        self.session.project_manager.discover()
        self.menu_available_projects.clear()
        self.action_available_project.clear()
        for project in self.session.project_manager.projects:
            icon_path = project.icon_path
            icon_name = icon_path if icon_path else ":/images/resources/openalealogo.png"
            action = QtGui.QAction(QtGui.QIcon(icon_name), project.name, self.menu_available_projects)
            action.triggered.connect(self._on_open_project_triggered)
            self.menu_available_projects.addAction(action)
            self.action_available_project[action] = project

    def _on_open_project_triggered(self):
        self.openProject(self.action_available_project[self.sender()])

def showNewProjectDialog(default_name=None, text=None, parent=None):
    my_path = path_(settings.get_project_dir())
    if default_name:
        my_path = my_path / default_name
    if not text:
        text = 'Select name to create project'
    fname = QtGui.QFileDialog.getSaveFileName(parent, text,
                                              my_path)
    return fname


def showOpenProjectDialog(parent=None):
    my_path = path_(settings.get_project_dir())
    fname = QtGui.QFileDialog.getExistingDirectory(parent, 'Select Project Directory',
                                                   my_path)
    return fname


class SelectCategory(QtGui.QWidget):
    def __init__(self, filename="", categories=["src"], parent=None):
        super(SelectCategory, self).__init__(parent=parent)
        self.categories = categories

        layout = QtGui.QGridLayout(self)

        self.label = QtGui.QLabel("Select in which category you want to add this file: ")
        self.label2 = QtGui.QLabel("New filename: ")
        self.combo = QtGui.QComboBox(self)
        self.combo.addItems(self.categories)
        self.combo.setCurrentIndex(1)
        self.line = QtGui.QLineEdit(filename)

        self.ok_button = QtGui.QPushButton("Ok")

        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.combo, 0, 1)
        layout.addWidget(self.label2, 1, 0)
        layout.addWidget(self.line, 1, 1)
        layout.addWidget(self.ok_button, 2, 0, 2, 2)

        self.setLayout(layout)

