from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10
import math

def draw_watermarks():
    glColor3f(0.85, 0.85, 0.87)
    for y in [-8, -4, 4, 8, 12]:
        for x in [-9, 4]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def draw_axes():
    glColor3f(0.4, 0.4, 0.4)
    glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(-10, 0); glVertex2f(15, 0)
    glVertex2f(0, -10); glVertex2f(0, 15)
    glEnd()

def transform(pts, deg, sx, sy, tx, ty, order="RST"):
    res, rad = [], math.radians(deg)
    for x, y in pts:
        if order == "RST": # Rotate -> Scale -> Translate
            rx, ry = x*math.cos(rad) - y*math.sin(rad), x*math.sin(rad) + y*math.cos(rad)
            res.append((rx * sx + tx, ry * sy + ty))
        else:              # Translate -> Scale -> Rotate
            tx_, ty_ = (x + tx) * sx, (y + ty) * sy
            res.append((tx_*math.cos(rad) - ty_*math.sin(rad), tx_*math.sin(rad) + ty_*math.cos(rad)))
    return res

def draw_poly(pts, r, g, b):
    glColor3f(r, g, b); glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    for x, y in pts: glVertex2f(x, y)
    glEnd()

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_watermarks()
    draw_axes()
    base = [(1, 1), (4, 1), (4, 4), (1, 4)] # Base square
    draw_poly(base, 0.4, 0.4, 0.4)
    draw_poly(transform(base, 30, 2, 2, 3, 2, "RST"), 0.1, 0.6, 0.2) # Rotate->Scale->Translate
    draw_poly(transform(base, 30, 2, 2, 3, 2, "TSR"), 0.8, 0.1, 0.4) # Translate->Scale->Rotate
    glFlush()

glutInit()
glutInitWindowSize(560, 420)
glutCreateWindow(b"Composite and Affine Transformations")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(-10, 15, -10, 15)
glutDisplayFunc(display)
glutMainLoop()