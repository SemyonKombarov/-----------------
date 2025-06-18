# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QPushButton, QSizePolicy, QStatusBar, QTableView,
    QVBoxLayout, QWidget)

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
        mainWindow.resize(525, 355)
        self.centralwidget = QWidget(mainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(185, 0))

        self.verticalLayout_3.addWidget(self.lineEdit)

        self.listWidget = QListWidget(self.centralwidget)
        self.listWidget.setObjectName(u"listWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setMaximumSize(QSize(16777215, 100))

        self.verticalLayout_3.addWidget(self.listWidget)

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setEnabled(True)

        self.verticalLayout_3.addWidget(self.pushButton)

        self.tableView = QTableView(self.centralwidget)
        self.tableView.setObjectName(u"tableView")

        self.verticalLayout_3.addWidget(self.tableView)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setEnabled(True)

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout.addWidget(self.pushButton_3)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.horizontalLayout_2.addLayout(self.verticalLayout_3)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lineEdit_2 = QLineEdit(self.centralwidget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setMinimumSize(QSize(185, 0))

        self.verticalLayout.addWidget(self.lineEdit_2)

        self.listWidget_2 = QListWidget(self.centralwidget)
        self.listWidget_2.setObjectName(u"listWidget_2")
        sizePolicy.setHeightForWidth(self.listWidget_2.sizePolicy().hasHeightForWidth())
        self.listWidget_2.setSizePolicy(sizePolicy)
        self.listWidget_2.setMaximumSize(QSize(16777215, 100))

        self.verticalLayout.addWidget(self.listWidget_2)

        self.pushButton_4 = QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setEnabled(True)
        self.pushButton_4.setAutoFillBackground(False)
        self.pushButton_4.setStyleSheet(u"/*QPushButton{background-color:rgb(233, 248, 255)}/\n"
"QPushButton::hover{background-color:rgb(208, 248, 255)}\n"
"QPushButton::pressed{background-color:rgb(181, 232, 255)}QPushButton::disabled{background-color:rgb(233, 248, 255)}\n"
"")

        self.verticalLayout.addWidget(self.pushButton_4)

        self.tableView_2 = QTableView(self.centralwidget)
        self.tableView_2.setObjectName(u"tableView_2")

        self.verticalLayout.addWidget(self.tableView_2)

        self.pushButton_5 = QPushButton(self.centralwidget)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setEnabled(True)

        self.verticalLayout.addWidget(self.pushButton_5)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setKerning(True)
        self.label.setFont(font)
        self.label.setStyleSheet(u"color:rgb(209, 209, 209);\n"
"background-color: transparent;")
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.label)

        mainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(mainWindow)
        self.statusbar.setObjectName(u"statusbar")
        mainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(mainWindow)

        QMetaObject.connectSlotsByName(mainWindow)
    # setupUi

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(QCoreApplication.translate("mainWindow", u"\u041f\u0435\u0440\u0435\u0432\u043e\u0434 \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442 v0.1", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("mainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0438\u0441\u0445\u043e\u0434\u043d\u0443\u044e \u0421\u041a (\u043a\u043e\u0434 ESPG)", None))
        self.pushButton.setText(QCoreApplication.translate("mainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0442\u043e\u0447\u043a\u0443", None))
        self.pushButton_2.setText(QCoreApplication.translate("mainWindow", u"\u041f\u043e\u043c\u043e\u0448\u044c", None))
        self.pushButton_3.setText(QCoreApplication.translate("mainWindow", u"\u0420\u0435\u0432\u0435\u0440\u0441 <=>", None))
        self.lineEdit_2.setPlaceholderText(QCoreApplication.translate("mainWindow", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0446\u0435\u043b\u0435\u0432\u0443\u044e \u0421\u041a (\u043a\u043e\u0434 ESPG)", None))
        self.pushButton_4.setText(QCoreApplication.translate("mainWindow", u"\u041f\u0435\u0440\u0435\u0441\u0447\u0438\u0442\u0430\u0442\u044c", None))
        self.pushButton_5.setText(QCoreApplication.translate("mainWindow", u"\u0412\u044b\u0433\u0440\u0443\u0437\u0438\u0442\u044c XLSX", None))
        self.label.setText(QCoreApplication.translate("mainWindow", u"powered by pyproj 3.7.1", None))
    # retranslateUi

