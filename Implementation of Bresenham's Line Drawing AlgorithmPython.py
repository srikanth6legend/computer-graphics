from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10

def draw_watermarks():
    glColor3f(0.88, 0.88, 0.90)
    for y in [-1.5, 1.5, 7.0, 12.5]:
        for x in [-1.5, 9.0]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def bresenham(x1, y1, x2, y2):
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx = 1 if x1 < x2 else -1; sy = 1 if y1 < y2 else -1
    err = dx - dy
    pts = []
    while True:
        pts.append((x1, y1))
        if x1 == x2 and y1 == y2: break
        e2 = 2 * err
        if e2 > -dy: err -= dy; x1 += sx
        if e2 < dx:  err += dx; y1 += sy
    return pts

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_watermarks()
    
    # Axes
    glColor3f(0.4, 0.4, 0.4); glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(-2, 0); glVertex2f(20, 0)
    glVertex2f(0, -2); glVertex2f(0, 14)
    glEnd()

    x1, y1, x2, y2 = 2, 3, 16, 11 # Coordinates
    
    # Continuous reference line
    glColor3f(0.7, 0.7, 0.7)
    glLineStipple(1, 0x00FF); glEnable(GL_LINE_STIPPLE)
    glBegin(GL_LINES); glVertex2f(x1, y1); glVertex2f(x2, y2); glEnd()
    glDisable(GL_LINE_STIPPLE)

    # Integer Bresenham Pixels (Red/Amber)
    glColor3f(0.85, 0.35, 0.0)
    for px, py in bresenham(x1, y1, x2, y2):
        glRectf(px - 0.35, py - 0.35, px + 0.35, py + 0.35)
    glFlush()

glutInit()
glutInitWindowSize(620, 360)
glutCreateWindow(b"Bresenham Line Drawing Algorithm")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(-2, 19, -2, 14)
glutDisplayFunc(display)
glutMainLoop()
