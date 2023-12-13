from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from mycanvas import *
from mymodel import *
import sys

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100,100,600,400)
        self.setWindowTitle("MyGLDrawer")
        self.setWindowIcon(QIcon('icons/window'))
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)
        # create a model object and pass to canvas
        self.model = MyModel()
        self.canvas.setModel(self.model)

        self.dialog = MyDialog()
        self.dialog2 = RectDialog() # Rectangle generator
        self.boundaryDialog = BoundaryDialog()

        # create a Toolbar
        tb = self.addToolBar("File")
        
        fit = QAction(QIcon("icons/fit.png"),"fit",self)
        tb.addAction(fit)
        
        clearAll = QAction(QIcon("icons/clear.png"), "clear",self)
        tb.addAction(clearAll)

        points = QAction(QIcon("icons/dots.png"),"points",self)
        tb.addAction(points)

        rectangle = QAction(QIcon("icons/rectangle.png"),"rectangle",self)
        tb.addAction(rectangle)

        boundary = QAction(QIcon("icons/boundary.png"), "boundary", self)
        tb.addAction(boundary)

        debug = QAction(QIcon("icons/debug.png"),"debug",self)
        tb.addAction(debug)

        tb.actionTriggered[QAction].connect(self.tbpressed)

    def tbpressed(self,a):
        if a.text() == "fit":
            self.canvas.fitWorldToViewport()
        if a.text() == "clear":
            self.canvas.clearAll()
        
        if a.text() == "points":
            self.dialog.exec_()
            self.canvas.pointCloud(self.dialog.getHPoints(), self.dialog.getVPoints())

        if a.text() == "debug":
            self.canvas.printPoints()

        if a.text() == "boundary":
            self.boundaryDialog.exec_()
            self.canvas.addBoundaryConditions(self.boundaryDialog.getValue())
            
        if a.text() == "rectangle":	
            self.dialog2.exec_()
            self.canvas.rectangle(self.dialog2.getHeight(), self.dialog2.getWidth())

        
class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.hpoints = 0
        self.vpoints = 0
        
        self.botaoPontos = QPushButton("Ok", self)
        self.botaoCancelar = QPushButton("Cancel", self)

        self.botaoCancelar.clicked.connect(self.exitDialog)
        self.botaoPontos.clicked.connect(self.callCloud)

        self.vLabel = QLabel("Pontos na Vertical")
        self.hLabel = QLabel("Pontos na Horizontal")
           
        self.vLine = QLineEdit()
        self.hLine = QLineEdit()
          
        self.grid = QGridLayout()
          
        self.grid.addWidget(self.vLabel, 0, 0)
        self.grid.addWidget(self.hLabel, 0, 1)
        self.grid.addWidget(self.vLine, 1, 0)
        self.grid.addWidget(self.hLine, 1, 1)
        self.grid.addWidget(self.botaoPontos, 2, 0)
        self.grid.addWidget(self.botaoCancelar, 2, 1)
            

        self.setLayout(self.grid)

        self.setWindowTitle("Point Cloud Generator")
        self.setWindowModality(Qt.ApplicationModal)
        

    def exitDialog(self):
        self.close()

    def callCloud(self):
        self.hpoints = int(self.hLine.text())
        self.vpoints = int(self.vLine.text())
        self.close()

        
    def getHPoints(self):
        return (self.hpoints)

    def getVPoints(self):
        return (self.vpoints)
       
    
class BoundaryDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.value = 0

        self.botaoOk = QPushButton("Ok", self)
        self.botaoOk.clicked.connect(self.setBCValue)

        self.botaoCancelar = QPushButton("Cancel", self)
        self.botaoCancelar.clicked.connect(self.exitDialog)

        self.label = QLabel("Valor da Condição de Contorno")

        self.valueLine = QLineEdit()

        self.grid = QGridLayout()
        self.grid.addWidget(self.label, 0, 0)
        self.grid.addWidget(self.valueLine, 0, 1)
        self.grid.addWidget(self.botaoOk, 1, 0)
        self.grid.addWidget(self.botaoCancelar, 1, 1)

        self.setLayout(self.grid)

        self.setWindowTitle("Condições de Contorno")
        self.setWindowModality(Qt.ApplicationModal)
        
    def setBCValue(self):
        self.value = int(self.valueLine.text())
        self.close()

    def exitDialog(self):
        self.close()
    
    def getValue(self):
        return self.value


class RectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.width = 0
        self.height = 0
        
        self.botaoRetangulo = QPushButton("Ok", self)
        self.botaoCancelar = QPushButton("Cancel", self)

        self.botaoCancelar.clicked.connect(self.exitDialog)
        self.botaoRetangulo.clicked.connect(self.callCloud)

        self.heightLabel = QLabel("Altura da placa")
        self.widthLabel = QLabel("Largura da Placa")
           
        self.heightLine = QLineEdit()
        self.widthLine = QLineEdit()
          
        self.grid = QGridLayout()
          
        self.grid.addWidget(self.heightLabel, 0, 0)
        self.grid.addWidget(self.widthLabel, 0, 1)
        self.grid.addWidget(self.widthLine, 1, 0)
        self.grid.addWidget(self.heightLine, 1, 1)
        self.grid.addWidget(self.botaoRetangulo, 2, 0)
        self.grid.addWidget(self.botaoCancelar, 2, 1)
            

        self.setLayout(self.grid)

        self.setWindowTitle("Rectangle Drawer")
        self.setWindowModality(Qt.ApplicationModal)
        

    def exitDialog(self):
        self.close()

    def callCloud(self):
        self.width = int(self.widthLine.text())
        self.height = int(self.heightLine.text())
        self.close()

        
    def getWidth(self):
        return (self.width)

    def getHeight(self):
        return (self.height)       
        