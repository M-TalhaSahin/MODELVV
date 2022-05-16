import psycopg2
from datetime import datetime
import re
import xml.etree.ElementTree as ET
from PyQt5.QtCore import Qt


class DataBaseConnection:
    def __init__(self, dbname, user, password):
        try:
            print("Connecting to database...")
            self.connection = psycopg2.connect("dbname =" + dbname + " user = " + user + " password = " + password)
            print("Connection to the database has been established.")
        except(Exception, psycopg2.Error) as errorMsg:
            print("A database-related error occured: ", errorMsg)

    def insertXmlFile(self, filename: str, description):
        cursor = self.connection.cursor()
        f = open(filename, "r")
        xmlFile = f.read()

        cursor.execute(
            "INSERT INTO tblUppaal(createDate, description, xmlfile, \"fileName\")"
            "VALUES(%s, %s, %s, %s) RETURNING modelID;",
            (str(datetime.now()), description, xmlFile, filename.split('/')[-1]))

        modelID = cursor.fetchall()[0][0]

        xmlFile = xmlFile.replace('\n', '')
        pattern = "<queries>(.*)</queries>"
        chopped = re.search(pattern, xmlFile)

        if chopped:
            xmlFile = "<queries> " + chopped.group(1) + " </queries>"

            tree = ET.ElementTree(ET.fromstring(xmlFile))
            root = tree.getroot()

            for query in root.findall('query'):
                cursor.execute(
                    "INSERT INTO tblQuery(modelID, query, description)"
                    "VALUES(%s, %s, %s)",
                    (modelID, query[0].text, query[1].text))

        self.connection.commit()
        cursor.close()

    def selectUppaalQueries(self, modelID):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT tblquery.query, tblquery.description, tblquery.result, tblquery.queryid FROM tblquery "
            "WHERE tblquery.modelID={0}".format(str(modelID)))
        rec = cursor.fetchall()
        cursor.close()
        return rec

    def setQueryState(self, queryID, state):
        cursor = self.connection.cursor()
        stateFormatted = 'null'
        if state == Qt.CheckState.Unchecked:
            stateFormatted = '0'
        elif state == Qt.CheckState.Checked:
            stateFormatted = '1'
        cursor.execute(
            "update tblquery set result = {0}::bit(1) where queryid={1}".format(stateFormatted, str(queryID)))

        self.connection.commit()
        cursor.close()
        pass

    def selectAllModelIDInfo(self):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT modelID, \"fileName\", createDate, description FROM tblUppaal")
        rec = cursor.fetchall()
        cursor.close()
        return rec

    def selectUppaalModelInfo(self, modelID):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT modelID, \"fileName\", createDate, description, xmlFile  FROM tblUppaal "
            "WHERE modelId = %s",
            (str(modelID)))
        rec = cursor.fetchall()
        cursor.close()
        return rec[0]

    def selectUppaalModelXml(self, modelID):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT xmlFile  FROM tblUppaal "
            "WHERE modelId = {0}".format(str(modelID)))
        rec = cursor.fetchall()
        cursor.close()
        return rec[0][0]
