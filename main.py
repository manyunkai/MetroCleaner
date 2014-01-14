# -*-coding:utf-8 -*-
'''
Created on 2014-1-13

@author: Danny
DannyWork Project
'''

import sys
import threading
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject

from ui import UiDialog

LOCALAPPDATA = os.getenv('LOCALAPPDATA')
PAKAGE_HOME = os.path.join(LOCALAPPDATA, 'Packages')


class Cleaner(QObject, threading.Thread):
    callback = QtCore.pyqtSignal(int, int, bool)

    def __init__(self, clean_cache, clean_cookies, clean_history, scan_only=False):
        super().__init__()

        self.options = clean_cache, clean_cookies, clean_history
        self.scan_only = scan_only

    def delete_empty_directories(self, working_dir):
        for item in os.listdir(working_dir):
            current_path = os.path.join(working_dir, item)
            if os.path.isdir(current_path):
                try:
                    os.rmdir(current_path)
                except OSError:
                    self.delete_empty_directories(current_path)
                try:
                    os.rmdir(current_path)
                except OSError:
                    pass

    def run(self):
        cleanning = []
        for name, is_clean in zip(['INetCache', 'INetCookies', 'INetHistory'], self.options):
            if is_clean:
                cleanning.append(name)

        count = 0
        size = 0

        for d in os.listdir(PAKAGE_HOME):
            AC_HOME = os.path.join(PAKAGE_HOME, d, 'AC')
            if not os.path.exists(AC_HOME):
                continue

            for name in cleanning:
                root = os.path.join(AC_HOME, name)
                if os.path.exists(root):
                    for curdir, directories, files in os.walk(root):
                        count += len(files)
                        for fn in files:
                            ap = os.path.join(root, curdir, fn)
                            size += os.path.getsize(os.path.join(root, curdir, ap))
                            if not self.scan_only:
                                try:
                                    os.remove(ap)
                                except WindowsError:
                                    pass
                    if not self.scan_only:
                        self.delete_empty_directories(root)

        self.callback.emit(count, size, False == self.scan_only)


class MainWindow(QtWidgets.QMainWindow, UiDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui(self)

        self.scan_btn.clicked.connect(self.scan)
        self.clr_btn.clicked.connect(self.clean)

    def init_cleaner(self, scan_only):
        self.cleaner = Cleaner(self.c_1.isChecked(), self.c_2.isChecked(),
                               self.c_3.isChecked(), scan_only)
        self.cleaner.callback.connect(self.report)

    def scan(self):
        self.report_txt.setText('请稍后...')
        self.init_cleaner(True)
        self.cleaner.run()

    def clean(self):
        self.report_txt.setText('请稍后...')
        self.init_cleaner(False)
        self.cleaner.run()

    def report(self, count, size, cleaned):
        if cleaned:
            self.report_txt.setText('{0}个文件已清理，共计{1:.2f}M。'.format(count, size / 1024 / 1024))
        else:
            self.report_txt.setText('{0}个文件可清理，可节约{1:.2f}M空间。'.format(count, size / 1024 / 1024))


app = QtWidgets.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
