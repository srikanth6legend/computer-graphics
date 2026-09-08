from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10
def draw_watermarks():
    glColor3f(0.85, 0.85, 0.87)
    for y in [-6.0, -3.0, 7.0, 9.5]:
        for x in [-8.0, 3.5]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def draw_axes():
    glColor3f(0.4, 0.4, 0.4)
    glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(-9, 0); glVertex2f(12, 0)
    glVertex2f(0, -8); glVertex2f(0, 11)
    glEnd()

def draw_poly(pts, r, g, b):
    glColor3f(r, g, b)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    for x, y in pts: glVertex2f(x, y)
    glEnd()

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_watermarks()
    draw_axes()

    base = [(1, 1), (4, 1), (4, 4), (1, 4)] # Original square
    
    # 1. Original Shape (Dim Gray)
    draw_poly(base, 0.45, 0.50, 0.55)

    # 2. Translation: tx = 2, ty = 3 (Amber)
    trans = [(x + 2, y + 3) for x, y in base]
    draw_poly(trans, 0.90, 0.55, 0.0)

    # 3. Scaling: sx = 2, sy = 2.5 (Cyan)
    scaled = [(x * 2.0, y * 2.5) for x, y in base]
    draw_poly(scaled, 0.0, 0.6, 0.8)

    # 4. Rotation: 45 degrees about origin (Magenta)
    th = math.radians(45)
    rot = [(x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th)) for x, y in base]
    draw_poly(rot, 0.85, 0.2, 0.5)

    glFlush()

glutInit()
glutInitWindowSize(560, 420)
glutCreateWindow(b"2D Geometric Transformations")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(-9, 12, -8, 11)
glutDisplayFunc(display)
glutMainLoop()
