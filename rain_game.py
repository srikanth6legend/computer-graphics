import sys
import random
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window Setup
WIDTH, HEIGHT = 900, 650

# Game State
score = 0
ground_level = 90

# Cloud Controller Properties
cloud_x = WIDTH // 2
cloud_y = HEIGHT - 85
cloud_speed = 18
moving_left = False
moving_right = False
is_raining = True

# Particles & Game Entities
raindrops = []  # List of dicts: {'x': float, 'y': float, 'len': int, 'speed': float}
plants = []     # List of dicts: {'x': int, 'stage': int, 'growth': float}
MAX_PLANTS = 9

# -------------------------------------------------------------
# 1. DDA LINE DRAWING ALGORITHM (Stems, Trunks & Branches)
# -------------------------------------------------------------
def draw_line_dda(x1, y1, x2, y2, r=1.0, g=1.0, b=1.0):
    dx = x2 - x1
    dy = y2 - y1
    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        glColor3f(r, g, b)
        glBegin(GL_POINTS)
        glVertex2i(int(x1), int(y1))
        glEnd()
        return

    x_inc = dx / float(steps)
    y_inc = dy / float(steps)

    x, y = float(x1), float(y1)
    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    for _ in range(steps + 1):
        glVertex2i(int(round(x)), int(round(y)))
        x += x_inc
        y += y_inc
    glEnd()

# -------------------------------------------------------------
# 2. BRESENHAM'S LINE ALGORITHM (HUD Frames & Dividers)
# -------------------------------------------------------------
def draw_line_bresenham(x1, y1, x2, y2, r=1.0, g=1.0, b=1.0):
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    while True:
        glVertex2i(x1, y1)
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    glEnd()

# -------------------------------------------------------------
# 3. COHEN-SUTHERLAND LINE CLIPPING ALGORITHM (Rain & Sunbeams)
# -------------------------------------------------------------
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

def compute_outcode(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE
    if x < xmin: code |= LEFT
    elif x > xmax: code |= RIGHT
    if y < ymin: code |= BOTTOM
    elif y > ymax: code |= TOP
    return code

def clip_and_draw_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax, r=0.45, g=0.75, b=1.0):
    code1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)
    accept = False

    while True:
        if (code1 | code2) == 0:
            accept = True
            break
        elif (code1 & code2) != 0:
            break
        else:
            x, y = 0.0, 0.0
            outcode = code1 if code1 != 0 else code2

            if outcode & TOP:
                if y2 != y1:
                    x = x1 + (x2 - x1) * (ymax - y1) / float(y2 - y1)
                else:
                    x = x1
                y = ymax
            elif outcode & BOTTOM:
                if y2 != y1:
                    x = x1 + (x2 - x1) * (ymin - y1) / float(y2 - y1)
                else:
                    x = x1
                y = ymin
            elif outcode & RIGHT:
                if x2 != x1:
                    y = y1 + (y2 - y1) * (xmax - x1) / float(x2 - x1)
                else:
                    y = y1
                x = xmax
            elif outcode & LEFT:
                if x2 != x1:
                    y = y1 + (y2 - y1) * (xmin - x1) / float(x2 - x1)
                else:
                    y = y1
                x = xmin

            if outcode == code1:
                x1, y1 = x, y
                code1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x, y
                code2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)

    if accept:
        draw_line_dda(x1, y1, x2, y2, r, g, b)

# -------------------------------------------------------------
# 4. MIDPOINT CIRCLE ALGORITHM (Cloud, Seeds, Petals & Canopy)
# -------------------------------------------------------------
def draw_circle_midpoint(xc, yc, r, red=1.0, green=1.0, blue=1.0):
    xc, yc = int(xc), int(yc)
    r = int(r)
    glColor3f(red, green, blue)
    glBegin(GL_POINTS)
    for curr_r in range(r, 0, -1):
        x = 0
        y = curr_r
        d = 1 - curr_r
        while x <= y:
            for sx, sy in [(x, y), (y, x), (-x, y), (-y, x),
                           (-x, -y), (-y, -x), (x, -y), (y, -x)]:
                glVertex2i(xc + sx, yc + sy)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
    glVertex2i(xc, yc)
    glEnd()

# -------------------------------------------------------------
# 5. SCAN-LINE POLYGON FILLING ALGORITHM (Ground & HUD Panel)
# -------------------------------------------------------------
def draw_polygon_scanline(vertices, red=0.3, green=0.2, blue=0.1):
    n = len(vertices)
    ymin = int(min(v[1] for v in vertices))
    ymax = int(max(v[1] for v in vertices))

    glColor3f(red, green, blue)
    glBegin(GL_POINTS)
    for y in range(ymin, ymax + 1):
        intersections = []
        for i in range(n):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % n]
            if p1[1] == p2[1]:
                continue
            if min(p1[1], p2[1]) <= y <= max(p1[1], p2[1]):
                x_int = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / float(p2[1] - p1[1])
                intersections.append(x_int)

        intersections.sort()
        for i in range(0, len(intersections) - 1, 2):
            x_start = int(round(intersections[i]))
            x_end = int(round(intersections[i + 1]))
            for x in range(x_start, x_end + 1):
                glVertex2i(x, y)
    glEnd()

# -------------------------------------------------------------
# GAME ENTITY DRAWING
# -------------------------------------------------------------
def draw_cloud(cx, cy):
    draw_circle_midpoint(cx - 35, cy, 24, 0.85, 0.88, 0.95)
    draw_circle_midpoint(cx + 35, cy, 24, 0.85, 0.88, 0.95)
    draw_circle_midpoint(cx - 15, cy + 14, 28, 0.95, 0.97, 1.0)
    draw_circle_midpoint(cx + 15, cy + 14, 28, 0.95, 0.97, 1.0)
    draw_circle_midpoint(cx, cy, 26, 0.9, 0.92, 0.98)

def draw_plant(plant):
    x = plant['x']
    y = ground_level
    stage = plant['stage']
    growth = plant['growth']

    if stage == 0:
        # Seed
        draw_circle_midpoint(x, y + 4, 5, 0.55, 0.35, 0.15)
        draw_circle_midpoint(x, y + 4, 3, 0.75, 0.55, 0.25)

    elif stage == 1:
        # Sprout
        stem_h = int(12 + growth * 0.4)
        for offset in [-1, 0, 1]:
            draw_line_dda(x + offset, y, x + offset, y + stem_h, 0.2, 0.75, 0.2)
        draw_circle_midpoint(x - 4, y + stem_h - 2, 3, 0.3, 0.85, 0.3)
        draw_circle_midpoint(x + 4, y + stem_h - 2, 3, 0.3, 0.85, 0.3)

    elif stage == 2:
        # Flower
        stem_h = 36
        for offset in [-1, 0, 1]:
            draw_line_dda(x + offset, y, x + offset, y + stem_h, 0.15, 0.65, 0.2)
        draw_circle_midpoint(x - 7, y + stem_h, 5, 0.95, 0.3, 0.5)
        draw_circle_midpoint(x + 7, y + stem_h, 5, 0.95, 0.3, 0.5)
        draw_circle_midpoint(x, y + stem_h + 7, 5, 0.95, 0.3, 0.5)
        draw_circle_midpoint(x, y + stem_h - 7, 5, 0.95, 0.3, 0.5)
        draw_circle_midpoint(x, y + stem_h, 4, 1.0, 0.85, 0.1)

    elif stage == 3:
        # Sapling
        stem_h = 55
        for offset in [-2, -1, 0, 1, 2]:
            draw_line_dda(x + offset, y, x + offset, y + stem_h, 0.4, 0.25, 0.1)
        draw_circle_midpoint(x, y + stem_h + 8, 14, 0.15, 0.65, 0.25)
        draw_circle_midpoint(x - 9, y + stem_h + 3, 10, 0.1, 0.55, 0.2)
        draw_circle_midpoint(x + 9, y + stem_h + 3, 10, 0.1, 0.55, 0.2)

    elif stage >= 4:
        # Full Mature Tree
        trunk_h = 80
        for offset in range(-4, 5):
            draw_line_dda(x + offset, y, x + offset, y + trunk_h, 0.35, 0.2, 0.08)
        draw_line_dda(x, y + 50, x - 22, y + 70, 0.35, 0.2, 0.08)
        draw_line_dda(x, y + 55, x + 22, y + 75, 0.35, 0.2, 0.08)
        draw_circle_midpoint(x, y + trunk_h + 20, 24, 0.1, 0.65, 0.2)
        draw_circle_midpoint(x - 20, y + trunk_h + 8, 18, 0.15, 0.55, 0.18)
        draw_circle_midpoint(x + 20, y + trunk_h + 8, 18, 0.15, 0.55, 0.18)
        draw_circle_midpoint(x, y + trunk_h + 30, 16, 0.2, 0.75, 0.25)
        draw_circle_midpoint(x - 10, y + trunk_h + 14, 3, 0.95, 0.15, 0.15)
        draw_circle_midpoint(x + 12, y + trunk_h + 22, 3, 0.95, 0.15, 0.15)
        draw_circle_midpoint(x + 5, y + trunk_h + 8, 3, 0.95, 0.15, 0.15)

def spawn_seed():
    if len(plants) < MAX_PLANTS:
        sx = random.randint(40, WIDTH - 40)
        for p in plants:
            if abs(sx - p['x']) < 65:
                return
        plants.append({'x': sx, 'stage': 0, 'growth': 0.0})

def render_bitmap_string(x, y, text):
    glRasterPos2i(int(x), int(y))
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

# -------------------------------------------------------------
# DISPLAY CALLBACK
# -------------------------------------------------------------
def display():
    glClear(GL_COLOR_BUFFER_BIT)

    # 1. Clipped Sunbeam Rays (Cohen-Sutherland)
    clip_and_draw_line(40, HEIGHT - 30, 180, 50, 10, ground_level, WIDTH - 10, HEIGHT - 10, 0.25, 0.32, 0.45)
    clip_and_draw_line(80, HEIGHT - 30, 260, 50, 10, ground_level, WIDTH - 10, HEIGHT - 10, 0.25, 0.32, 0.45)

    # 2. Ground Soil & Grass (Scan-Line Polygon Filling)
    soil_poly = [(0, 0), (WIDTH, 0), (WIDTH, ground_level), (0, ground_level)]
    draw_polygon_scanline(soil_poly, 0.25, 0.16, 0.08)

    grass_poly = [(0, ground_level - 6), (WIDTH, ground_level - 6), (WIDTH, ground_level), (0, ground_level)]
    draw_polygon_scanline(grass_poly, 0.15, 0.55, 0.15)

    # 3. Outer Borders & HUD Box (Bresenham's)
    draw_line_bresenham(5, 5, WIDTH - 5, 5, 0.2, 0.4, 0.5)
    draw_line_bresenham(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5, 0.2, 0.4, 0.5)
    draw_line_bresenham(WIDTH - 5, HEIGHT - 5, 5, HEIGHT - 5, 0.2, 0.4, 0.5)
    draw_line_bresenham(5, HEIGHT - 5, 5, 5, 0.2, 0.4, 0.5)

    hud_poly = [(WIDTH - 240, HEIGHT - 70), (WIDTH - 10, HEIGHT - 70), (WIDTH - 10, HEIGHT - 10), (WIDTH - 240, HEIGHT - 10)]
    draw_polygon_scanline(hud_poly, 0.08, 0.14, 0.22)
    draw_line_bresenham(WIDTH - 240, HEIGHT - 70, WIDTH - 10, HEIGHT - 70, 0.3, 0.6, 0.8)
    draw_line_bresenham(WIDTH - 240, HEIGHT - 10, WIDTH - 240, HEIGHT - 70, 0.3, 0.6, 0.8)

    # 4. Raindrops Clipped to Atmosphere (Cohen-Sutherland Line Clipping)
    for drop in raindrops:
        clip_and_draw_line(drop['x'], drop['y'], drop['x'], drop['y'] - drop['len'], 
                           10, ground_level, WIDTH - 10, cloud_y - 10, 
                           0.45, 0.75, 1.0)

    # 5. Seeds & Growing Plants
    for plant in plants:
        draw_plant(plant)

    # 6. Controllable Cloud
    draw_cloud(cloud_x, cloud_y)

    # 7. UI Text & Score
    total_trees = sum(1 for p in plants if p['stage'] >= 4)
    glColor3f(1.0, 1.0, 1.0)
    render_bitmap_string(WIDTH - 225, HEIGHT - 35, f"GROWTH SCORE: {score}")
    render_bitmap_string(WIDTH - 225, HEIGHT - 58, f"FULL TREES: {total_trees}")

    glColor3f(0.8, 0.85, 0.9)
    render_bitmap_string(20, HEIGHT - 30, "Move Cloud: [A/D] or [<- / ->]")
    render_bitmap_string(20, HEIGHT - 52, "Rain Toggle: [SPACE] | New Seed: [S]")

    glutSwapBuffers()

# -------------------------------------------------------------
# GAME LOGIC & ANIMATION LOOP
# -------------------------------------------------------------
def update(value):
    global cloud_x, score, is_raining

    if moving_left:
        cloud_x = max(70, cloud_x - cloud_speed)
    if moving_right:
        cloud_x = min(WIDTH - 70, cloud_x + cloud_speed)

    if is_raining:
        for _ in range(4):
            rx = cloud_x + random.randint(-45, 45)
            ry = cloud_y - 15 + random.randint(-5, 5)
            raindrops.append({'x': rx, 'y': ry, 'len': random.randint(8, 14), 'speed': random.uniform(6.5, 9.5)})

    for drop in raindrops[:]:
        drop['y'] -= drop['speed']

        if drop['y'] <= ground_level:
            for plant in plants:
                hit_radius = 18 if plant['stage'] < 2 else (30 if plant['stage'] < 4 else 45)
                if abs(drop['x'] - plant['x']) <= hit_radius:
                    plant['growth'] += 0.45
                    score += 1

                    if plant['stage'] == 0 and plant['growth'] >= 15:
                        plant['stage'] = 1
                    elif plant['stage'] == 1 and plant['growth'] >= 40:
                        plant['stage'] = 2
                    elif plant['stage'] == 2 and plant['growth'] >= 75:
                        plant['stage'] = 3
                    elif plant['stage'] == 3 and plant['growth'] >= 120:
                        plant['stage'] = 4
                    break

            if drop in raindrops:
                raindrops.remove(drop)

    if random.random() < 0.015:
        spawn_seed()

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

# -------------------------------------------------------------
# CONTROLS
# -------------------------------------------------------------
def keyboard_down(key, x, y):
    global moving_left, moving_right, is_raining
    if key in (b'a', b'A'):
        moving_left = True
    elif key in (b'd', b'D'):
        moving_right = True
    elif key == b' ':
        is_raining = not is_raining
    elif key in (b's', b'S'):
        spawn_seed()

def keyboard_up(key, x, y):
    global moving_left, moving_right
    if key in (b'a', b'A'):
        moving_left = False
    elif key in (b'd', b'D'):
        moving_right = False

def special_down(key, x, y):
    global moving_left, moving_right
    if key == GLUT_KEY_LEFT:
        moving_left = True
    elif key == GLUT_KEY_RIGHT:
        moving_right = True

def special_up(key, x, y):
    global moving_left, moving_right
    if key == GLUT_KEY_LEFT:
        moving_left = False
    elif key == GLUT_KEY_RIGHT:
        moving_right = False

# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(100, 80)
    glutCreateWindow(b"Cloud Rain & Plant Growth - With Cohen-Sutherland Clipping")

    glClearColor(0.12, 0.18, 0.28, 1.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)

    for _ in range(4):
        spawn_seed()

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutTimerFunc(0, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()