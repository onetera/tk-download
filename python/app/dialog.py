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
from pprint import pprint
import socket
import sys

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
        #self.ui.set_path_btn.clicked.connect(self.set_path)

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
        if os.getenv( 'WW_LOCATION' ) == 'vietnam' :
            print("----------------------WW_LOCATION-------------------------")
            print(os.getenv('WW_LOCATION'))
            self._host = host.ftpHost(
                '220.127.148.3',
                'west_rnd',
                'rnd2022!'
            )
        else:
            print("----------------------DEBUG-------------------------")
            self._host = host.ftpHost(
                '10.0.20.38',
                'west_rnd',
                'rnd2022!'
            )
        # if self._get_ftp_info:
        #     print(self._get_ftp_info['sg_ftp_host'])
        #     print(self._get_ftp_info['sg_ftp_id'])
        #     print(self._get_ftp_info['sg_ftp_password'])

        # if os.getenv( 'WW_LOCATION' ) == 'vietnam' :
        #     ftp_ip = '220.127.148.3'
        # else:
        #     ftp_ip = '10.0.20.38'

        # if ftp_ip == '10.0.20.38':
        #     print("----------------------DEBUG-------------------------")
        #     self._host = host.ftpHost(
        #         '10.0.20.38',
        #         "west_rnd",
        #         "rnd2022!"
        #     )
        # else:
        #     self._host = host.ftpHost(
        #         self._get_ftp_info['sg_ftp_host'],
        #         self._get_ftp_info['sg_ftp_id'],
        #         self._get_ftp_info['sg_ftp_password']
        #     )

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

#        if not self.ui.path_edt.text():
#            return



        if self._comp_item:
            self._set_item_and_print_log()
        print("-----------------------------download start-------------------------")


        ## set path를 사용 하지 않고 강제로 다운로드 경로 생성
        input_path = os.path.expanduser( '~' )
#        input_path = self.ui.path_edt.text()
#        if input_path[-1] == '/':
#            input_path = input_path[:-1]

        self.log_path = os.path.join( 
                                input_path,  'show', "log"
        )
        self.ftp_log_path = self._host._get_log_path()



        if len(self.item) > 0:
            for i in self.item:
                result_path = input_path + i[0]
                directory_path, file_name = os.path.split(result_path)

                print( '\n' )
                print( '*'*50 )
                print( ' i : ' , i )
                print( 'input_path : ' , input_path )
                print( 'result_path : ' , result_path )
                print( 'directory path : ' , directory_path )
                print( 'file name : ' , file_name )
                print( '*'*50 )
                print( '\n' )
                

                if not os.path.exists(directory_path):
                    os.makedirs(directory_path)

                if not os.path.exists(result_path) and self._host.path.exists(i[0]):
                    download = down.Download(result_path,i,self._host)
                    # if download._result[1] == True:
                    log_data.append(download._result)
                elif not self._host.path.exists(i[0]):
                    pure_file_name = file_name.split('.')[0]
                    
                    log_data.append('FTP Path is not exists.')
                    self.msg_box( 'error', 'Ftp Download Error', 'FTP Path is not exists.\n file name : {}'.format(pure_file_name) )
                    return
        
        else:
            log_data.append('This task has not "org" or "src" type shots.')
            self.msg_box( 'error', 'Shot Type Error', 'This task has not "org" or "src" type shots.')

        print("-----------------------------download end-------------------------")
        log_data.append("=================================================")
        self._ftp_log(log_data)
        self.msg_box( 'info', 'Download', 'Finished to download' )


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

        print( '\n' )
        print( '== item select ==' )
        pprint( selection_detail )
        print( '\n' )

        task_name_list = ['comp', 'test', 'remove', 'roto']

        for sel in selection_detail:
            if sel['entity']['content'] in task_name_list:
                self._comp_item.append(CompItemRegister(sel, self._sg))
    
#    def set_path(self):
#        default_directory = os.path.expanduser("~")
#        file_dialog = QtGui.QFileDialog().getExistingDirectory(None,
#                                                               'Output directory',
#                                                               default_directory)
#        self.ui.path_edt.setText(file_dialog)
#        return file_dialog

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

    def msg_box( self, msg_type, title, message ):
        msg = QtGui.QMessageBox
        
        if msg_type == 'info':
            msg = msg.information( self, title, message )

        if msg_type == 'error':
            msg = msg.critical( self, title, message)

        if msg_type == 'warning':
            msg = msg.warning( self, title, message)

        return msg