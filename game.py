import sys
import random
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window Dimensions
WIDTH, HEIGHT = 800, 600

# Game State
score = 0
game_over = False

# Paddle Properties
paddle_x = WIDTH // 2
paddle_y = 50
paddle_w = 120
paddle_h = 16
paddle_speed = 15  # Reduced from 25 for slower movement
moving_left = False
moving_right = False

# Ball Properties
ball_x = WIDTH // 2
ball_y = 150
ball_radius = 8.0
ball_speed = 7.0
ball_vx = 3.5
ball_vy = 6.0
max_ball_radius = 22.0

# Spawned Targets
targets = []  # List of dicts: {'x': int, 'y': int, 'size': int}
MAX_TARGETS = 10

# -------------------------------------------------------------
# 1. BRESENHAM'S LINE DRAWING ALGORITHM (Borders & HUD Box)
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
# 2. MIDPOINT CIRCLE ALGORITHM (Filled Ball & Pixel Targets)
# -------------------------------------------------------------
def draw_circle_midpoint(xc, yc, r, red=1.0, green=0.2, blue=0.2):
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
# 3. SCAN-LINE POLYGON FILLING ALGORITHM (Paddle)
# -------------------------------------------------------------
def draw_polygon_scanline(vertices, red=0.2, green=0.8, blue=0.4):
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
# TARGET SPAWN LOGIC
# -------------------------------------------------------------
def spawn_target():
    if len(targets) < MAX_TARGETS:
        tx = random.randint(40, WIDTH - 40)
        ty = random.randint(260, HEIGHT - 90)
        # Avoid spawning directly inside an existing target
        for t in targets:
            if math.hypot(tx - t['x'], ty - t['y']) < 25:
                return
        targets.append({'x': tx, 'y': ty, 'size': random.randint(6, 9)})

def draw_simple_digit(x, y, digit, scale=1.0):
    """Draw simple digit using Bresenham lines"""
    digit_patterns = {
        '0': [(0,0), (2,0), (2,4), (0,4), (0,0)],
        '1': [(1,0), (1,4)],
        '2': [(0,0), (2,0), (2,2), (0,2), (0,4), (2,4)],
        '3': [(0,0), (2,0), (2,2), (0,2), (2,2), (2,4), (0,4)],
        '4': [(2,0), (0,2), (2,2), (2,4)],
        '5': [(2,0), (0,0), (0,2), (2,2), (2,4), (0,4)],
        '6': [(2,0), (0,0), (0,4), (2,4), (2,2), (0,2)],
        '7': [(0,0), (2,0), (2,4)],
        '8': [(0,0), (2,0), (2,4), (0,4), (0,0), (0,2), (2,2)],
        '9': [(2,4), (0,4), (0,0), (2,0), (2,2), (0,2)],
        ':': [(0,1), (0,1.2), (0,3), (0,3.2)],
    }
    pattern = digit_patterns.get(digit, [])
    glColor3f(1.0, 1.0, 1.0)
    for i in range(len(pattern)-1):
        x1, y1 = pattern[i]
        x2, y2 = pattern[i+1]
        draw_line_bresenham(x + x1*scale, y + y1*scale, x + x2*scale, y + y2*scale, 1, 1, 1)

def render_text_simple(x, y, text):
    """Render text using simple digit drawing"""
    x_offset = 0
    for char in text:
        if char.isdigit() or char == ':':
            draw_simple_digit(x + x_offset, y, char, scale=2.0)
            x_offset += 8
        elif char == ' ':
            x_offset += 6

# -------------------------------------------------------------
# DISPLAY CALLBACK
# -------------------------------------------------------------
def display():
    glClear(GL_COLOR_BUFFER_BIT)

    # 1. Outer Arena Borders (Bresenham)
    draw_line_bresenham(12, 12, WIDTH - 12, 12, 0.35, 0.4, 0.5)
    draw_line_bresenham(WIDTH - 12, 12, WIDTH - 12, HEIGHT - 12, 0.35, 0.4, 0.5)
    draw_line_bresenham(WIDTH - 12, HEIGHT - 12, 12, HEIGHT - 12, 0.35, 0.4, 0.5)
    draw_line_bresenham(12, HEIGHT - 12, 12, 12, 0.35, 0.4, 0.5)

    # 2. HUD Box
    draw_line_bresenham(WIDTH - 220, HEIGHT - 12, WIDTH - 220, HEIGHT - 65, 0.2, 0.7, 0.9)
    draw_line_bresenham(WIDTH - 220, HEIGHT - 65, WIDTH - 12, HEIGHT - 65, 0.2, 0.7, 0.9)

    # 3. Paddle (Scan-Line Polygon Fill)
    px1, px2 = paddle_x - paddle_w // 2, paddle_x + paddle_w // 2
    py1, py2 = paddle_y - paddle_h // 2, paddle_y + paddle_h // 2
    paddle_verts = [(px1, py1), (px2, py1), (px2, py2), (px1, py2)]
    draw_polygon_scanline(paddle_verts, 0.2, 0.85, 0.5)

    # 4. Target Pixels / Orbs (Midpoint Circle)
    for t in targets:
        draw_circle_midpoint(t['x'], t['y'], t['size'], 1.0, 0.8, 0.1)

    # 5. Animated Bouncing Ball (Midpoint Circle)
    draw_circle_midpoint(ball_x, ball_y, ball_radius, 0.95, 0.3, 0.25)

    # 6. Top-Right Score & HUD Info (using simple text rendering)
    glColor3f(1.0, 1.0, 1.0)
    # Draw score indicator lines
    draw_line_bresenham(WIDTH - 210, HEIGHT - 35, WIDTH - 180, HEIGHT - 35, 1.0, 1.0, 1.0)
    render_text_simple(WIDTH - 175, HEIGHT - 40, str(score).zfill(5))
    
    # Draw ball size indicator
    draw_line_bresenham(WIDTH - 210, HEIGHT - 55, WIDTH - 180, HEIGHT - 55, 1.0, 1.0, 1.0)
    render_text_simple(WIDTH - 175, HEIGHT - 60, str(int(ball_radius)).zfill(2))

    if game_over:
        glColor3f(1.0, 0.25, 0.25)
        draw_line_bresenham(WIDTH // 2 - 150, HEIGHT // 2, WIDTH // 2 + 150, HEIGHT // 2, 1.0, 0.25, 0.25)

    glutSwapBuffers()

# -------------------------------------------------------------
# GAME UPDATE & PHYSICS ENGINE
# -------------------------------------------------------------
def update(value):
    global ball_x, ball_y, ball_vx, ball_vy, ball_radius, score, game_over, paddle_x

    if not game_over:
        # Paddle Continuous Movement
        if moving_left:
            paddle_x = max(paddle_w // 2 + 15, paddle_x - paddle_speed)
        if moving_right:
            paddle_x = min(WIDTH - paddle_w // 2 - 15, paddle_x + paddle_speed)

        # Move Ball
        ball_x += ball_vx
        ball_y += ball_vy

        # Left / Right Wall Collisions
        if ball_x - ball_radius <= 14:
            ball_x = 14 + ball_radius
            ball_vx = abs(ball_vx)
        elif ball_x + ball_radius >= WIDTH - 14:
            ball_x = WIDTH - 14 - ball_radius
            ball_vx = -abs(ball_vx)

        # Top Wall Collision
        if ball_y + ball_radius >= HEIGHT - 14:
            ball_y = HEIGHT - 14 - ball_radius
            ball_vy = -abs(ball_vy)

        # Paddle Collision (AABB vs Circle Check)
        px_min = paddle_x - paddle_w // 2
        px_max = paddle_x + paddle_w // 2
        py_min = paddle_y - paddle_h // 2
        py_max = paddle_y + paddle_h // 2

        # Check if ball is touching paddle top surface while falling down
        if ball_vy < 0:
            if (px_min - 4 <= ball_x <= px_max + 4) and (py_min <= ball_y - ball_radius <= py_max + 6):
                # Reposition ball directly on top of paddle to avoid clipping
                ball_y = py_max + ball_radius + 1

                # Angle calculation based on hit position
                hit_offset = (ball_x - paddle_x) / (paddle_w / 2.0)
                hit_offset = max(-0.9, min(0.9, hit_offset))  # Clamp value

                max_angle = math.radians(60)
                bounce_angle = hit_offset * max_angle

                speed = math.hypot(ball_vx, ball_vy)
                speed = min(speed, 10.0)  # Cap max speed to prevent runaway
                ball_vx = speed * math.sin(bounce_angle)
                ball_vy = speed * math.cos(bounce_angle)
                # Ensure ball always bounces upward
                if ball_vy < 0:
                    ball_vy = abs(ball_vy)

        # Missed Ball (Bottom Edge)
        if ball_y - ball_radius < 5:
            game_over = True

        # Target Collisions
        for t in targets[:]:
            dist = math.hypot(ball_x - t['x'], ball_y - t['y'])
            if dist <= (ball_radius + t['size']):
                targets.remove(t)
                score += 10
                # Grow ball size slightly
                if ball_radius < max_ball_radius:
                    ball_radius += 1.2
                break

        # Spawn targets randomly
        if random.random() < 0.035:
            spawn_target()

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

# -------------------------------------------------------------
# SMOOTH KEYBOARD CONTROLS
# -------------------------------------------------------------
def keyboard_down(key, x, y):
    global moving_left, moving_right, game_over, score, ball_x, ball_y, ball_vx, ball_vy, ball_radius, paddle_x, targets
    if key in (b'a', b'A'):
        moving_left = True
    elif key in (b'd', b'D'):
        moving_right = True
    elif key in (b'r', b'R') and game_over:
        # Full Reset
        score = 0
        game_over = False
        ball_x, ball_y = WIDTH // 2, 150
        ball_vx, ball_vy = 3.5, 6.0
        ball_radius = 8.0
        paddle_x = WIDTH // 2
        targets.clear()
        for _ in range(6):
            spawn_target()
    elif key == b'\x1b':  # ESC key
        sys.exit(0)

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
# INITIALIZATION
# -------------------------------------------------------------
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(150, 100)
    glutCreateWindow(b"Block Breaker - Computer Graphics Mini Project")

    glClearColor(0.06, 0.08, 0.12, 1.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)

    for _ in range(6):
        spawn_target()

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutTimerFunc(0, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()