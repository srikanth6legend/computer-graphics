from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10 
mode = 0  # 0: Cohen-Sutherland, 1: Liang-Barsky, 2: Sutherland-Hodgman
L, R, B, T = 2, 10, 2, 8  # Clipping window

def draw_watermarks():
    glColor3f(0.88, 0.88, 0.90)
    for y in [-2.5, 0.0, 9.5, 11.0]:
        for x in [-3.5, 7.0]:
            glRasterPos2f(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266":
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))

def draw_axes():
    glColor3f(0.4, 0.4, 0.4); glLineWidth(1.2)
    glBegin(GL_LINES)
    glVertex2f(-4, 0); glVertex2f(16, 0)
    glVertex2f(0, -3); glVertex2f(0, 12)
    glEnd()

def draw_clip_box(color):
    glColor3f(*color); glLineWidth(1.5)
    glBegin(GL_LINE_LOOP)
    for x, y in [(L, B), (R, B), (R, T), (L, T)]: glVertex2f(x, y)
    glEnd()

def cohen_sutherland(x1, y1, x2, y2):
    def code(x, y):
        return (1 if x < L else 2 if x > R else 0) | (4 if y < B else 8 if y > T else 0)
    c1, c2 = code(x1, y1), code(x2, y2)
    while True:
        if not (c1 | c2): return True, x1, y1, x2, y2
        if c1 & c2: return False, 0, 0, 0, 0
        c = c1 or c2
        if c & 8:    x, y = x1 + (x2 - x1) * (T - y1) / (y2 - y1), T
        elif c & 4:  x, y = x1 + (x2 - x1) * (B - y1) / (y2 - y1), B
        elif c & 2:  y, x = y1 + (y2 - y1) * (R - x1) / (x2 - x1), R
        else:        y, x = y1 + (y2 - y1) * (L - x1) / (x2 - x1), L
        if c == c1: x1, y1, c1 = x, y, code(x, y)
        else:       x2, y2, c2 = x, y, code(x, y)

def liang_barsky(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    p = [-dx, dx, -dy, dy]; q = [x1 - L, R - x1, y1 - B, T - y1]
    u1, u2 = 0.0, 1.0
    for i in range(4):
        if p[i] == 0 and q[i] < 0: return False, 0, 0, 0, 0
        if p[i] < 0: u1 = max(u1, q[i] / p[i])
        elif p[i] > 0: u2 = min(u2, q[i] / p[i])
    if u1 > u2: return False, 0, 0, 0, 0
    return True, x1 + u1 * dx, y1 + u1 * dy, x1 + u2 * dx, y1 + u2 * dy

def sutherland_hodgman(poly):
    def clip_edge(pts, edge):
        out = []
        if not pts: return out
        p1 = pts[-1]
        for p2 in pts:
            in1 = (p1[0] >= L if edge == 'L' else p1[0] <= R if edge == 'R' else p1[1] >= B if edge == 'B' else p1[1] <= T)
            in2 = (p2[0] >= L if edge == 'L' else p2[0] <= R if edge == 'R' else p2[1] >= B if edge == 'B' else p2[1] <= T)
            if in1 != in2:
                if edge in ['L', 'R']:
                    x = L if edge == 'L' else R
                    y = p1[1] + (p2[1] - p1[1]) * (x - p1[0]) / (p2[0] - p1[0])
                else:
                    y = B if edge == 'B' else T
                    x = p1[0] + (p2[0] - p1[0]) * (y - p1[1]) / (p2[1] - p1[1])
                out.append((x, y))
            if in2: out.append(p2)
            p1 = p2
        return out
    for e in ['L', 'R', 'B', 'T']: poly = clip_edge(poly, e)
    return poly

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_watermarks()
    draw_axes()

    if mode in [0, 1]:
        draw_clip_box((0.85, 0.45, 0.0))
        orig = (-2, 1, 13, 10)
        glColor3f(0.7, 0.7, 0.7); glLineStipple(1, 0x00FF); glEnable(GL_LINE_STIPPLE)
        glBegin(GL_LINES); glVertex2f(orig[0], orig[1]); glVertex2f(orig[2], orig[3]); glEnd()
        glDisable(GL_LINE_STIPPLE)

        # Output 1: Cohen-Sutherland (Green) | Output 2: Liang-Barsky (Magenta)
        ok, x1, y1, x2, y2 = cohen_sutherland(*orig) if mode == 0 else liang_barsky(*orig)
        if ok:
            glColor3f(0.1, 0.6, 0.2 if mode == 0 else 0.85); glLineWidth(3.0)
            glBegin(GL_LINES); glVertex2f(x1, y1); glVertex2f(x2, y2); glEnd()
    else:
        # Output 3: Sutherland-Hodgman Polygon Clipping
        draw_clip_box((0.0, 0.5, 0.7))
        orig_poly = [(0, 4), (5, 10), (12, 7), (8, 0), (3, 1)]
        glColor3f(0.7, 0.7, 0.7); glLineStipple(1, 0x00FF); glEnable(GL_LINE_STIPPLE)
        glBegin(GL_LINE_LOOP)
        for vx, vy in orig_poly: glVertex2f(vx, vy)
        glEnd(); glDisable(GL_LINE_STIPPLE)

        clipped_poly = sutherland_hodgman(orig_poly)
        glColor3f(0.1, 0.6, 0.2); glLineWidth(2.5)
        glBegin(GL_LINE_LOOP)
        for vx, vy in clipped_poly: glVertex2f(vx, vy)
        glEnd()

    glFlush()

def keyboard(key, x, y):
    global mode
    if key == b' ':
        mode = (mode + 1) % 3
        titles = [b"Clipping: Cohen-Sutherland", b"Clipping: Liang-Barsky", b"Clipping: Sutherland-Hodgman"]
        glutSetWindowTitle(titles[mode])
        glutPostRedisplay()

glutInit()
glutInitWindowSize(560, 400)
glutCreateWindow(b"Clipping: Cohen-Sutherland (Press SPACE to toggle)")
glClearColor(1.0, 1.0, 1.0, 1.0)
gluOrtho2D(-4, 15, -3, 12)
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutMainLoop()