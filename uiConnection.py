from ui.gui_main import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QColor
from PyQt5.QtCore import Qt

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
        self.uppaalDisplayer = self.__class__.NodeEditorWidget_class(self.ui.wcontUPPAALDemo)
        self.uppaalDisplayer.setParent(self.ui.wcontUPPAALDemo)
        self.uppaalDisplayer.resize(self.ui.wcontUPPAALDemo.size())
        self.uppaalDisplayer.setModel(nodeEdgeList)
        self.uppaalDisplayer.addNodes(0)
        self.uppaalDisplayer.setVisible(True)

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
        else:
            self.ui.btnSaveDataBase.setEnabled(False)
            self.currentFileName = None
            xmlProp = getNodeEdgeList(self.dbClass.selectUppaalModelXml(self.modelsList[index][0]))
            self.setLabelTexts(modelId=str(self.modelsList[index][0]), fileName=self.modelsList[index][1],
                               createDate=self.modelsList[index][2].strftime("%m/%d/%Y"),
                               description=self.modelsList[index][3])
            self.setDisplayerWidget(xmlProp)


