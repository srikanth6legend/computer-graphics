from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10

def draw_watermarks():
    glColor3f(0.88, 0.88, 0.90)
    for y in [-0.5, 1.5, 15.5, 17.0]:
        for x in [0.0, 14.0]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def midpoint_circle(xc, yc, r):
    x, y, p = 0, r, 1 - r
    pts = []
    while x <= y:
        for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y), (y, x), (-y, x), (y, -x), (-y, -x)]:
            pts.append((xc + dx, yc + dy))
        x += 1
        p += 2 * x + 1 if p < 0 else (2 * (x - y) + 1)
        if p >= 0 and p - (2 * x + 1) >= 0: y -= 1
    return pts

def midpoint_ellipse(xc, yc, rx, ry):
    x, y = 0, ry
    d1 = (ry**2) - (rx**2 * ry) + (0.25 * rx**2)
    pts = []
    while (2 * ry**2 * x) <= (2 * rx**2 * y):
        for dx, dy in [(x, y), (-x, y), (x, -y), (-x, -y)]: pts.append((xc + dx, yc + dy))
        x += 1
        d1 += (2 * ry**2 * x) + ry**2 if d1 < 0 else (2 * ry**2 * x) - (2 * rx**2 * y) + ry**2
        if d1 >= 0: y -= 1
    return pts

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_watermarks()
    
    # Axes
    glColor3f(0.4, 0.4, 0.4); glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(-1, 0); glVertex2f(28, 0)
    glVertex2f(0, -1); glVertex2f(0, 18)
    glEnd()

    # Circle (Green) and Ellipse (Cyan)
    glColor3f(0.1, 0.6, 0.2)
    for px, py in midpoint_circle(7, 9, 6):
        glRectf(px - 0.35, py - 0.35, px + 0.35, py + 0.35)

    glColor3f(0.0, 0.5, 0.7)
    for px, py in midpoint_ellipse(18, 9, 7, 4):
        glRectf(px - 0.35, py - 0.35, px + 0.35, py + 0.35)
    glFlush()

glutInit()
glutInitWindowSize(600, 380)
glutCreateWindow(b"Midpoint Circle and Ellipse Algorithms")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(-1, 28, -1, 18)
glutDisplayFunc(display)
glutMainLoop()
