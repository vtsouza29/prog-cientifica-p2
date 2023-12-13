from PyQt5 import QtCore, QtOpenGL
from PyQt5.QtWidgets import *
from OpenGL.GL import *
from hetool import HeController, HeModel, HeView, Tesselation, Point
import numpy as np
import math
import json
from datetime import datetime

class MyCanvas(QtOpenGL.QGLWidget):
    def __init__(self):
        super(MyCanvas, self).__init__()
        self.m_model = None
        self.m_w = 0 # width: GL canvas horizontal size
        self.m_h = 0 # height: GL canvas vertical size
        self.m_L = -1000.0
        self.m_R = 1000.0
        self.m_B = -1000.0
        self.m_T = 1000.0
        self.list = None

        self.nPts = 0

        self.boundGrid = []
        self.gridPoints = []

        self.selectedPoints = []

        self.boundaryConditions = np.array([])

        self.pointsDict = {}
        self.filename = "./output.json"

        self.m_buttonPressed = False
        self.m_buttonPressedF = False

        self.m_pt0 = QtCore.QPoint(0,0)
        self.m_pt1 = QtCore.QPoint(0,0)

        self.m_ptf0 = QtCore.QPoint(0,0)
        self.m_ptf1 = QtCore.QPoint(0,0)

        self.tol = 0.1
        self.hemodel = HeModel()
        self.heview = HeView(self.hemodel)
        self.hecontroller = HeController(self.hemodel)

    def initializeGL(self):
        #glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_LINE_SMOOTH)
        self.list = glGenLists(1)
        
        
    def resizeGL(self, _width, _height):
        # store GL canvas sizes in object properties
        self.m_w = _width
        self.m_h = _height
        # Setup world space window limits (bounding box?)
        # self.scaleWorldWindow(1.0)

        if(self.m_model==None)or(self.m_model.isEmpty()): self.scaleWorldWindow(1.0)
        else:
            self.m_L,self.m_R,self.m_B,self.m_T = self.m_model.getBoundBox()
            self.scaleWorldWindow(1.1)

        # setup the viewport to canvas dimensions
        glViewport(0, 0, self.m_w, self.m_h)
        # reset the coordinate system
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # establish the clipping volume by setting up an
        # orthographic projection
        glOrtho(0.0, self.m_w, 0.0, self.m_h, -1.0, 1.0)
        # setup display in model coordinates
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        # clear the buffer with the current clear color
        glClear(GL_COLOR_BUFFER_BIT)
        # draw the model
        # if (self.m_model==None)or(self.m_model.isEmpty()):      
        #     return

        glCallList(self.list)
        glDeleteLists(self.list, 1)
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)

        # Display model polygon RGB color at its vertices
        # interpolating smoothly the color in the interior
        # verts = self.m_model.getVerts()
        # glShadeModel(GL_SMOOTH)
        # glColor3f(0.0, 1.0, 0.0) # green
        # glBegin(GL_TRIANGLES)
        # for vtx in verts:
        #     glVertex2f(vtx.getX(), vtx.getY())
        # glEnd()

        

        # Desenho dos pontos coletados
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
     

        if not((self.m_model == None) and (self.m_model.isEmpty())):
            verts = self.m_model.getVerts()
            glColor3f(0.0, 1.0, 0.0) # green
            # glBegin(GL_TRIANGLES)
            # for vtx in verts:
            #     glVertex2f(vtx.getX(), vtx.getY())
            # glEnd()
            curves = self.m_model.getCurves()
            glColor3f(0.0, 0.0, 1.0) # blue
            glBegin(GL_LINES)
            for curv in curves:
                glVertex2f(curv.getP1().getX(), curv.getP1().getY())
                glVertex2f(curv.getP2().getX(), curv.getP2().getY())
            glEnd()

        if not(self.heview.isEmpty()):
            # print("teste")
            patches = self.heview.getPatches()
            # print(len(patches))
            glColor3f(0.5, 0.0, 1.0)
            for pat in patches:
                triangs = Tesselation.tessellate(pat.getPoints())
                for triang in triangs:
                    glBegin(GL_TRIANGLES)
                    for pt in triang:
                        glVertex2d(pt.getX(), pt.getY())
                    glEnd()
                
            segments = self.heview.getSegments()
            glColor3f(0.0, 1.0, 1.0)
            # print(len(segments))
            for curv in segments:
                ptc = curv.getPointsToDraw()
                # glColor3f(0.0, 1.0, 1.0) # 
                glBegin(GL_LINES)
                
                glVertex2f(ptc[0].getX(), ptc[0].getY())
                glVertex2f(ptc[1].getX(), ptc[1].getY())
                
                glEnd()

            # verts = self.heview.getPoints()
            # glPointSize(4)
            # glBegin(GL_POINTS)
            # for vert in verts:
            #     glColor3f(0.0, 1.0, 0.0)
            #     glVertex2f(vert.getX(), vert.getY())
            # glEnd()
            
            
            glPointSize(4)
            glBegin(GL_POINTS)
            for vert in self.gridPoints:
                if vert in self.selectedPoints:
                    glColor3f(0.0, 0, 1.0)
                    glVertex2f(vert.getX(), vert.getY())
                else:
                    glColor3f(1.0, 0.0, 0)
                    glVertex2f(vert.getX(), vert.getY())
            glEnd()

            # Desenhando Todos os Pontos do Grid
            # glColor3f(1.0, 1.0, 1.0)
            # glPointSize(3)
            # glBegin(GL_POINTS)
            # for p in self.boundGrid:
            #     glVertex2f(p.getX(), p.getY())
            # glEnd()

            # Desenho dos eixos de coordenadas
            ### R
            glColor3f(1.0, 0.0, 0.0)
            glPointSize(4)
            glBegin(GL_POINTS)
            glVertex2f(0, 0)
            glEnd()
            ### G
            glColor3f(0.0, 1.0, 0.0)
            glPointSize(4)
            glBegin(GL_POINTS)
            glVertex2f(0, 1)
            glEnd()
            ### B
            glColor3f(0.0, 0.0, 1.0)
            glPointSize(4)
            glBegin(GL_POINTS)
            glVertex2f(1, 0)
            glEnd()
                
        
        if(self.m_buttonPressedF):
            pt0f_U = self.convertPtCoordsToUniverse(self.m_ptf0)
            pt1f_U = self.convertPtCoordsToUniverse(self.m_ptf1)

            glColor3f(1.0, 1.0, 0.0)
            glBegin(GL_LINE_STRIP)
            glVertex2f(pt0f_U.x(), pt0f_U.y())
            glVertex2f(pt1f_U.x(), pt0f_U.y())
            glVertex2f(pt1f_U.x(), pt1f_U.y())
            glVertex2f(pt0f_U.x(), pt1f_U.y())
            glVertex2f(pt0f_U.x(), pt0f_U.y())
            glEnd()


        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(pt0_U.x(), pt0_U.y())
        glVertex2f(pt1_U.x(), pt1_U.y())
        glEnd()

        glEndList()

        
    def setModel(self,_model):
        self.m_model = _model

    def fitWorldToViewport(self):  #atualizar para o modelo novo
        print("fitWorldToViewport")
        if self.m_model == None:
            return
        self.m_L,self.m_R,self.m_B,self.m_T=self.m_model.getBoundBox()
        self.scaleWorldWindow(1.10)
        self.update()

    def scaleWorldWindow(self,_scaleFac):
        # Compute canvas viewport distortion ratio.
        vpr = self.m_h / self.m_w
        # Get current window center.
        cx = (self.m_L + self.m_R) / 2.0
        cy = (self.m_B + self.m_T) / 2.0
        # Set new window sizes based on scaling factor.
        sizex = (self.m_R - self.m_L) * _scaleFac
        sizey = (self.m_T - self.m_B) * _scaleFac
        # Adjust window to keep the same aspect ratio of the viewport.
        if sizey > (vpr*sizex):
            sizex = sizey / vpr
        else:
            sizey = sizex * vpr

        self.m_L = cx - (sizex * 0.5)
        self.m_R = cx + (sizex * 0.5)
        self.m_B = cy - (sizey * 0.5)
        self.m_T = cy + (sizey * 0.5)
        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)

    def panWorldWindow(self, _panFacX, _panFacY):
        # Compute pan distances in horizontal and vertical directions.
        panX = (self.m_R - self.m_L) * _panFacX
        panY = (self.m_T - self.m_B) * _panFacY
        # Shift current window.
        self.m_L += panX
        self.m_R += panX
        self.m_B += panY
        self.m_T += panY
        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)

    def convertPtCoordsToUniverse(self, _pt):
        dX = self.m_R - self.m_L
        dY = self.m_T - self.m_B
        mX = _pt.x() * dX / self.m_w
        mY = (self.m_h - _pt.y()) * dY / self.m_h
        x = self.m_L + mX
        y = self.m_B + mY
        return QtCore.QPointF(x,y)


    def mousePressEvent(self, event):
        # print(event.button())
        if event.button() == 1:
            # print("Botão esquerdo pressionado!")
            self.m_buttonPressed = True
            self.m_pt0 = event.pos()
        else:
            # print("Botão direito pressionado")
            self.m_buttonPressedF = True
            self.m_ptf0 = event.pos()
            # print(event.pos())
            

    def mouseMoveEvent(self, event):
        if self.m_buttonPressed:
            self.m_pt1 = event.pos()
            self.update()

        if self.m_buttonPressedF:
            self.m_ptf1 = event.pos()
            self.update()


    def mouseReleaseEvent(self, event):

        if event.button() == 1:
            # print(self.m_pt0.x(), self.m_pt0.y())
            # print(self.m_pt1.x(), self.m_pt1.y())
            pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
            pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)

            tol = 0.5
            snapped1, xs1, ys1 = self.heview.snapToPoint(pt0_U.x(), pt0_U.y(), tol)
            snapped2, xs2, ys2 = self.heview.snapToPoint(pt1_U.x(), pt1_U.y(), tol)
            # print(snapped1, xs1, ys1)
            # print(snapped2, xs2, ys2)

            if self.heview.isEmpty():
                self.hecontroller.insertSegment([pt0_U.x(),pt0_U.y(), pt1_U.x(),pt1_U.y()], self.tol)
            else:
                try:
                    if snapped1 and not snapped2:
                        self.hecontroller.insertSegment([xs1, ys1, pt1_U.x(),pt1_U.y()], self.tol)
                    elif snapped2 and not snapped1:
                        self.hecontroller.insertSegment([pt0_U.x(),pt0_U.y(), xs2, ys2], self.tol)
                    elif snapped1 and snapped2:
                        self.hecontroller.insertSegment([xs1, ys1, xs2, ys2], self.tol)
                    else: 
                        self.hecontroller.insertSegment([pt0_U.x(),pt0_U.y(), pt1_U.x(),pt1_U.y()], self.tol)
                except:
                    self.hecontroller.insertSegment([pt0_U.x(),pt0_U.y(), pt1_U.x(),pt1_U.y()], self.tol)

            self.m_buttonPressed = False
            self.m_pt0 = QtCore.QPoint(0,0)
            self.m_pt1 = QtCore.QPoint(0,0)
            self.update()
            self.paintGL()
        else:
            ptf0_U = self.convertPtCoordsToUniverse(self.m_ptf0)
            ptf1_U = self.convertPtCoordsToUniverse(self.m_ptf1)
            self.m_buttonPressedF = False
            self.selectedPoints = []

            for point in self.gridPoints:
                xP = point.getX()
                yP = point.getY()

                # print(f" ({xP}, {yP})    ({ptf0_U.x()}, {ptf0_U.y()})     ({ptf1_U.x()}, {ptf1_U.y()})")
                # print(min(ptf0_U.y(), ptf1_U.y()) <= yP <= max(ptf0_U.y(), ptf1_U.y()), min(ptf0_U.x(), ptf1_U.x()) <= yP <= max(ptf0_U.x(), ptf1_U.x()))
               
                if (min(ptf0_U.x(), ptf1_U.x()) <= xP <= max(ptf0_U.x(), ptf1_U.x()) and min(ptf0_U.y(), ptf1_U.y()) <= yP <=  max(ptf0_U.y(), ptf1_U.y())) == True:
                    self.selectedPoints.append(point)

            print(len(self.selectedPoints))

            self.m_pt0f = QtCore.QPoint(0,0)
            self.m_pt1f = QtCore.QPoint(0,0)

            self.update()
            self.paintGL()

    def addBoundaryConditions(self, value):
      
        if self.boundaryConditions.size == 0:
            self.boundaryConditions = np.zeros((len(self.gridPoints), 2))
        
        for i in range(len(self.gridPoints)):
            if self.gridPoints[i] in self.selectedPoints:
                self.boundaryConditions[i, 0] = 1
                self.boundaryConditions[i, 1] = value
                
            self.pointsDict["bc"] = self.boundaryConditions.tolist()

            with open(self.filename, 'w') as jsonfile:
                json.dump(self.pointsDict, jsonfile)
        

        for i in range(len(self.boundaryConditions)):
            print(self.boundaryConditions[i])
                

    def rectangle(self, width, height):
        tol = 0.1
        # print(height, width)
        
        self.hecontroller.insertSegment([1, 1, width, 1], tol)
        self.hecontroller.insertSegment([1, 1, 1, height], tol)
        self.hecontroller.insertSegment([1, height, width, height], tol)
        self.hecontroller.insertSegment([width, height, width, 1], tol)

        self.fitWorldToViewport()
        self.paintGL()

    def pointCloud(self, hpoints, vpoints):
        xmin, xmax, ymin, ymax = self.heview.getBoundBox()
        xmin += 0.01
        xmax -= 0.01
        ymin += 0.01
        ymax -= 0.01

        dx = (abs(xmax) - abs(xmin))/(hpoints-1)
        dy = (abs(ymax) - abs(ymin))/(vpoints-1)
        tol = 0.2

        # nPts = 0
        # print(xmax, xmin, dx)

        patches = self.heview.getPatches()
        self.pointsDict = {"coords":[], "conect":[], "n":0, "h":0, "k":0, "bc":[], "hpoints":0, "vpoints":0}
        
        self.pointsDict["h"] = dx
        self.pointsDict["k"] = dy
        self.pointsDict["hpoints"] = hpoints
        self.pointsDict["vpoints"] = vpoints

        for i in np.linspace(xmin, xmax, hpoints, endpoint=True):
            for j in np.linspace(ymin, ymax, vpoints, endpoint=True):
                point = Point(i, j)
                self.boundGrid.append(point)
                for patch in patches:
                    if patch.isPointInside(point):
                        self.hecontroller.insertPoint([i, j], tol)
                        self.gridPoints.append(point)
                        coords = (i,j)
                        self.pointsDict['coords'].append(coords)
                        self.nPts += 1
        self.pointsDict["n"] = self.nPts
        print(len(self.gridPoints))         
        conect = np.zeros((len(self.boundGrid), 4)) 

        # Primeiro monto a matriz conect para todos os pontos do grid retangular
        for i in range(len(conect)):
            leftNeigh = i - vpoints
            rightNeigh = i + vpoints
            topNeigh = i + 1
            bottomNeigh = i - 1

            if leftNeigh >= 0 and leftNeigh <= len(conect)-1:
                leftNeigh += 1                                 
                conect[i][1] = leftNeigh

            if bottomNeigh >= 0 and bottomNeigh <= len(conect)-1 and i%vpoints!=0:
                bottomNeigh += 1
                conect[i][2] = bottomNeigh
                
            if topNeigh >= 0 and topNeigh <= len(conect)-1 and topNeigh%vpoints !=0:
                topNeigh += 1
                conect[i][3] = topNeigh
                
            if rightNeigh >= 0 and rightNeigh <= len(conect)-1:
                rightNeigh += 1
                conect[i][0] = rightNeigh   
                
            # numCon = 0 
            # for j in range(1, 5):   # Contando o número de conexões
            #     if conect[i][j] != 0:
            #         numCon+=1
            # conect[i][0] = numCon
          
        indicesRemover = []
        cont = 1
        for i in range(len(self.boundGrid)):
            for patch in patches:
                if not patch.isPointInside(self.boundGrid[i]):
                    for j in range(len(conect)):
                        for k in range(0, 4):
                            if (i+1) == conect[j, k]:
                                conect[j,k] = 0
                                # conect[j, 0] -= 1
                    indicesRemover.append(i)
                else:
                    for j in range(len(conect)):
                        for k in range(0, 4):
                            if (i + 1) == conect[j, k]:
                                conect[j, k] = cont
                    cont += 1
                    
        conect = np.delete(conect, indicesRemover, axis=0)
        # print(conect)
        self.pointsDict["conect"] = conect.tolist()
        # print(indicesRemover)
                

        # for i in range(len(conect)):
        #     print(conect[i])

        # self.filename = "points_" + datetime.now().strftime("%H%M")+".json"
        self.filename = "../input.json"
        with open(self.filename, 'w') as jsonfile:
            json.dump(self.pointsDict, jsonfile)


        self.update()
        self.paintGL()

    def clearAll(self):
        self.hemodel.clearAll()
        self.m_model.clearAll()
        self.boundGrid = []
        self.gridPoints = []
        self.boundaryConditions = []
        self.update()
        self.paintGL()

    def printPoints(self):
        verts = self.heview.getPoints()
        for p in verts:
            print(p.getX(), p.getY())
