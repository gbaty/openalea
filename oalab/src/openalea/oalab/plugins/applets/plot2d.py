
from openalea.oalab.plugins.applets import PluginApplet

class Plot2dWidget(PluginApplet):                     

    name = 'Plot2d'
    alias = 'Plot2d'

    def __call__(self):
        # Load and instantiate graphical component that actually provide feature
        from openalea.oalab.plot2d.widget import MplTabWidget
        return MplTabWidget

    def graft(self, **kwds):
        mainwindow = kwds['oa_mainwin'] if 'oa_mainwin' in kwds else None
        applet = kwds['applet'] if 'applet' in kwds else None

        if applet is None or mainwindow is None:
            return
    
        from openalea.oalab.plot2d import activate_in_pyplot
        from matplotlib import pyplot as plt

        # work with qt4agg backend
        plt.switch_backend('qt4agg')

        activate_in_pyplot()
        plt.ion()
        mainwindow.add_applet(applet, self.alias, area='outputs')

        actions = applet.get_plugin_actions()
        if actions:
            for action in actions:
                # Add actions in PanedMenu
                mainwindow.menu.addBtnByAction('Plot2d', *action)

                # add action in classical menu
                group_name, act, btn_type = action
                mainwindow.add_action_to_existing_menu(action=act, menu_name='Plot2d', sub_menu_name=group_name)

