# :coding: utf-8

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
import traceback
import host
import down

from datetime import datetime
# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from sgtk.util import get_current_user

from .framework_qtwidgets import *
from .ui.dialog import Ui_Dialog
from .util import monitor_qobject_lifetime
from .my_tasks.my_tasks_form import MyTasksForm
from .my_tasks.my_tasks_model import MyTasksModel

# import from_storenext
from .model.comp_item_model import CompItemRegister

# There are two loggers
# logger is shotgun logger
# _logger is a independet logger
logger = sgtk.platform.get_logger(__name__)

DEBUG = True

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


def msg_box(text):
    msg_box = QtGui.QMessageBox()
    msg_box.setWindowTitle("Popup Message")
    msg_box.setText(text)
    msg_box.exec_()

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

        self.ui.horizontalLayout_3 = QtGui.QVBoxLayout()
        self.ui.set_path_btn = QtGui.QPushButton("Set_Path",self)
        self.ui.progress = QtGui.QProgressBar()
        self.ui.line_editor = QtGui.QLineEdit()
        
        self.ui.horizontalLayout_3.addWidget(self.ui.line_editor)
        self.ui.horizontalLayout_3.addWidget(self.ui.progress)
        self.ui.horizontalLayout_3.addWidget(self.ui.set_path_btn)

        #기존 다운로드 버튼보다 Set_Path버튼이 위로 올라가도록
        self.ui.horizontalLayout_3.removeWidget(self.ui.download_btn)
        self.ui.horizontalLayout_3.addWidget(self.ui.download_btn)

        self.ui.verticalLayout_2.addLayout(self.ui.horizontalLayout_3)
        ################################################################

        self.ui.download_btn.clicked.connect(self.btnCallback)
        self.ui.set_path_btn.clicked.connect(self.set_path)

        # create a background task manager for the widget to use
        self._task_manager = task_manager.BackgroundTaskManager(self,
            start_processing=True,
            max_threads=4)
        monitor_qobject_lifetime(self._task_manager, "Main task manager")
        self._task_manager.start_processing()

        self.createTasksForm()

        #sgtk
        current_bundle = sgtk.platform.current_bundle()
        context = current_bundle.context
        self._sg = context.tank.shotgun
        #get user info
        self._get_ftp_info = self._get_user_ftp_info(self.user['id'])

        #ftp 앱을 실행하면 host객체의 접속을 유지한다.
        print(os.getenv("DEBUG"))        
        if None != self._get_ftp_info:
            print(self._get_ftp_info['sg_ftp_host'])
            print(self._get_ftp_info['sg_ftp_id'])
            print(self._get_ftp_info['sg_ftp_password'])

        if DEBUG:
            print("----------------------DEBUG-------------------------")
            self._host = host.ftpHost(
                "10.0.20.38",
                "west_rnd",
                "rnd2022!"
            )
        else:
            self._host = host.ftpHost(
                self._get_ftp_info['sg_ftp_host'],
                self._get_ftp_info['sg_ftp_id'],
                self._get_ftp_info['sg_ftp_password']
            )

    def closeEvent(self,event):
        self._host.close()
        print("closeEvent")

    def _set_item_and_print_log(self):
        self.item = []
        # print("*"*100)
        for comp in self._comp_item:
            for down_item in comp.get_download_items:
                self.item.append(down_item)
                # print(down_item)
        # print("*"*100)

    def btnCallback(self):
        #test
        # if self._host.path.exists("/log"):
        # self._host.upload("/storenext3/user/pipeline/minwoo/log/20230817_1826.log","/log/20230817_1826.log")
        # return
        log_data = list()
        log_data.append("=================================================")
        log_data.append(datetime.today().strftime("%Y/%m/%d %H:%M:%S\n"))

        if not self.ui.line_editor.text():
            return
        if None != self._comp_item:
            self._set_item_and_print_log()
        print("-----------------------------download start-------------------------")
        input_path = self.ui.line_editor.text()
        if input_path[-1] == '/':
            input_path = input_path[:-1]

        self.log_path = input_path + "/show/log"
        self.ftp_log_path = self._host._get_log_path()
        for i in self.item:
            result_path = input_path + i[0]
            directory_path, file_name = os.path.split(result_path)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            if not os.path.exists(result_path):
                download = down.Download(result_path,i,self._host)
                # if download._result[1] == True:
                log_data.append(download._result)
        print("-----------------------------download end-------------------------")
        log_data.append("=================================================")
        self._ftp_log(log_data)
        msg_box("다운로드 완료")

    def _ftp_log(self,item):
        filename = datetime.today().strftime("%Y%m%d") + ".log"
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        log_path = os.path.join(self.log_path,filename)
        with open(log_path, 'a') as file:
            for log in item:
                file.write(str(log) + '\n')
        self._host.upload(log_path,os.path.join(self.ftp_log_path,filename))

        

    def itemSelect(self,selection_detail):
        self._comp_item = []
        self.copy = []
        #1.Comp Task
        for sel in selection_detail:
            if sel['entity']['content'] == "comp" or sel['entity']['content'] == "test":
                self._comp_item.append(CompItemRegister(sel, self._sg))
    
    def set_path(self):
        default_directory = os.path.expanduser("~")
        file_dialog = QtGui.QFileDialog().getExistingDirectory(None,
                                                               'Output directory',
                                                               default_directory)
        self.ui.line_editor.setText(file_dialog)
        return file_dialog

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
            
            # self._my_tasks_form.selectionChanged(self._on_selection_changed)
            
            
        except Exception as e:
            logger.exception("Failed to Load my tasks, because %s \n %s"
                             % (e, traceback.format_exc()))



    def _get_user_ftp_info(self,id):
        return self._sg.find_one("HumanUser",[['id','is',id]],['sg_ftp_id','sg_ftp_password','sg_ftp_host'])
            
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