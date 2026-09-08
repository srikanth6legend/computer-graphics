from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10

def draw_watermarks():
    glColor3f(0.85, 0.85, 0.87)
    for y in [-0.6, 1.5, 3.5, 5.2]:
        for x in [-0.8, 4.0]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_watermarks()
    
    # Axes
    glColor3f(0.4, 0.4, 0.4); glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(-1, 0); glVertex2f(8, 0)
    glVertex2f(0, -1); glVertex2f(0, 6)
    glEnd()

    f = 5.0 # Focal length
    pts3d = [(2, 2, 4), (4, 2, 8), (6, 3, 12), (2, 4, 4)]
    proj = [(f * x / z, f * y / z) for x, y, z in pts3d] # Projection mapping

    # Center/Pin-hole point
    glColor3f(0.8, 0.4, 0.0); glPointSize(7.0)
    glBegin(GL_POINTS); glVertex2f(0, 0); glEnd()

    # Perspective projected shape
    glColor3f(0.1, 0.6, 0.2); glLineWidth(2.0)
    glBegin(GL_LINE_STRIP)
    for px, py in proj: glVertex2f(px, py)
    glEnd()
    glPointSize(5.0)
    glBegin(GL_POINTS)
    for px, py in proj: glVertex2f(px, py)
    glEnd()
    glFlush()

glutInit()
glutInitWindowSize(560, 420)
glutCreateWindow(b"Perspective Projection")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(-1, 8, -1, 6)
glutDisplayFunc(display)
glutMainLoop()
