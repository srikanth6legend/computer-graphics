from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10
def draw_watermarks():
    glColor3f(0.85, 0.85, 0.87)
    for y in [1.0, 3.5, 13.5, 16.0]:
        for x in [1.0, 12.0]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def display():
    glClear(GL_COLOR_BUFFER_BIT) # Framebuffer clear operation
    draw_watermarks()

    # Framebuffer Pixel Grid Simulation
    glColor3f(0.85, 0.85, 0.85)
    glLineWidth(1.0)
    for x in range(1, 24):
        glBegin(GL_LINES); glVertex2f(x, 1); glVertex2f(x, 17); glEnd()
    for y in range(1, 18):
        glBegin(GL_LINES); glVertex2f(1, y); glVertex2f(23, y); glEnd()

    # Cartesian Axes aligned through Framebuffer
    glColor3f(0.4, 0.4, 0.4)
    glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(1, 1); glVertex2f(23, 1)
    glVertex2f(1, 1); glVertex2f(1, 17)
    glEnd()

    # Primitive 1: Point
    glColor3f(0.85, 0.2, 0.2)
    glPointSize(10.0)
    glBegin(GL_POINTS)
    glVertex2f(5, 13)
    glEnd()

    # Primitive 2: Horizontal Line
    glColor3f(0.1, 0.6, 0.2)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex2f(3, 9); glVertex2f(19, 9)
    glEnd()

    # Primitive 3: Vertical Line
    glColor3f(0.0, 0.4, 0.8)
    glBegin(GL_LINES)
    glVertex2f(13, 3); glVertex2f(13, 14)
    glEnd()

    glFlush()

glutInit()
glutInitWindowSize(600, 420)
glutCreateWindow(b"Graphics Primitives and Framebuffer Operations")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(0, 24, 0, 18)
glutDisplayFunc(display)
glutMainLoop()
