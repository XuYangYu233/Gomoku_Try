from PyQt5 import QtWidgets
from window import GomokuWindow
import sys


def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = GomokuWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
