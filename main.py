
from uiConnection import UIConnection
from PyQt5.QtWidgets import *
import sys

from DataBaseConnection import DataBaseConnection as DBC

DATABASE_NAME = "UPPAALDB"
USER_NAME = "postgres"
PASSWORD = "4458771"


def start():
    qApplication = QApplication(sys.argv)
    win = UIConnection(DBC(DATABASE_NAME, USER_NAME, PASSWORD))
    win.show()
    sys.exit(qApplication.exec())


if __name__ == "__main__":
    start()
