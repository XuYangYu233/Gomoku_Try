from PyQt5.QtWidgets import QApplication
from window import GomokuWindow
import sys


def main():
    app = QApplication(sys.argv)
    ex = GomokuWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
