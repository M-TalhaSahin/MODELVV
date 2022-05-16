from ui.gui_main import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QColor
from PyQt5.QtCore import Qt
import re
import xml.etree.ElementTree as ET

import nodeeditor.node_editor_widget as wdg
from xmlToNode import getNodeEdgeList
from DataBaseConnection import DataBaseConnection


class UIConnection(QMainWindow):
    NodeEditorWidget_class = wdg.NodeEditorWidget

    def __init__(self, _dbClass: DataBaseConnection):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.dbClass = _dbClass
        self.modelsList = []

        self.uppaalDisplayer = None
        self.currentFileName = None

        self.lwModel = QStandardItemModel(self.ui.lwModelList)


        self.ui.btnSaveDataBase.setEnabled(False)
        self.fillLWFromDB()
        self.UiComponents()

    def UiComponents(self):
        self.ui.btnFromLocal.clicked.connect(self.openFromLocal)
        self.ui.btnSaveDataBase.clicked.connect(self.save2DataBase)
        self.ui.lwModelList.doubleClicked.connect(self.listItemClicked)

    def setDisplayerWidget(self, nodeEdgeList):
        self.ui.tabWidgetTemplates.clear()
        for i in range(nodeEdgeList.__len__()):
            currentTab = QWidget()
            self.ui.tabWidgetTemplates.addTab(currentTab, nodeEdgeList[i].name)
            self.uppaalDisplayer = self.__class__.NodeEditorWidget_class(currentTab)
            self.uppaalDisplayer.setParent(currentTab)
            self.uppaalDisplayer.resize(self.ui.tabWidgetTemplates.size())
            self.uppaalDisplayer.setModel(nodeEdgeList)
            self.uppaalDisplayer.addNodes(i)
            self.uppaalDisplayer.setVisible(True)

    def setNonDBQueriesToWidget(self, fileName):
        f = open(fileName, "r")
        xmlFile = f.read()

        xmlFile = xmlFile.replace('\n', '')
        pattern = "<queries>(.*)</queries>"
        chopped = re.search(pattern, xmlFile)

        if chopped:
            xmlFile = "<queries> " + chopped.group(1) + " </queries>"
            tree = ET.ElementTree(ET.fromstring(xmlFile))
            root = tree.getroot()
            queryListModel = QStandardItemModel(self.ui.listView)
            for query in root.findall('query'):
                item = QStandardItem(query[0].text + "\n" + query[1].text)
                item.setEditable(False)
                queryListModel.appendRow(item)
            self.ui.listView.setModel(queryListModel)

    def setQueriesToWidget(self, queryList):
        queryListModel = QStandardItemModel(self.ui.listView)
        for i in range(queryList.__len__()):
            item = QStandardItem(queryList[i][0] + "\n" + queryList[i][1])
            item.setEditable(False)
            item.setCheckable(True)
            if not queryList[i][2]:
                item.setCheckState(Qt.CheckState.PartiallyChecked)
            elif queryList[i][2] == '1':
                item.setCheckState(Qt.CheckState.Checked)
                item.setBackground(QColor(179, 217, 255))
            elif queryList[i][2] == '0':
                item.setCheckState(Qt.CheckState.Unchecked)
                item.setBackground(QColor(255, 147, 149))
            queryListModel.appendRow(item)
        self.ui.listView.setModel(queryListModel)

    def fillLWFromDB(self):
        self.modelsList = self.dbClass.selectAllModelIDInfo()

        self.lwModel.clear()
        for model in self.modelsList:
            item = QStandardItem(str(model[0]) + ": " + model[1])
            item.setEditable(False)
            item.setBackground(QColor(161, 172, 213))
            self.lwModel.appendRow(item)

        self.ui.lwModelList.setModel(self.lwModel)

    def openFromLocal(self):
        fname, filter = QFileDialog.getOpenFileName(self, 'Select xml file', '', 'Graph (*.xml);;All files (*)')
        if fname:
            with open(fname, "r") as f:
                info = getNodeEdgeList(f.read())
            self.setDisplayerWidget(info)
            self.setLabelTexts(fileName=fname)
            self.currentFileName = fname
            item = QStandardItem("-: " + fname)
            item.setBackground(QColor(230, 175, 175))
            item.setEditable(False)
            self.lwModel.appendRow(item)
            self.modelsList.append(["-", fname, "-", "-"])
            self.ui.btnSaveDataBase.setEnabled(True)
            self.setNonDBQueriesToWidget(fname)

    def setLabelTexts(self, modelId="-", fileName="-", createDate="-", description="-"):
        self.ui.lblModelID.setText(modelId)
        self.ui.lblFileName.setText(fileName)
        self.ui.lblCreateDate.setText(createDate)
        self.ui.lblDescription.setText(description)

    def save2DataBase(self):
        self.dbClass.insertXmlFile(self.currentFileName, "emptyDesc")
        self.fillLWFromDB()

    def listItemClicked(self, index):
        index = index.row()
        if str(self.modelsList[index][0]) == "-":
            self.ui.btnSaveDataBase.setEnabled(True)
            fname = self.modelsList[index][1]
            with open(fname, "r") as f:
                info = getNodeEdgeList(f.read())
            self.setDisplayerWidget(info)
            self.setLabelTexts(fileName=fname)
            self.setNonDBQueriesToWidget(fname)
        else:
            self.ui.btnSaveDataBase.setEnabled(False)
            self.currentFileName = None
            xmlProp = getNodeEdgeList(self.dbClass.selectUppaalModelXml(self.modelsList[index][0]))
            self.setLabelTexts(modelId=str(self.modelsList[index][0]), fileName=self.modelsList[index][1],
                               createDate=self.modelsList[index][2].strftime("%m/%d/%Y"),
                               description=self.modelsList[index][3])
            self.setDisplayerWidget(xmlProp)
            self.setQueriesToWidget(self.dbClass.selectUppaalQueries(self.modelsList[index][0]))


