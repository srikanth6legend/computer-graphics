from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10
def draw_watermarks_2d():
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, 560, 0, 420)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(0.85, 0.85, 0.87)
    for y in [30, 80, 340, 390]:
        for x in [20, 300]:
            glRasterPos2i(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW); glEnable(GL_DEPTH_TEST)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(4.5, 3.5, 5.5, 0, 0, 0, 0, 1, 0)
    
    # 3D Coordinate Axes (X, Y, Z)
    glLineWidth(1.5)
    glBegin(GL_LINES)
    glColor3f(0.8, 0.0, 0.0); glVertex3f(0, 0, 0); glVertex3f(3.5, 0, 0)
    glColor3f(0.0, 0.6, 0.0); glVertex3f(0, 0, 0); glVertex3f(0, 3.5, 0)
    glColor3f(0.0, 0.2, 0.8); glVertex3f(0, 0, 0); glVertex3f(0, 0, 3.5)
    glEnd()

    # Original Reference Cube
    glColor3f(0.65, 0.65, 0.65)
    glutWireCube(1.5)
    
    # Transformed Cube: Translation, Scaling, Rotation
    glPushMatrix()
    glTranslatef(1.0, 0.8, -0.5)
    glRotatef(40, 1.0, 1.0, 0.0)
    glScalef(1.4, 0.7, 1.0)
    glColor3f(0.1, 0.6, 0.2)
    glutWireCube(1.5)
    glPopMatrix()
    
    draw_watermarks_2d()
    glutSwapBuffers()

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(560, 420)
glutCreateWindow(b"3D Geometric Transformations")
glClearColor(1.0, 1.0, 1.0, 1.0)
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_PROJECTION)
gluPerspective(45.0, 560.0/420.0, 1.0, 20.0)
glMatrixMode(GL_MODELVIEW)
glutDisplayFunc(display)
glutMainLoop()
