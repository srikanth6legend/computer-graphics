import sys
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *

# ==========================================
# GAME STATE & CONFIGURATION
# ==========================================
WIDTH, HEIGHT = 1000, 600
GROUND_Y = 120

score = 0
game_over = False
power_up_active = False
power_threshold = 50

# Knight Physics & State
k_x = 150
k_y = GROUND_Y
k_w, k_h = 36, 64
vy = 0.0
gravity = -1.4
jump_power = 18.0
is_jumping = False
is_ducking = False
is_slashing = False
slash_timer = 0

projectiles = []
flag_pixels = []
PROJECTILE_SPAWN_CHANCE = 0.035
PROJECTILE_SPEED_MIN = 14.0
PROJECTILE_SPEED_MAX = 22.0
POWER_UP_SPEED_MULTIPLIER = 1.35
PROJECTILE_SPAWN_MIN_FRAMES = 15
PROJECTILE_SPAWN_MAX_FRAMES = 21
projectile_spawn_timer = 1

# ==========================================
# 1. DDA LINE ALGORITHM
# ==========================================
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

# ==========================================
# 2. BRESENHAM'S LINE ALGORITHM
# ==========================================
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

# ==========================================
# 3. MIDPOINT CIRCLE ALGORITHM
# ==========================================
def draw_circle_midpoint(xc, yc, r, red=1.0, green=1.0, blue=1.0):
    xc, yc, r = int(xc), int(yc), int(r)
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
    glEnd()

# ==========================================
# 4. MIDPOINT ELLIPSE ALGORITHM
# ==========================================
def draw_ellipse_midpoint(xc, yc, rx, ry, red=1.0, green=1.0, blue=1.0):
    xc, yc, rx, ry = int(xc), int(yc), int(rx), int(ry)
    glColor3f(red, green, blue)
    glBegin(GL_POINTS)
    for curr_rx, curr_ry in [(rx, ry), (max(1, rx - 1), max(1, ry - 1))]:
        x = 0
        y = curr_ry
        d1 = (curr_ry**2) - (curr_rx**2 * curr_ry) + (0.25 * curr_rx**2)
        dx = 2 * curr_ry**2 * x
        dy = 2 * curr_rx**2 * y

        while dx < dy:
            for sx, sy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                glVertex2i(xc + sx, yc + sy)
            x += 1
            dx += 2 * curr_ry**2
            if d1 < 0:
                d1 += dx + (curr_ry**2)
            else:
                y -= 1
                dy -= 2 * curr_rx**2
                d1 += dx - dy + (curr_ry**2)

        d2 = ((curr_ry**2) * ((x + 0.5)**2)) + ((curr_rx**2) * ((y - 1)**2)) - (curr_rx**2 * curr_ry**2)
        while y >= 0:
            for sx, sy in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                glVertex2i(xc + sx, yc + sy)
            y -= 1
            dy -= 2 * curr_rx**2
            if d2 > 0:
                d2 += (curr_rx**2) - dy
            else:
                x += 1
                dx += 2 * curr_ry**2
                d2 += dx - dy + (curr_rx**2)
    glEnd()

# ==========================================
# 5. SCAN-LINE POLYGON FILLING
# ==========================================
def draw_polygon_scanline(vertices, r=1.0, g=1.0, b=1.0):
    n = len(vertices)
    if n < 3: return
    ymin = int(min(v[1] for v in vertices))
    ymax = int(max(v[1] for v in vertices))

    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    for y in range(ymin, ymax + 1):
        intersections = []
        for i in range(n):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % n]
            if p1[1] == p2[1]: continue
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

# ==========================================
# 6. FLOOD FILL ALGORITHM
# ==========================================
def compute_flood_fill(cx, cy, width, height):
    """
    Computes flood fill pixels bounded by a rectangle to avoid real-time
    recursion limits and maintain 60FPS. Cached to a list.
    """
    visited = set()
    queue = [(cx, cy)]
    xmin, xmax = cx - width // 2, cx + width // 2
    ymin, ymax = cy - height // 2, cy + height // 2
    
    while queue:
        x, y = queue.pop(0)
        if (x, y) not in visited:
            visited.add((x, y))
            for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                if xmin <= nx <= xmax and ymin <= ny <= ymax:
                    queue.append((nx, ny))
    return list(visited)

def render_cached_flood_fill(pixels, r, g, b):
    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    for px, py in pixels:
        glVertex2i(px, py)
    glEnd()

# ==========================================
# 7. COHEN-SUTHERLAND LINE CLIPPING
# ==========================================
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

def compute_outcode(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE
    if x < xmin: code |= LEFT
    elif x > xmax: code |= RIGHT
    if y < ymin: code |= BOTTOM
    elif y > ymax: code |= TOP
    return code

def clip_and_draw_laser(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    c1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
    c2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)
    accept = False

    while True:
        if not (c1 | c2):
            accept = True
            break
        elif (c1 & c2):
            break
        else:
            x, y = 0.0, 0.0
            outcode = c1 if c1 else c2

            if outcode & TOP:
                if y2 == y1:
                    break
                x = x1 + (x2 - x1) * (ymax - y1) / float(y2 - y1)
                y = ymax
            elif outcode & BOTTOM:
                if y2 == y1:
                    break
                x = x1 + (x2 - x1) * (ymin - y1) / float(y2 - y1)
                y = ymin
            elif outcode & RIGHT:
                if x2 == x1:
                    break
                y = y1 + (y2 - y1) * (xmax - x1) / float(x2 - x1)
                x = xmax
            elif outcode & LEFT:
                if x2 == x1:
                    break
                y = y1 + (y2 - y1) * (xmin - x1) / float(x2 - x1)
                x = xmin

            if outcode == c1:
                x1, y1 = x, y
                c1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x, y
                c2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)

    if accept:
        draw_line_dda(x1, y1, x2, y2, 1.0, 0.1, 0.1)

# ==========================================
# DRAWING ENTITIES (Inspired by Images)
# ==========================================
def draw_environment():
    # River / Bottom Water
    draw_polygon_scanline([(0, 0), (WIDTH, 0), (WIDTH, GROUND_Y - 40), (0, GROUND_Y - 40)], 0.2, 0.45, 0.5)
    
    # Swamp Bridge (Purple-grey bricks)
    bridge_poly = [(0, GROUND_Y - 40), (WIDTH, GROUND_Y - 40), (WIDTH, GROUND_Y), (0, GROUND_Y)]
    draw_polygon_scanline(bridge_poly, 0.45, 0.4, 0.5)
    
    # Bridge details & cracks (Bresenham)
    for i in range(0, WIDTH, 80):
        draw_line_bresenham(i, GROUND_Y, i, GROUND_Y - 40, 0.25, 0.2, 0.3)
        draw_line_bresenham(i, GROUND_Y - 20, i + 80, GROUND_Y - 20, 0.25, 0.2, 0.3)

    # Background Pillars (Scan-line)
    pillar1 = [(WIDTH - 250, GROUND_Y), (WIDTH - 150, GROUND_Y), (WIDTH - 150, HEIGHT), (WIDTH - 250, HEIGHT)]
    draw_polygon_scanline(pillar1, 0.55, 0.45, 0.5)
    
    # Hanging Vines (DDA & Bresenham)
    for i in range(20, WIDTH - 200, 120):
        draw_line_bresenham(i, HEIGHT, i + 20, HEIGHT - 80, 0.15, 0.25, 0.2)
        draw_line_dda(i + 20, HEIGHT - 80, i - 10, HEIGHT - 140, 0.15, 0.25, 0.2)
        draw_line_bresenham(i - 10, HEIGHT - 140, i + 15, HEIGHT - 190, 0.15, 0.25, 0.2)

def draw_castle_and_cannon():
    # Main Castle Structure (Purple-grey hues)
    draw_polygon_scanline([(WIDTH - 150, GROUND_Y), (WIDTH, GROUND_Y), (WIDTH, 450), (WIDTH - 150, 450)], 0.6, 0.6, 0.7)
    draw_polygon_scanline([(WIDTH - 180, GROUND_Y), (WIDTH - 150, GROUND_Y), (WIDTH - 150, 300), (WIDTH - 180, 300)], 0.5, 0.5, 0.6)
    
    # Battlements
    for i in range(0, 150, 30):
        draw_polygon_scanline([(WIDTH - 150 + i, 450), (WIDTH - 135 + i, 450), (WIDTH - 135 + i, 480), (WIDTH - 150 + i, 480)], 0.6, 0.6, 0.7)
        draw_line_bresenham(WIDTH - 150 + i, 450, WIDTH - 150 + i, 480, 0.3, 0.3, 0.4)

    # Castle Door (Ellipse intersecting ground)
    draw_ellipse_midpoint(WIDTH - 75, GROUND_Y + 10, 40, 60, 0.2, 0.15, 0.15)
    
    # Window
    draw_ellipse_midpoint(WIDTH - 75, 350, 15, 30, 0.1, 0.1, 0.1)

    # Flags (Render precomputed flood fill)
    render_cached_flood_fill(flag_pixels, 0.8, 0.2, 0.3)
    draw_line_dda(WIDTH - 75, 480, WIDTH - 75, 550, 0.1, 0.1, 0.1) # Flag pole

    # Cannon Base (Wooden semicircle)
    draw_polygon_scanline([(WIDTH - 210, GROUND_Y), (WIDTH - 150, GROUND_Y), (WIDTH - 150, GROUND_Y + 40), (WIDTH - 210, GROUND_Y + 40)], 0.7, 0.5, 0.3)
    draw_circle_midpoint(WIDTH - 180, GROUND_Y + 40, 30, 0.7, 0.5, 0.3)
    
    # Cannon Barrel (Dark iron)
    draw_polygon_scanline([(WIDTH - 240, GROUND_Y + 60), (WIDTH - 160, GROUND_Y + 90), (WIDTH - 150, GROUND_Y + 60), (WIDTH - 230, GROUND_Y + 30)], 0.25, 0.25, 0.3)
    draw_ellipse_midpoint(WIDTH - 240, GROUND_Y + 45, 12, 20, 0.15, 0.15, 0.2) # Barrel opening

    # Targeting Laser (Cohen-Sutherland clipped to screen)
    laser_y_target = GROUND_Y + 45 - (150 if is_ducking else 0)
    clip_and_draw_laser(WIDTH - 240, GROUND_Y + 45, -100, laser_y_target, 0, 0, WIDTH, HEIGHT)

def draw_knight():
    # Dynamic positions based on ducking
    h = (k_h // 2) if is_ducking else k_h
    body_y = k_y if is_ducking else k_y + 12

    # Legs
    if not is_ducking:
        draw_polygon_scanline([(k_x - 12, k_y), (k_x - 4, k_y), (k_x - 4, body_y), (k_x - 12, body_y)], 0.4, 0.4, 0.45)
        draw_polygon_scanline([(k_x + 4, k_y), (k_x + 12, k_y), (k_x + 12, body_y), (k_x + 4, body_y)], 0.4, 0.4, 0.45)

    # Chibi Body
    draw_polygon_scanline([(k_x - k_w//2, body_y), (k_x + k_w//2, body_y), (k_x + k_w//2, body_y + h), (k_x - k_w//2, body_y + h)], 0.75, 0.75, 0.8)
    draw_line_bresenham(k_x - k_w//2, body_y, k_x + k_w//2, body_y, 0.2, 0.2, 0.2)
    draw_line_bresenham(k_x - k_w//2, body_y + h, k_x + k_w//2, body_y + h, 0.2, 0.2, 0.2)

    # Head (Helmet)
    head_y = body_y + h + 14
    draw_circle_midpoint(k_x, head_y, 18, 0.8, 0.8, 0.85)

    # T-Visor (Multiple DDA lines for thickness)
    for offset in range(-2, 3):
        draw_line_dda(k_x - 12, head_y + 4 + offset, k_x + 12, head_y + 4 + offset, 0.1, 0.1, 0.1)
    for offset in range(-2, 3):
        draw_line_dda(k_x + offset, head_y + 4, k_x + offset, head_y - 8, 0.1, 0.1, 0.1)

    # Sword and Arm
    arm_y = body_y + h // 2
    draw_circle_midpoint(k_x + 15, arm_y, 8, 0.6, 0.6, 0.65)

    if is_slashing:
        blade_c = (0.2, 0.9, 1.0) if power_up_active else (0.9, 0.9, 0.9)
        # Hilt
        draw_polygon_scanline([(k_x + 20, arm_y - 6), (k_x + 30, arm_y + 6), (k_x + 36, arm_y), (k_x + 26, arm_y - 12)], 0.8, 0.3, 0.1)
        # Blade
        draw_polygon_scanline([(k_x + 26, arm_y), (k_x + 90, arm_y + 20), (k_x + 95, arm_y + 10), (k_x + 32, arm_y - 10)], *blade_c)
        # Wind Slash Effect
        draw_line_dda(k_x + 40, arm_y + 40, k_x + 110, arm_y, 1.0, 1.0, 1.0)
    else:
        # Idle Sword
        draw_polygon_scanline([(k_x + 10, arm_y - 20), (k_x + 20, arm_y - 10), (k_x + 10, arm_y - 5), (k_x, arm_y - 15)], 0.8, 0.3, 0.1)
        draw_polygon_scanline([(k_x + 15, arm_y - 15), (k_x + 45, arm_y + 15), (k_x + 40, arm_y + 20), (k_x + 10, arm_y - 10)], 0.9, 0.9, 0.9)

def draw_text(x, y, text):
    glRasterPos2i(int(x), int(y))
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

# ==========================================
# MAIN DISPLAY & UPDATE LOOP
# ==========================================
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    draw_environment()
    draw_castle_and_cannon()
    draw_knight()

    # Draw Projectiles
    for p in projectiles:
        if p['type'] == 'rock':
            draw_circle_midpoint(p['x'], p['y'], p['radius'], 0.35, 0.35, 0.35)
            # Texture lines
            draw_line_bresenham(p['x']-8, p['y']+5, p['x']+8, p['y']-5, 0.2, 0.2, 0.2)
        elif p['type'] == 'fireball':
            draw_ellipse_midpoint(p['x'], p['y'], p['rx'], p['ry'], 1.0, 0.4, 0.1)
            draw_ellipse_midpoint(p['x'] + 5, p['y'], p['rx'] - 5, p['ry'] - 4, 1.0, 0.8, 0.2) # Inner core

    # UI Elements
    glColor3f(1.0, 1.0, 1.0)
    draw_text(20, HEIGHT - 35, f"SCORE: {score}")
    
    if power_up_active:
        glColor3f(0.2, 0.9, 1.0)
        draw_text(20, HEIGHT - 65, "ENCHANTED SWORD: Fireballs can be slashed!")
        
    if game_over:
        glColor3f(1.0, 0.2, 0.2)
        draw_text(WIDTH // 2 - 100, HEIGHT // 2, "GAME OVER! Press 'R' to Restart")

    glutSwapBuffers()

def update(value):
    global k_y, vy, is_jumping, is_slashing, slash_timer, score, game_over, power_up_active
    global projectile_spawn_timer

    if not game_over:
        # Physics Jump
        if is_jumping:
            k_y += vy
            vy += gravity
            if k_y <= GROUND_Y:
                k_y = GROUND_Y
                is_jumping = False
                vy = 0

        # Slash Cooldown
        if is_slashing:
            slash_timer -= 1
            if slash_timer <= 0:
                is_slashing = False

        # Power Up Unlock
        if score >= power_threshold:
            power_up_active = True

        # Use a cooldown so spawning stays responsive instead of depending on luck.
        projectile_spawn_timer -= 1
        if projectile_spawn_timer <= 0 and len(projectiles) < 5:
            p_type = 'rock' if random.random() > 0.45 else 'fireball'
            spawn_y = GROUND_Y + (15 if random.random() > 0.5 else 75)
            speed_multiplier = POWER_UP_SPEED_MULTIPLIER if power_up_active else 1.0
            speed = random.uniform(PROJECTILE_SPEED_MIN, PROJECTILE_SPEED_MAX) * speed_multiplier
            projectile_spawn_timer = random.randint(PROJECTILE_SPAWN_MIN_FRAMES,
                                                     PROJECTILE_SPAWN_MAX_FRAMES)
            
            if p_type == 'rock':
                projectiles.append({'x': WIDTH - 240, 'y': spawn_y, 'type': 'rock', 'radius': 15, 'speed': speed})
            else:
                projectiles.append({'x': WIDTH - 240, 'y': spawn_y, 'type': 'fireball', 'rx': 22, 'ry': 12, 'speed': speed + 4.0})

        # Update Projectiles & Collisions
        for p in projectiles[:]:
            p['x'] -= p['speed']
            
            p_w = p['radius'] if p['type'] == 'rock' else p['rx']
            p_h = p['radius'] if p['type'] == 'rock' else p['ry']
            hitbox_h = (k_h // 2) + 20 if is_ducking else k_h + 30

            # Sword Hit Detection
            sword_overlaps = (k_x < p['x'] + p_w and k_x + 100 > p['x'] - p_w
                              and k_y < p['y'] + p_h
                              and k_y + hitbox_h > p['y'] - p_h)
            if is_slashing and sword_overlaps:
                if p['type'] == 'rock' or (p['type'] == 'fireball' and power_up_active):
                    projectiles.remove(p)
                    score += 10 if p['type'] == 'rock' else 20
                    continue
            
            # Knight Body Collision
            if (k_x - k_w//2 < p['x'] + p_w and k_x + k_w//2 > p['x'] - p_w):
                if (k_y < p['y'] + p_h and k_y + hitbox_h > p['y'] - p_h):
                    game_over = True

            # Dodged successfully
            if p['x'] < -40 and p in projectiles:
                projectiles.remove(p)
                score += 5

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

# ==========================================
# INPUT CONTROLS
# ==========================================
def keyboard_down(key, x, y):
    global is_slashing, slash_timer, game_over, score, power_up_active
    global k_y, vy, is_jumping, is_ducking, projectile_spawn_timer
    if key == b' ' and not is_slashing and not game_over:
        is_slashing = True
        slash_timer = 15
    elif key in (b'r', b'R') and game_over:
        score = 0
        game_over = False
        power_up_active = False
        k_y = GROUND_Y
        vy = 0.0
        is_jumping = False
        is_ducking = False
        is_slashing = False
        slash_timer = 0
        projectile_spawn_timer = 1
        projectiles.clear()

def special_down(key, x, y):
    global is_jumping, is_ducking, vy
    if key == GLUT_KEY_UP and not is_jumping:
        is_jumping = True
        vy = jump_power
    elif key == GLUT_KEY_DOWN:
        is_ducking = True

def special_up(key, x, y):
    global is_ducking
    if key == GLUT_KEY_DOWN:
        is_ducking = False

# ==========================================
# INITIALIZATION
# ==========================================
def main():
    global flag_pixels
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"Pixel Knight - Aesthetic Overhaul")
    
    # Dark Teal Swamp Sky Background
    glClearColor(0.22, 0.32, 0.35, 1.0)
    glPointSize(1.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)

    # Pre-compute flood fills before the game loop starts to ensure smooth 60 FPS
    flag_pixels = compute_flood_fill(WIDTH - 75, 520, 40, 40)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_down)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutTimerFunc(0, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()