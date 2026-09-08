from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10

angle, pos_x = 0.0, -6.0

def draw_watermarks():
    glColor3f(0.88, 0.88, 0.90)
    for y in [-5.0, -3.0, 3.0, 5.0]:
        for x in [-9.0, 2.0]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def display():
    global angle, pos_x
    glClear(GL_COLOR_BUFFER_BIT)
    draw_watermarks()
    
    # Axes
    glColor3f(0.4, 0.4, 0.4); glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(-10, 0); glVertex2f(10, 0)
    glVertex2f(0, -6); glVertex2f(0, 6)
    glEnd()

    # Animated Object (Translation + Rotation)
    glPushMatrix()
    glTranslatef(pos_x, 0.0, 0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)
    glColor3f(0.1, 0.6, 0.2)
    glRectf(-1.2, -1.2, 1.2, 1.2)
    glColor3f(0.85, 0.45, 0.0); glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    for x, y in [(-1.2, -1.2), (1.2, -1.2), (1.2, 1.2), (-1.2, 1.2)]: glVertex2f(x, y)
    glEnd()
    glPopMatrix()
    
    glutSwapBuffers()

def update(val):
    global angle, pos_x
    angle += 2.0
    pos_x += 0.05
    if pos_x > 6.0: pos_x = -6.0
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(560, 360)
glutCreateWindow(b"Animated Object Transformations")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(-10, 10, -6, 6)
glutDisplayFunc(display)
glutTimerFunc(0, update, 0)
glutMainLoop()