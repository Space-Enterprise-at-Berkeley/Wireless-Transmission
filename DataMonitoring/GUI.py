import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import random, time, sys, os
from datetime import datetime

# Contains Thread Definitions
from GUI_threads import *

sensor_type_to_name = {
        "low_pt" : "Low Pressure",
        "high_pt" : "High Pressure",
        "temp" : "Temperature"
}

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100, fig=None, nrows=None, ncols=None, index=None):
        if fig:
            self.axes = fig.add_subplot(nrows,ncols,index)
        else:
            fig = Figure(figsize=(width, height), dpi=dpi)
            # nrows ncols index
            self.axes = fig.add_subplot(1,1,1)

        super(MplCanvas, self).__init__(fig)

class StatusGroup(QWidget):
    def __init__(self, name, *args, **kwargs):
        super(StatusGroup, self).__init__(*args, **kwargs)

        self.name = name
        layout = QGridLayout()

        self.open_btn = QPushButton("OPEN")
        self.open_btn.setFont(QFont("Helvetica Neue"))
        self.open_btn.clicked.connect(self.open_act)
        self.close_btn = QPushButton("CLOSE")
        self.close_btn.setFont(QFont("Helvetica Neue"))
        self.close_btn.clicked.connect(self.close_act)
        self.status = Status()

        layout.addWidget(self.open_btn,0,0)
        layout.addWidget(self.close_btn,1,0)
        layout.addWidget(self.status,0,1,2,1)

        self.setLayout(layout)
        self.setMaximumHeight(80)

    def open_act(self):
        if self.status.closed:
            print("Opening " + self.name)
            self.status.switch()

    def close_act(self):
        if not self.status.closed:
            print("Closing " + self.name)
            self.status.switch()

class Status(QWidget):
    def __init__(self, *args, **kwargs):
        super(Status, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

        self.closed_txt = "<font color='White'>CLOSED</font>"
        self.open_txt = "  OPEN"
        self.color = 'red'
        self.closed = True
        self.set_color(self.color)


        layout = QVBoxLayout()
        self.l = QLabel(self.closed_txt)
        labelfont = QFont("Helvetica Neue", 14, QFont.Bold)
        labelfont.setLetterSpacing(QFont.PercentageSpacing, 105)
        self.l.setFont(labelfont)

        layout.addWidget(self.l, Qt.AlignCenter)

        self.setLayout(layout)

        self.setMaximumHeight(60)
        self.setMinimumWidth(90)
        self.setMaximumWidth(90)

    def switch(self):
        if self.color == 'red':
            # Change to open (green)
            self.color = 'green'
            self.l.setText(self.open_txt)
            self.set_color("#60d936") # Light Green
            self.closed = False
            # TODO: VALVE OPENING ACTION
        elif self.color == 'green':
            # Change to closed (red)
            self.color = 'red'
            self.l.setText(self.closed_txt)
            self.set_color("#ee230c") # Bright Red
            self.closed = True
            # TODO: VALVE CLOSING ACTION

    def set_color(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class MainWindow(QMainWindow):

    def __init__(self, file_path, sensor_types, sensor_nums, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.sensor_types = sensor_types.copy()
        self.sensor_nums = sensor_nums.copy()


        mainlayout = QGridLayout()

        # row 0

        title = QLabel("Ground Dashboard")
        titlefont = QFont("Lucida Grande",20, QFont.Bold)
        title.setFont(titlefont)

        mainlayout.addWidget(title,0,0,1,2)

        # ---------- Valves -----------------------------------------

        # Dynamically create StatusGroup objects and formatted labels for all valves

        valves = ["Pressurant", "LOX GEMS", "Propane GEMS", "LOX 2-WAY",
        "Propane 2-WAY", "LOX 5-WAY", "Propane 5-WAY"]
        StatusGroups = {}
        for i,name in enumerate(valves):
            StatusGroups[name] = StatusGroup(name)

        label_names = ['Pressurant', 'LOX', 'Propane', 'GEMS', '2-WAY', '5-WAY']
        valve_labels = {}
        for i,name in enumerate(label_names):
            label = QLabel(name)
            font = QFont("Lucida Grande",14, QFont.Bold)
            label.setFont(font)
            valve_labels[name] = label

        # Put StatusGroup objects and labels in valve GridLayout, as outlined in rough draft diagram

        valve_container = QWidget()
        valve_layout = QGridLayout()
        # row 0 & 1
        valve_layout.addWidget(valve_labels["Pressurant"],0,1,1,2,Qt.AlignCenter)
        valve_layout.addWidget(StatusGroups['Pressurant'],1,1,1,2,Qt.AlignCenter)
        # row 2
        valve_layout.addWidget(valve_labels["LOX"],2,1,Qt.AlignCenter)
        valve_layout.addWidget(valve_labels["Propane"],2,2,Qt.AlignCenter)
        # row 3
        valve_layout.addWidget(valve_labels["GEMS"],3,0)
        valve_layout.addWidget(StatusGroups['LOX GEMS'],3,1)
        valve_layout.addWidget(StatusGroups['Propane GEMS'],3,2)
        # row 4
        valve_layout.addWidget(valve_labels["2-WAY"],4,0)
        valve_layout.addWidget(StatusGroups['LOX 2-WAY'],4,1)
        valve_layout.addWidget(StatusGroups['Propane 2-WAY'],4,2)
        # row 5
        valve_layout.addWidget(valve_labels["5-WAY"],5,0)
        valve_layout.addWidget(StatusGroups['LOX 5-WAY'],5,1)
        valve_layout.addWidget(StatusGroups['Propane 5-WAY'],5,2)

        valve_container.setLayout(valve_layout)
        mainlayout.addWidget(valve_container,1,0)

        # ---------- Graphs -----------------------------------------

        # Remnants from before graphing was moved into separate thread
        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        # self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        # sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        # mainlayout.addWidget(self.canvas,1,1,1,1)

        # n_data = 50
        # self.xdata = list(range(n_data))
        # self.ydata = [random.randint(0, 10) for i in range(n_data)]
        #
        # self._plot_ref = None
        # self.update_plot()

        # Timer for initial testing with random noise
        # self.timer = QTimer()
        # self.timer.setInterval(30)
        # self.timer.timeout.connect(self.update_plot)
        # self.timer.start()

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        # self.graphs = []
        # self.graphs.append(MplCanvas(self, width=5, height=4, dpi=100))


        # Dynamically create the correct number of graphs based off input numbers
        graphWidget = QTabWidget()
        self.graphs = {}
        self.figures = {}
        for sensor in self.sensor_types:
            # TODO: make graph allocation more generalized,
            # since we may have more than 6 of a given type of sensor (temp?)
            self.graphs[sensor] = []
            num = self.sensor_nums[sensor]
            tabWidget = QWidget()
            tabGrid = QGridLayout()
            if num == 1:
                grid_pos = self.generate_pos(1,1)
            elif num <= 4:
                grid_pos = self.generate_pos(2,2)
            else:
                grid_pos = self.generate_pos(2,3)

            # fig = Figure(figsize=(5, 4), dpi=100)
            # self.figures[sensor] = fig
            for i in range(num):
                canvas = MplCanvas(self,width=5, height=4, dpi=100)
                self.graphs[sensor].append(canvas)
                row,col = next(grid_pos)
                tabGrid.addWidget(canvas,row,col)
            tabWidget.setLayout(tabGrid)
            # else:

            graphWidget.addTab(tabWidget, sensor_type_to_name[sensor])
        # graphWidget.addTab(QLabel("Beans"),"Beans")
        mainlayout.addWidget(graphWidget,1,1,1,1)


        # Creates a threadpool to handle scheduled threads
        self.threadpool = QThreadPool()

        # Sets `beans` to be called every time serialThread sends a
        # 'data' signal
        self.serialThread = SerialThread(self.graphs)
        self.serialThread.signals.data.connect(self.beans)
        self.threadpool.start(self.serialThread)


        # ---------- Display ----------------------------------------

        # Add layout to a dummy QWidget, and set it as the Central Widget
        widget = QWidget()
        widget.setLayout(mainlayout)

        self.setCentralWidget(widget)


    '''Old method from when graph was in main object, not in separate thread'''
    def update_plot(self, data=None):
        if data is None:
            self.ydata = self.ydata[1:] + [random.randint(0, 10)]
        else:
            self.ydata = self.ydata[1:] + [data]

        if self._plot_ref is None:
            plot_refs = self.canvas.axes.plot(self.xdata, self.ydata, 'b')
            self._plot_ref = plot_refs[0]
        else:
            self._plot_ref.set_ydata(self.ydata)

        self.canvas.draw()

    def beans(self, num):
        print("{} beans".format(num))

    def generate_pos(self,nrows,ncols):
        rows = 0
        cols = 0
        while rows < nrows:
            while cols < ncols:
                yield (rows,cols)
                cols += 1
            cols = 0
            rows += 1

    # Override close event to stop threads
    def closeEvent(self, event):
        print("Shutting down threads")
        self.serialThread.stop_thread()
        time.sleep(0.2)
        event.accept()


class Entry(QMainWindow):
    def __init__(self, parent=None):
        super(Entry, self).__init__(parent)

        self.sensors = ["low_pt", "high_pt", "temp"]
        self.sensor_nums = {}

        mainlayout = QGridLayout()

        # row 0

        title = QLabel("Dashboard Settings")
        title.setFont(QFont("Lucida Grande",20, QFont.Bold))

        mainlayout.addWidget(title,0,0,1,2)

        self.storage_path = 'data'

        label_names = ['Base Filename:', 'Folder:', 'File Path:','# Low PTs:', '# High PTs:', '# Temp Sensors:']
        label_ids = ['base_file', 'folder', 'file_path', 'low_pt', 'high_pt', 'temp']
        self.labels = {}
        line_edit_defaults = ['waterflow', self.storage_path, '', '0', '0','0']
        self.line_edits = {}
        label_font = QFont("Lucida Grande",14, QFont.Bold)
        for i,name in enumerate(label_names):
            label = QLabel(name)
            label.setFont(label_font)
            self.labels[label_ids[i]] = label
            mainlayout.addWidget(label,i+1,0)
            # create a QLineEdit for all rows except 'File Path'
            if name =='File Path:':
                line_edit = QLabel('')
                self.labels['file_path_text'] = line_edit
            else:
                line_edit = QLineEdit()
                line_edit.setText(line_edit_defaults[i])
                self.line_edits[label_ids[i]] = line_edit
            mainlayout.addWidget(line_edit,i+1,1)

        # Set various object settings
        self.line_edits['low_pt'].setValidator(QIntValidator(0,5))
        self.line_edits['high_pt'].setValidator(QIntValidator(0,2))
        self.line_edits['temp'].setValidator(QIntValidator(0,7))
        self.line_edits['base_file'].textChanged.connect(self.update_full_file_path)
        self.line_edits['folder'].textChanged.connect(self.update_full_file_path)
        self.update_full_file_path()


        self.launchButton = QPushButton("Launch Dashboard")
        mainlayout.addWidget(self.launchButton,len(label_names) + 1,0,1,2,Qt.AlignCenter)
        self.launchButton.clicked.connect(self.on_launchButton_clicked)

        # Dummy container widget
        widget = QWidget()
        widget.setLayout(mainlayout)
        self.setCentralWidget(widget)


    def update_full_file_path(self):
        self.file_name = self.full_file_name(self.line_edits['base_file'].text())
        self.folder_name = self.line_edits['folder'].text()
        self.labels['file_path_text'].setText(os.path.join(self.folder_name,self.file_name))

    '''Given a base file name BASE, will return the correct full name "BASE_MM-DD-YY_#{i}"'''
    def full_file_name(self, base):
        return "{}_{}.csv".format(base,datetime.now().strftime('%m-%d-%y_%H:%M'))

    def update_sensor_vals(self):
        for sensor_type in self.sensors:
            val = int(self.line_edits[sensor_type].text())
            if val > 0:
                self.sensor_nums[sensor_type] = val


    def on_launchButton_clicked(self):
        if not os.path.isdir(self.folder_name):
            message = '''<p>The given folder to save data in does not exist:</p>    {}
                    <p>Would you like to create the a new folder with the given name?</p>'''.format(folder_name)
            msgBox = QMessageBox(QMessageBox.Warning,
                    "QMessageBox.warning()", message,
                    QMessageBox.NoButton, self)
            msgBox.addButton("Create", QMessageBox.AcceptRole)
            msgBox.addButton("Cancel", QMessageBox.RejectRole)
            if msgBox.exec_() == QMessageBox.AcceptRole:
                os.mkdir(self.folder_name)
            else:
                return

        self.update_sensor_vals()
        self.mainWindow = MainWindow(self.labels['file_path_text'].text(), list(self.sensor_nums.keys()), self.sensor_nums)
        self.mainWindow.show()
        self.hide()


def main():
    app = QApplication(sys.argv)
    w = Entry()
    w.show()
    app.exec_()

if __name__ == '__main__':
    main()