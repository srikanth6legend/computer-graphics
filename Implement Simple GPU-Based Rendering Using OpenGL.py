from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10
def draw_watermarks():
    glColor3f(0.85, 0.85, 0.87)
    for y in [-4.0, -2.0, 3.5, 4.5]:
        for x in [-4.5, 1.0]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_watermarks()

    # 2D Reference Axes
    glColor3f(0.4, 0.4, 0.4)
    glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(-5, 0); glVertex2f(5, 0)
    glVertex2f(0, -5); glVertex2f(0, 5)
    glEnd()

    # GPU-Based Smooth Color Interpolation (Gouraud Shading across Vertices)
    glBegin(GL_TRIANGLES)
    glColor3f(0.1, 0.7, 0.2); glVertex2f(-3.5, 2.5)  # Vertex 1: Green
    glColor3f(0.1, 0.2, 0.9); glVertex2f(3.5, 2.5)   # Vertex 2: Blue
    glColor3f(0.9, 0.1, 0.1); glVertex2f(0.0, -3.5)  # Vertex 3: Red
    glEnd()

    # Outlining Rendered Triangle Geometry & Displaying Vertex Nodes
    glColor3f(0.2, 0.2, 0.2)
    glLineWidth(1.5)
    glBegin(GL_LINE_LOOP)
    glVertex2f(-3.5, 2.5); glVertex2f(3.5, 2.5); glVertex2f(0.0, -3.5)
    glEnd()

    glPointSize(7.0)
    glBegin(GL_POINTS)
    glColor3f(0.1, 0.7, 0.2); glVertex2f(-3.5, 2.5)
    glColor3f(0.1, 0.2, 0.9); glVertex2f(3.5, 2.5)
    glColor3f(0.9, 0.1, 0.1); glVertex2f(0.0, -3.5)
    glEnd()

    glFlush()

glutInit()
glutInitWindowSize(560, 420)
glutCreateWindow(b"GPU-Based Rendering")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(-5, 5, -5, 5)
glutDisplayFunc(display)
glutMainLoop()
