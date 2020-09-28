from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time
import traceback, sys
import random

class Worker(QRunnable):
    '''
    Worker Thread
    '''

    running = True

    def __init__(self):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialize the independent thread
        '''
        print("Starting thread")
        while Worker.running:
            result = 2 + 2 + random.randint(0, 10)
            # self.signals.result.emit(result)
            print(result)
            time.sleep(0.3)
        print("Thread Complete")

        self.signals.finished.emit()

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread

    Suported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum {} threads".format(self.threadpool.maxThreadCount()))

        self.counter = 0

        layout = QVBoxLayout()

        self.l = QLabel("Start")
        b = QPushButton("DANGER!")
        b.pressed.connect(self.start_thread)

        b2 = QPushButton("stop_threads")
        b2.pressed.connect(self.stop_threads)

        layout.addWidget(self.l)
        layout.addWidget(b)
        layout.addWidget(b2)


        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

    def change_message(self, val):
        self.l.setText("Thread val: {}".format(val))

    def stop_threads(self):
        print("Stopping Threads")
        Worker.running = False

    def start_thread(self):
        worker = Worker()
        worker.signals.result.connect(self.change_message)
        self.threadpool.start(worker)

    def closeEvent(self, event):

        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            print("Shutting down threads")
            self.stop_threads()
            time.sleep(1)
            event.accept()
        else:
            event.ignore()


app = QApplication([])
window = MainWindow()
app.exec_()
