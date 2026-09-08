from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10
def draw_watermarks():
    glColor3f(0.85, 0.85, 0.87)
    for y in [1.0, 4.0, 14.0, 17.0]:
        for x in [1.0, 14.0]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def draw_axes():
    glColor3f(0.4, 0.4, 0.4)
    glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(0, 0); glVertex2f(28, 0)
    glVertex2f(0, 0); glVertex2f(0, 19)
    glEnd()

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_watermarks()
    draw_axes()

    # 1. Raster Graphics Representation: Discrete Grid & Blocky Character 'A'
    glColor3f(0.8, 0.8, 0.8) # Grid lines
    glLineWidth(1.0)
    for x in range(2, 9):
        glBegin(GL_LINES); glVertex2f(x, 6); glVertex2f(x, 13); glEnd()
    for y in range(6, 14):
        glBegin(GL_LINES); glVertex2f(2, y); glVertex2f(8, y); glEnd()

    # Filled character pixels
    glColor3f(0.1, 0.1, 0.1)
    raster_pixels = [
        (4, 12), (5, 12), (3, 11), (6, 11),
        (2, 10), (7, 10), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9),
        (2, 8), (7, 8), (2, 7), (7, 7), (2, 6), (7, 6)
    ]
    print(raster_pixels)
    for px, py in raster_pixels:
        glRectf(px, py, px + 1, py + 1)

    # 2. Vector Graphics Representation: Exact Coordinate Geometry Endpoints
    x1, y1, x2, y2 = 14, 6, 25, 13
    glColor3f(0.1, 0.6, 0.2)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex2f(x1, y1); glVertex2f(x2, y2)
    glEnd()

    # Vector Start & End Nodes
    glColor3f(0.85, 0.35, 0.0)
    glPointSize(8.0)
    glBegin(GL_POINTS)
    glVertex2f(x1, y1); glVertex2f(x2, y2)
    glEnd()

    glFlush()

glutInit()
glutInitWindowSize(600, 400)
glutCreateWindow(b"Raster and Vector Graphics Representation")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(0, 28, 0, 19)
glutDisplayFunc(display)
glutMainLoop()
