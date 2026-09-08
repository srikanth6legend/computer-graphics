from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10

def draw_watermarks():
    glColor3f(0.85, 0.85, 0.87)
    for y in [-8.5, -4.0, 5.5, 9.5]:
        for x in [-12.0, 4.0]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def draw_axes():
    glColor3f(0.4, 0.4, 0.4)
    glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(-14, 0); glVertex2f(14, 0)
    glVertex2f(0, -10); glVertex2f(0, 11)
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

    base = [(1, 1), (4, 1), (4, 4), (1, 4)] # Base square in Quadrant I

    # 1. Original Shape (Dim Gray)
    draw_poly(base, 0.45, 0.50, 0.55)

    # 2. Reflection across X-axis: (x, -y)
    draw_poly([(x, -y) for x, y in base], 0.90, 0.55, 0.0)

    # 3. Reflection across Y-axis: (-x, y)
    draw_poly([(-x, y) for x, y in base], 0.1, 0.65, 0.3)

    # 4. Reflection across Origin: (-x, -y)
    draw_poly([(-x, -y) for x, y in base], 0.85, 0.2, 0.5)

    # 5. Shearing along X-axis: (x + shx * y, y), shx = 1.5
    draw_poly([(x + 1.5 * y, y) for x, y in base], 0.0, 0.55, 0.8)

    glFlush()

glutInit()
glutInitWindowSize(580, 420)
glutCreateWindow(b"Reflection and Shearing Transformations")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(-14, 14, -10, 11)
glutDisplayFunc(display)
glutMainLoop()
