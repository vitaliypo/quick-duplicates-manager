# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\design.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1500, 1000)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.gui_button = QtWidgets.QPushButton(self.centralwidget)
        self.gui_button.setObjectName("gui_button")
        self.horizontalLayout.addWidget(self.gui_button)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_errors_count = QtWidgets.QLabel(self.centralwidget)
        self.label_errors_count.setObjectName("label_errors_count")
        self.horizontalLayout_2.addWidget(self.label_errors_count)
        self.btn_previous_error = QtWidgets.QPushButton(self.centralwidget)
        self.btn_previous_error.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_previous_error.sizePolicy().hasHeightForWidth())
        self.btn_previous_error.setSizePolicy(sizePolicy)
        self.btn_previous_error.setMinimumSize(QtCore.QSize(20, 0))
        self.btn_previous_error.setObjectName("btn_previous_error")
        self.horizontalLayout_2.addWidget(self.btn_previous_error)
        self.btn_next_error = QtWidgets.QPushButton(self.centralwidget)
        self.btn_next_error.setEnabled(False)
        self.btn_next_error.setObjectName("btn_next_error")
        self.horizontalLayout_2.addWidget(self.btn_next_error)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.field_current_error = QtWidgets.QLineEdit(self.centralwidget)
        self.field_current_error.setEnabled(True)
        self.field_current_error.setReadOnly(True)
        self.field_current_error.setObjectName("field_current_error")
        self.horizontalLayout_2.addWidget(self.field_current_error)
        spacerItem1 = QtWidgets.QSpacerItem(100, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.groups_have_actions_label = QtWidgets.QLabel(self.centralwidget)
        self.groups_have_actions_label.setObjectName("groups_have_actions_label")
        self.horizontalLayout_2.addWidget(self.groups_have_actions_label)
        self.btn_previous_group = QtWidgets.QPushButton(self.centralwidget)
        self.btn_previous_group.setEnabled(False)
        self.btn_previous_group.setObjectName("btn_previous_group")
        self.horizontalLayout_2.addWidget(self.btn_previous_group)
        self.btn_next_group = QtWidgets.QPushButton(self.centralwidget)
        self.btn_next_group.setEnabled(False)
        self.btn_next_group.setObjectName("btn_next_group")
        self.horizontalLayout_2.addWidget(self.btn_next_group)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1500, 20))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuMark = QtWidgets.QMenu(self.menubar)
        self.menuMark.setObjectName("menuMark")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.OpenResults = QtWidgets.QAction(MainWindow)
        self.OpenResults.setObjectName("OpenResults")
        self.actionDelete_sibling_duplicates = QtWidgets.QAction(MainWindow)
        self.actionDelete_sibling_duplicates.setObjectName("actionDelete_sibling_duplicates")
        self.actionHardlink_sibling_duplicates = QtWidgets.QAction(MainWindow)
        self.actionHardlink_sibling_duplicates.setObjectName("actionHardlink_sibling_duplicates")
        self.menuFile.addAction(self.OpenResults)
        self.menuMark.addAction(self.actionDelete_sibling_duplicates)
        self.menuMark.addAction(self.actionHardlink_sibling_duplicates)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuMark.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Open all folders"))
        self.gui_button.setText(_translate("MainWindow", "Open selected folder"))
        self.pushButton_2.setText(_translate("MainWindow", "Execute actions"))
        self.pushButton_3.setText(_translate("MainWindow", "Mark all "))
        self.label_errors_count.setText(_translate("MainWindow", "Errors found: 0"))
        self.btn_previous_error.setText(_translate("MainWindow", "Previous ▲"))
        self.btn_next_error.setText(_translate("MainWindow", "Next ▼"))
        self.label_2.setText(_translate("MainWindow", "Current row error:"))
        self.field_current_error.setText(_translate("MainWindow", "Source for Hardlink not specified"))
        self.groups_have_actions_label.setText(_translate("MainWindow", "Groups have actions: "))
        self.btn_previous_group.setText(_translate("MainWindow", "Previous ▲"))
        self.btn_next_group.setText(_translate("MainWindow", "Next ▼"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuMark.setTitle(_translate("MainWindow", "Mark"))
        self.OpenResults.setText(_translate("MainWindow", "Open CloneSpy results"))
        self.OpenResults.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionDelete_sibling_duplicates.setText(_translate("MainWindow", "Delete sibling duplicates"))
        self.actionHardlink_sibling_duplicates.setText(_translate("MainWindow", "Hardlink sibling duplicates"))
