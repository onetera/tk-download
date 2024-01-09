# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(464, 830)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tasks_widget = QtGui.QTabWidget(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tasks_widget.sizePolicy().hasHeightForWidth())
        self.tasks_widget.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.tasks_widget.setFont(font)
        self.tasks_widget.setAcceptDrops(True)
        self.tasks_widget.setObjectName("tasks_widget")
        self.horizontalLayout.addWidget(self.tasks_widget)
        self.horizontalLayout.setStretch(0, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.path_edt = QtGui.QLineEdit(  )
        self.set_path_btn = QtGui.QPushButton('Set Path' )
        self.path_edt.setMinimumHeight( 30 )
        self.set_path_btn.setMinimumHeight( 30 )

        path_lay = QtGui.QHBoxLayout()
        path_lay.addWidget( self.path_edt )
        path_lay.addWidget( self.set_path_btn )

        self.download_btn = QtGui.QPushButton(Dialog)
        self.download_btn.setObjectName("download_btn")
        self.download_btn.setMinimumHeight( 35 )
        #self.horizontalLayout_2.addWidget(self.download_btn)

        self.progress = QtGui.QProgressBar()

        self.verticalLayout_2.addLayout( path_lay )
        self.verticalLayout_2.addWidget( self.progress  )
        self.verticalLayout_2.addWidget( self.download_btn )
        self.verticalLayout_2.setStretch(0, 10)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "The Current Sgtk Environment", None, QtGui.QApplication.UnicodeUTF8))
        self.download_btn.setText(QtGui.QApplication.translate("Dialog", "Download", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
