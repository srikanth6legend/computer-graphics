from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10 

mode = 0  # 0: Flood Fill, 1: Scan-Line Fill

def draw_watermarks():
    glColor3f(0.85, 0.85, 0.87)
    for y in [-0.5, 1.5, 10.5, 12.0]:
        for x in [0.5, 9.0]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def draw_axes():
    glColor3f(0.4, 0.4, 0.4); glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(-1, 0); glVertex2f(17, 0)
    glVertex2f(0, -1); glVertex2f(0, 13)
    glEnd()

def scanline_fill(vertices):
    ys = [v[1] for v in vertices]
    pts = []
    for y in range(min(ys), max(ys) + 1):
        xs = []
        for i in range(len(vertices)):
            x1, y1 = vertices[i]; x2, y2 = vertices[(i + 1) % len(vertices)]
            if y1 != y2 and min(y1, y2) <= y < max(y1, y2):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(round(xs[i])), int(round(xs[i+1])) + 1):
                pts.append((x, y))
    return pts

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_watermarks()
    draw_axes()

    if mode == 0:
        # Output 1: Flood Fill
        glColor3f(0.85, 0.45, 0.0)
        for x in range(3, 12):
            for y in (2, 7): glRectf(x - 0.4, y - 0.4, x + 0.4, y + 0.4)
        for y in range(2, 8):
            for x in (3, 11): glRectf(x - 0.4, y - 0.4, x + 0.4, y + 0.4)
        glColor3f(0.1, 0.6, 0.2)
        for x in range(4, 11):
            for y in range(3, 7): glRectf(x - 0.35, y - 0.35, x + 0.35, y + 0.35)
    else:
        # Output 2: Scan-Line Fill
        poly = [(3, 2), (10, 2), (12, 6), (7, 9), (2, 6)]
        glColor3f(0.1, 0.6, 0.2)
        for px, py in scanline_fill(poly):
            glRectf(px - 0.35, py - 0.35, px + 0.35, py + 0.35)
        glColor3f(0.85, 0.45, 0.0); glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for vx, vy in poly: glVertex2f(vx, vy)
        glEnd()

    glFlush()

def keyboard(key, x, y):
    global mode
    if key == b' ':
        mode = 1 - mode
        glutSetWindowTitle(b"Polygon Fill: Scan-Line" if mode else b"Polygon Fill: Flood Fill")
        glutPostRedisplay()

glutInit()
glutInitWindowSize(560, 400)
glutCreateWindow(b"Polygon Fill: Flood Fill (Press SPACE to toggle)")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(-1, 16, -1, 13)
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMainLoop()