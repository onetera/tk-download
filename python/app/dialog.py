# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import os
import sys
import traceback
import threading
import subprocess

# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from sgtk.util import get_current_user

from .framework_qtwidgets import *
from .ui.dialog import Ui_Dialog
from .util import monitor_qobject_lifetime
from .my_tasks.my_tasks_form import MyTasksForm
from .my_tasks.my_tasks_model import MyTasksModel

# There are two loggers
# logger is shotgun logger
# _logger is a independet logger
logger = sgtk.platform.get_logger(__name__)


def show_dialog(app_instance):
    """
    Shows the main dialog window.
    """
    # in order to handle UIs seamlessly, each toolkit engine has methods for launching
    # different types of windows. By using these methods, your windows will be correctly
    # decorated and handled in a consistent fashion by the system. 
    
    # we pass the dialog class to this method and leave the actual construction
    # to be carried out by toolkit.
    app_instance.engine.show_dialog("Download", app_instance, AppDialog)



class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """
    
    def __init__(self):
        """
        Constructor
        """
        QtGui.QWidget.__init__(self)

        self._app = sgtk.platform.current_bundle()
        
        self.user = sgtk.util.get_current_user(self._app.sgtk)

        ################################################################
        self.ui = Ui_Dialog() 
        self.ui.setupUi(self)
        ################################################################

        self.ui.download_btn.clicked.connect(self.btnCallback)

        # create a background task manager for the widget to use
        self._task_manager = task_manager.BackgroundTaskManager(self,
            start_processing=True,
            max_threads=4)
        monitor_qobject_lifetime(self._task_manager, "Main task manager")
        self._task_manager.start_processing()

        self.createTasksForm()

    def btnCallback(self):
        msg_box = QtGui.QMessageBox()
        msg_box.setWindowTitle("Popup Message")
        msg_box.setText("OK")
        msg_box.exec_()

    def createTasksForm(self):
        """
        Create my task form and facility task form icluding model and view.
        :param UI_filter_action: QAction contains shotgun filter selected in UI
        """
        try:
            self._my_tasks_model = self._build_my_tasks_model(
                self._app.context.project)
            self._my_tasks_form = MyTasksForm(self._my_tasks_model,
                                              allow_task_creation=False,
                                              parent=self)
            # refresh tab
            self.ui.tasks_widget.addTab(self._my_tasks_form, "My Tasks")
            self._my_tasks_form.entity_selected.connect(self.itemSelect)
            
            
        except Exception as e:
            logger.exception("Failed to Load my tasks, because %s \n %s"
                             % (e, traceback.format_exc()))
    
    # def itemSelect(self,selection_detail,breadcrumb_trail):
    def itemSelect(self):
        print("select task item")
            
    def _build_my_tasks_model(self, project):
        """
        Get settings from config file and append those settings default
        Then create task model
        :param project: dict
                        sg project context
        :UI_filter action: QAction contains shotgun filter selected in UI
        """
        if not self.user:
            # can't show my tasks if we don't know who 'my' is!
            logger.debug("There is no tasks because user is not defined")
            return None
        # get any extra display fields we'll need to retrieve:
        extra_display_fields = self._app.get_setting("my_tasks_extra_display_fields")
        # get the my task filters from the config.
        my_tasks_filters = self._app.get_setting("my_tasks_filters")
        model = MyTasksModel(project,
                             self.user,
                             extra_display_fields,
                             my_tasks_filters,
                             parent=self,
                             bg_task_manager=self._task_manager)
        monitor_qobject_lifetime(model, "My Tasks Model")
        model.async_refresh()
        logger.debug("Tasks Model Build Finished")
        return model