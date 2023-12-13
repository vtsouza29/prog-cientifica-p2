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
        self.m_buttonPressed = False
        self.m_pt0 = QtCore.QPoint(0,0)
        self.m_pt1 = QtCore.QPoint(0,0)

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
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(pt0_U.x(), pt0_U.y())
        glVertex2f(pt1_U.x(), pt1_U.y())
        glEnd()

        
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
    
            verts = self.heview.getPoints()
            glColor3f(1.0, 0, 0)
            glPointSize(4)
            glBegin(GL_POINTS)
            for vert in verts:
                glVertex2f(vert.getX(), vert.getY())
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
        self.m_buttonPressed = True
        self.m_pt0 = event.pos()


    def mouseMoveEvent(self, event):
        if self.m_buttonPressed:
            self.m_pt1 = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
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
        self.update()
        self.paintGL()


    def rectangle(self, width, height):
        tol = 0.1
        # print(height, width)
        
        self.hecontroller.insertSegment([0, 0, width, 0], tol)
        self.hecontroller.insertSegment([0, 0, 0, height], tol)
        self.hecontroller.insertSegment([0, height, width, height], tol)
        self.hecontroller.insertSegment([width, height, width, 0], tol)

    def pointCloud(self, hpoints, vpoints):
        xmin, xmax, ymin, ymax = self.heview.getBoundBox()
        radius = abs(ymax - ymin)/(2*vpoints)                 
           
        xmin = xmin + radius
        xmax = xmax - radius

        ymin = ymin + radius
        ymax = ymax - radius

        dx = (abs(xmax) - abs(xmin))/(hpoints-1)
        dy = (abs(ymax) - abs(ymin))/(vpoints-1)
        tol = 0.1
        
        nPts = 0
        

        patches = self.heview.getPatches()
        pointsDict = {"coords":[], "radius":radius, "force":[], "restr":[], "conect":[],"mass":7850.0, "nE":0, "constMola":210000000000.0, "numPassos":3000, "h":1e-05}
        print(dx, dy)
        for i in np.linspace(xmin, xmax, hpoints, endpoint = True):
            for j in np.linspace(ymin, ymax, vpoints, endpoint=True):
                # print("j:", j)
                for patch in patches:
                    if patch.isPointInside(Point(i,j)):
                        self.hecontroller.insertPoint([i, j], tol)
                        coords = (i,j)
                        pointsDict['coords'].append(coords)
           
                        nPts += 1

        f = -1000
        force = np.zeros((nPts, 2))
        for i in range(hpoints*vpoints - (vpoints), hpoints*vpoints): #Preenchendo matriz de força com forças aplicadas na extremiadade direita
            force[i][0] = f
            force[i][1] = 0.0
            
        restr = np.zeros((nPts, 2))
        for i in range(0, vpoints): # Preenchendo matriz de restrição com partículas da extremidade esquerda presas
           restr[i][0] = 1
           restr[i][1] = 1 

        
        conect = np.zeros((nPts, 5)) # Matriz para trabalhar no python
        conectExport = []               # Matriz que vai pro JSON
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
                conect[i][4] = rightNeigh   
                
            numCon = 0 
            for j in range(1, 5):   # Contando o número de conexões
                if conect[i][j] != 0:
                    numCon+=1
            conect[i][0] = numCon
            b = conect[i][:1]
            a = conect[i][1:]
            a.sort()
            a = a[::-1]
           
            conect_i = [*b, *a]
            conectExport.append(conect_i)
           
        
        pointsDict["nE"] = nPts
        pointsDict["force"] = force.tolist()
        pointsDict["restr"] = restr.tolist()
        pointsDict["conect"] = conectExport
        filename = "points_" + datetime.now().strftime("%H%M%S")+".json"
        with open(filename, 'w') as jsonfile:
            json.dump(pointsDict, jsonfile)

        self.update()
        self.paintGL()

    def clearAll(self):
        self.hemodel.clearAll()
        self.m_model.clearAll()
        self.update()
        self.paintGL()

    def printPoints(self):
        verts = self.heview.getPoints()
        for p in verts:
            print(p.getX(), p.getY())


