import math
import random
import sys

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *


WIDTH, HEIGHT = 900, 500
GROUND_Y = 100
PLAYER_X = 120
PLAYER_WIDTH, PLAYER_HEIGHT = 30, 60
POWER_THRESHOLD = 50

score = 0
game_over = False
power_up_active = False

player_y = GROUND_Y
vertical_velocity = 0.0
is_jumping = False
is_ducking = False
is_slashing = False
slash_timer = 0

projectiles = []
banner_pixels = []


def draw_line_bresenham(x1, y1, x2, y2, red=1, green=1, blue=1):
    x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    step_x = 1 if x1 < x2 else -1
    step_y = 1 if y1 < y2 else -1
    error = dx - dy
    glColor3f(red, green, blue)
    glBegin(GL_POINTS)
    while True:
        glVertex2i(x1, y1)
        if x1 == x2 and y1 == y2:
            break
        doubled_error = 2 * error
        if doubled_error > -dy:
            error -= dy
            x1 += step_x
        if doubled_error < dx:
            error += dx
            y1 += step_y
    glEnd()


def draw_line_dda(x1, y1, x2, y2, red=1, green=1, blue=1):
    dx, dy = x2 - x1, y2 - y1
    steps = int(max(abs(dx), abs(dy)))
    glColor3f(red, green, blue)
    glBegin(GL_POINTS)
    if steps == 0:
        glVertex2i(round(x1), round(y1))
    else:
        x_step, y_step = dx / steps, dy / steps
        x, y = float(x1), float(y1)
        for _ in range(steps + 1):
            glVertex2i(round(x), round(y))
            x += x_step
            y += y_step
    glEnd()


def draw_circle_midpoint(center_x, center_y, radius, red=1, green=1, blue=1):
    center_x, center_y, radius = map(int, (center_x, center_y, radius))
    glColor3f(red, green, blue)
    glBegin(GL_POINTS)
    for current_radius in range(radius, 0, -1):
        x, y = 0, current_radius
        decision = 1 - current_radius
        while x <= y:
            points = ((x, y), (y, x), (-x, y), (-y, x),
                      (-x, -y), (-y, -x), (x, -y), (y, -x))
            for offset_x, offset_y in points:
                glVertex2i(center_x + offset_x, center_y + offset_y)
            if decision < 0:
                decision += 2 * x + 3
            else:
                decision += 2 * (x - y) + 5
                y -= 1
            x += 1
    glEnd()


def draw_ellipse_midpoint(center_x, center_y, radius_x, radius_y,
                          red=1, green=0.5, blue=0):
    center_x, center_y, radius_x, radius_y = map(
        int, (center_x, center_y, radius_x, radius_y))
    glColor3f(red, green, blue)
    glBegin(GL_POINTS)
    for current_x_radius, current_y_radius in (
            (radius_x, radius_y),
            (max(1, radius_x - 2), max(1, radius_y - 2))):
        x, y = 0, current_y_radius
        decision_one = (current_y_radius ** 2
                        - current_x_radius ** 2 * current_y_radius
                        + 0.25 * current_x_radius ** 2)
        delta_x = 0
        delta_y = 2 * current_x_radius ** 2 * y
        while delta_x < delta_y:
            for offset_x, offset_y in ((x, y), (-x, y), (x, -y), (-x, -y)):
                glVertex2i(center_x + offset_x, center_y + offset_y)
            x += 1
            delta_x += 2 * current_y_radius ** 2
            if decision_one < 0:
                decision_one += delta_x + current_y_radius ** 2
            else:
                y -= 1
                delta_y -= 2 * current_x_radius ** 2
                decision_one += delta_x - delta_y + current_y_radius ** 2
        decision_two = (current_y_radius ** 2 * (x + 0.5) ** 2
                        + current_x_radius ** 2 * (y - 1) ** 2
                        - current_x_radius ** 2 * current_y_radius ** 2)
        while y >= 0:
            for offset_x, offset_y in ((x, y), (-x, y), (x, -y), (-x, -y)):
                glVertex2i(center_x + offset_x, center_y + offset_y)
            y -= 1
            delta_y -= 2 * current_x_radius ** 2
            if decision_two > 0:
                decision_two += current_x_radius ** 2 - delta_y
            else:
                x += 1
                delta_x += 2 * current_y_radius ** 2
                decision_two += delta_x - delta_y + current_x_radius ** 2
    glEnd()


def draw_polygon_scanline(vertices, red=0.5, green=0.5, blue=0.5):
    if len(vertices) < 3:
        return
    minimum_y = int(min(vertex[1] for vertex in vertices))
    maximum_y = int(max(vertex[1] for vertex in vertices))
    glColor3f(red, green, blue)
    glBegin(GL_POINTS)
    for y in range(minimum_y, maximum_y + 1):
        intersections = []
        for index, first in enumerate(vertices):
            second = vertices[(index + 1) % len(vertices)]
            if first[1] == second[1]:
                continue
            if min(first[1], second[1]) <= y < max(first[1], second[1]):
                intersections.append(first[0] + (y - first[1])
                                     * (second[0] - first[0])
                                     / float(second[1] - first[1]))
        intersections.sort()
        for index in range(0, len(intersections) - 1, 2):
            for x in range(round(intersections[index]),
                           round(intersections[index + 1]) + 1):
                glVertex2i(x, y)
    glEnd()


def precompute_flood_fill(center_x, center_y, width, height):
    minimum_x, maximum_x = center_x - width // 2, center_x + width // 2
    minimum_y, maximum_y = center_y - height // 2, center_y + height // 2
    visited = set()
    queue = [(center_x, center_y)]
    while queue:
        point = queue.pop()
        if point in visited:
            continue
        visited.add(point)
        x, y = point
        for neighbor in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if minimum_x <= neighbor[0] <= maximum_x and minimum_y <= neighbor[1] <= maximum_y:
                if neighbor not in visited:
                    queue.append(neighbor)
    return list(visited)


def draw_flood_filled_banner():
    glColor3f(0.8, 0.1, 0.2)
    glBegin(GL_POINTS)
    for x, y in banner_pixels:
        glVertex2i(x, y)
    glEnd()


INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8


def compute_outcode(x, y, minimum_x, minimum_y, maximum_x, maximum_y):
    code = INSIDE
    if x < minimum_x:
        code |= LEFT
    elif x > maximum_x:
        code |= RIGHT
    if y < minimum_y:
        code |= BOTTOM
    elif y > maximum_y:
        code |= TOP
    return code


def clip_and_draw_laser(x1, y1, x2, y2):
    minimum_x, minimum_y, maximum_x, maximum_y = 0, 0, WIDTH, HEIGHT
    code_one = compute_outcode(x1, y1, minimum_x, minimum_y, maximum_x, maximum_y)
    code_two = compute_outcode(x2, y2, minimum_x, minimum_y, maximum_x, maximum_y)
    while True:
        if not (code_one | code_two):
            draw_line_dda(x1, y1, x2, y2, 1.0, 0.2, 0.2)
            return
        if code_one & code_two:
            return
        outcode = code_one or code_two
        if outcode & TOP:
            denominator = y2 - y1
            if denominator == 0:
                return
            x, y = x1 + (x2 - x1) * (maximum_y - y1) / denominator, maximum_y
        elif outcode & BOTTOM:
            denominator = y2 - y1
            if denominator == 0:
                return
            x, y = x1 + (x2 - x1) * (minimum_y - y1) / denominator, minimum_y
        elif outcode & RIGHT:
            denominator = x2 - x1
            if denominator == 0:
                return
            x, y = maximum_x, y1 + (y2 - y1) * (maximum_x - x1) / denominator
        else:
            denominator = x2 - x1
            if denominator == 0:
                return
            x, y = minimum_x, y1 + (y2 - y1) * (minimum_x - x1) / denominator
        if outcode == code_one:
            x1, y1 = x, y
            code_one = compute_outcode(x1, y1, minimum_x, minimum_y, maximum_x, maximum_y)
        else:
            x2, y2 = x, y
            code_two = compute_outcode(x2, y2, minimum_x, minimum_y, maximum_x, maximum_y)


def draw_knight():
    body_height = PLAYER_HEIGHT // 2 if is_ducking else PLAYER_HEIGHT
    body_y = player_y if is_ducking else player_y + 15
    body = [(PLAYER_X - PLAYER_WIDTH // 2, body_y),
            (PLAYER_X + PLAYER_WIDTH // 2, body_y),
            (PLAYER_X + PLAYER_WIDTH // 2, body_y + body_height),
            (PLAYER_X - PLAYER_WIDTH // 2, body_y + body_height)]
    draw_polygon_scanline(body, 0.6, 0.6, 0.65)
    draw_circle_midpoint(PLAYER_X, body_y + body_height + 10, 12, 0.8, 0.8, 0.8)
    if is_slashing:
        color = (0.2, 0.8, 1.0) if power_up_active else (0.9, 0.9, 0.9)
        blade = [(PLAYER_X + 10, body_y + body_height // 2),
                 (PLAYER_X + 70, body_y + body_height // 2 - 10),
                 (PLAYER_X + 75, body_y + body_height // 2),
                 (PLAYER_X + 70, body_y + body_height // 2 + 10)]
        draw_polygon_scanline(blade, *color)
        draw_line_dda(PLAYER_X + 30, body_y + body_height + 20,
                      PLAYER_X + 80, body_y - 20, 1, 1, 1)


def draw_castle():
    draw_polygon_scanline([(WIDTH - 120, GROUND_Y), (WIDTH, GROUND_Y),
                           (WIDTH, GROUND_Y + 150), (WIDTH - 120, GROUND_Y + 150)],
                          0.3, 0.3, 0.35)
    for index in range(4):
        x = WIDTH - 120 + index * 30
        draw_line_bresenham(x, GROUND_Y + 150, x, GROUND_Y + 170, 0.5, 0.5, 0.5)
        draw_line_bresenham(x, GROUND_Y + 170, x + 15, GROUND_Y + 170, 0.5, 0.5, 0.5)
        draw_line_bresenham(x + 15, GROUND_Y + 170, x + 15, GROUND_Y + 150, 0.5, 0.5, 0.5)
    draw_ellipse_midpoint(WIDTH - 60, GROUND_Y + 80, 15, 30, 0.1, 0.1, 0.1)
    clip_and_draw_laser(WIDTH - 120, GROUND_Y + 50, -500,
                        GROUND_Y + 50 - (200 if is_ducking else 0))
    draw_flood_filled_banner()


def spawn_projectile():
    if len(projectiles) >= 4:
        return
    projectile_type = 'rock' if random.random() > 0.4 else 'fireball'
    y = GROUND_Y + (15 if random.random() > 0.5 else 60)
    projectile = {'x': WIDTH - 120, 'y': y, 'type': projectile_type,
                  'speed': random.uniform(5.5, 8.5)}
    if projectile_type == 'rock':
        projectile['r'] = 12
    else:
        projectile.update(rx=18, ry=10, speed=projectile['speed'] + 2)
    projectiles.append(projectile)


def write_text(x, y, text):
    glRasterPos2i(int(x), int(y))
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character))


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    draw_line_bresenham(0, GROUND_Y, WIDTH, GROUND_Y, 0.3, 0.7, 0.3)
    draw_castle()
    draw_knight()
    for projectile in projectiles:
        if projectile['type'] == 'rock':
            draw_circle_midpoint(projectile['x'], projectile['y'], projectile['r'], 0.4, 0.4, 0.4)
        else:
            draw_ellipse_midpoint(projectile['x'], projectile['y'], projectile['rx'], projectile['ry'], 1, 0.4, 0.1)
    glColor3f(1, 1, 1)
    write_text(30, HEIGHT - 45, f'SCORE: {score}')
    if power_up_active:
        glColor3f(0.2, 0.8, 1)
        write_text(30, HEIGHT - 80, 'ENCHANTED SWORD ACTIVE!')
    if game_over:
        glColor3f(1, 0.2, 0.2)
        write_text(WIDTH // 2 - 100, HEIGHT // 2, "GAME OVER! Press 'R'")
    glutSwapBuffers()


def update(_value):
    global player_y, vertical_velocity, is_jumping, is_slashing
    global slash_timer, score, game_over, power_up_active
    if not game_over:
        if is_jumping:
            player_y += vertical_velocity
            vertical_velocity -= 0.8
            if player_y <= GROUND_Y:
                player_y, vertical_velocity, is_jumping = GROUND_Y, 0, False
        if is_slashing:
            slash_timer -= 1
            if slash_timer <= 0:
                is_slashing = False
        power_up_active = score >= POWER_THRESHOLD
        if random.random() < 0.02:
            spawn_projectile()
        for projectile in projectiles[:]:
            projectile['x'] -= projectile['speed']
            radius_x = projectile.get('r', projectile.get('rx'))
            radius_y = projectile.get('r', projectile.get('ry'))
            left, right = projectile['x'] - radius_x, projectile['x'] + radius_x
            bottom, top = projectile['y'] - radius_y, projectile['y'] + radius_y
            player_height = PLAYER_HEIGHT // 2 if is_ducking else PLAYER_HEIGHT + 20
            sword_hit = is_slashing and left < PLAYER_X + 85 and right > PLAYER_X
            sword_hit = sword_hit and bottom < player_y + player_height and top > player_y
            if sword_hit and (projectile['type'] == 'rock' or power_up_active):
                projectiles.remove(projectile)
                score += 10 if projectile['type'] == 'rock' else 20
                continue
            body_hit = (PLAYER_X - PLAYER_WIDTH // 2 < right
                        and PLAYER_X + PLAYER_WIDTH // 2 > left
                        and player_y < top and player_y + player_height > bottom)
            if body_hit:
                game_over = True
            elif projectile['x'] < -50:
                projectiles.remove(projectile)
                score += 5
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


def keyboard_down(key, _x, _y):
    global is_slashing, slash_timer, score, game_over, power_up_active
    global player_y, vertical_velocity, is_jumping, is_ducking
    if key == b' ' and not is_slashing and not game_over:
        is_slashing, slash_timer = True, 12
    elif key in (b'r', b'R') and game_over:
        score, game_over, power_up_active = 0, False, False
        player_y, vertical_velocity = GROUND_Y, 0
        is_jumping, is_ducking, is_slashing, slash_timer = False, False, False, 0
        projectiles.clear()


def special_down(key, _x, _y):
    global is_jumping, is_ducking, vertical_velocity
    if key == GLUT_KEY_UP and not is_jumping:
        is_jumping, vertical_velocity = True, 14.0
    elif key == GLUT_KEY_DOWN:
        is_ducking = True


def special_up(key, _x, _y):
    global is_ducking
    if key == GLUT_KEY_DOWN:
        is_ducking = False


def main():
    global banner_pixels
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b'Pixel Knight - Complete CG Algorithms')
    glClearColor(0.1, 0.1, 0.15, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    banner_pixels = precompute_flood_fill(WIDTH - 60, GROUND_Y + 120, 20, 30)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_down)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutTimerFunc(0, update, 0)
    glutMainLoop()


if __name__ == '__main__':
    main()
import sys
import random
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# --- Window & Game State ---
WIDTH, HEIGHT = 900, 500
ground_y = 100
score = 0
game_over = False
power_up_active = False
power_threshold = 50

# --- Knight State ---
k_x = 120
k_y = ground_y
k_w, k_h = 30, 60
vy = 0.0
gravity = -0.8
is_jumping = False
is_ducking = False
is_slashing = False
slash_timer = 0

# --- Projectiles & FX ---
projectiles = []  # {'x', 'y', 'type': 'rock'|'fireball', 'radius', 'speed', 'rx', 'ry'}
banner_pixels = [] # Cached flood fill

# ==========================================
# 1. BRESENHAM'S LINE ALGORITHM
# ==========================================
def draw_line_bresenham(x1, y1, x2, y2, r=1, g=1, b=1):
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    while True:
        glVertex2i(x1, y1)
        if x1 == x2 and y1 == y2: break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy; x1 += sx
        if e2 < dx:
            err += dx; y1 += sy
    glEnd()

# ==========================================
# 2. DDA LINE ALGORITHM
# ==========================================
def draw_line_dda(x1, y1, x2, y2, r=1, g=1, b=1):
    dx, dy = x2 - x1, y2 - y1
    steps = int(max(abs(dx), abs(dy)))
    if steps == 0: return
    x_inc, y_inc = dx / steps, dy / steps
    x, y = float(x1), float(y1)
    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    for _ in range(steps + 1):
        glVertex2i(int(round(x)), int(round(y)))
        x += x_inc; y += y_inc
    glEnd()

# ==========================================
# 3. MIDPOINT CIRCLE ALGORITHM
# ==========================================
def draw_circle_midpoint(xc, yc, r, red=1, green=1, blue=1):
    xc, yc, r = int(xc), int(yc), int(r)
    glColor3f(red, green, blue)
    glBegin(GL_POINTS)
    for curr_r in range(r, 0, -1):
        x, y = 0, curr_r
        d = 1 - curr_r
        while x <= y:
            for sx, sy in [(x,y), (y,x), (-x,y), (-y,x), (-x,-y), (-y,-x), (x,-y), (y,-x)]:
                glVertex2i(xc + sx, yc + sy)
            if d < 0: d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
    glEnd()

# ==========================================
# 4. MIDPOINT ELLIPSE ALGORITHM
# ==========================================
def draw_ellipse_midpoint(xc, yc, rx, ry, red=1, green=0.5, blue=0):
    xc, yc, rx, ry = int(xc), int(yc), int(rx), int(ry)
    glColor3f(red, green, blue)
    glBegin(GL_POINTS)
    for crx, cry in [(rx, ry), (max(1, rx-2), max(1, ry-2))]:
        x, y = 0, cry
        d1 = (cry*cry) - (crx*crx*cry) + (0.25*crx*crx)
        dx, dy = 2*cry*cry*x, 2*crx*crx*y
        while dx < dy:
            for sx, sy in [(x,y), (-x,y), (x,-y), (-x,-y)]:
                glVertex2i(xc + sx, yc + sy)
            x += 1
            dx += 2*cry*cry
            if d1 < 0: d1 += dx + (cry*cry)
            else:
                y -= 1
                dy -= 2*crx*crx
                d1 += dx - dy + (cry*cry)
        d2 = ((cry*cry)*((x+0.5)**2)) + ((crx*crx)*((y-1)**2)) - (crx*crx*cry*cry)
        while y >= 0:
            for sx, sy in [(x,y), (-x,y), (x,-y), (-x,-y)]:
                glVertex2i(xc + sx, yc + sy)
            y -= 1
            dy -= 2*crx*crx
            if d2 > 0: d2 += (crx*crx) - dy
            else:
                x += 1
                dx += 2*cry*cry
                d2 += dx - dy + (crx*crx)
    glEnd()

# ==========================================
# 5. SCAN-LINE POLYGON FILLING
# ==========================================
def draw_polygon_scanline(vertices, r=0.5, g=0.5, b=0.5):
    n = len(vertices)
    if n < 3: return
    ymin, ymax = int(min(v[1] for v in vertices)), int(max(v[1] for v in vertices))
    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    for y in range(ymin, ymax + 1):
        intersections = []
        for i in range(n):
            p1, p2 = vertices[i], vertices[(i + 1) % n]
            if p1[1] == p2[1]: continue
            if min(p1[1], p2[1]) <= y <= max(p1[1], p2[1]):
                x_int = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / float(p2[1] - p1[1])
                intersections.append(x_int)
        intersections.sort()
        for i in range(0, len(intersections) - 1, 2):
            for x in range(int(round(intersections[i])), int(round(intersections[i + 1])) + 1):
                glVertex2i(x, y)
    glEnd()

# ==========================================
# 6. FLOOD FILL ALGORITHM (Cached for Performance)
# ==========================================
def precompute_flood_fill(cx, cy, width, height):
    # Simulates a bounded flood fill for the Castle Banner
    visited = set()
    queue = [(cx, cy)]
    xmin, xmax = cx - width//2, cx + width//2
    ymin, ymax = cy - height//2, cy + height//2
    while queue:
        x, y = queue.pop(0)
        if (x, y) not in visited:
            visited.add((x, y))
            for nx, ny in [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]:
                if xmin <= nx <= xmax and ymin <= ny <= ymax:
                    queue.append((nx, ny))
    return list(visited)

def draw_flood_filled_banner():
    glColor3f(0.8, 0.1, 0.2)
    glBegin(GL_POINTS)
    for x, y in banner_pixels:
        glVertex2i(x, y)
    glEnd()

# ==========================================
# 7. COHEN-SUTHERLAND CLIPPING (Targeting Laser)
# ==========================================
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8
def compute_outcode(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE
    if x < xmin: code |= LEFT
    elif x > xmax: code |= RIGHT
    if y < ymin: code |= BOTTOM
    elif y > ymax: code |= TOP
    return code

def clip_and_draw_laser(x1, y1, x2, y2):
    xmin, ymin, xmax, ymax = 0, 0, WIDTH, HEIGHT
    c1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
    c2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)
    accept = False
    while True:
        if not (c1 | c2): 
            accept = True; break
        elif (c1 & c2): 
            break
        else:
            x, y = 0.0, 0.0
            outcode = c1 if c1 else c2
            if outcode & TOP: x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1); y = ymax
            elif outcode & BOTTOM: x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1); y = ymin
            elif outcode & RIGHT: y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1); x = xmax
            elif outcode & LEFT: y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1); x = xmin
            if outcode == c1:
                x1, y1 = x, y
                c1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x, y
                c2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)
    if accept:
        draw_line_dda(x1, y1, x2, y2, 1.0, 0.2, 0.2)

# --- Drawing Entities ---
def draw_knight():
    # Dynamic Hitbox Dimensions based on state
    h = k_h // 2 if is_ducking else k_h
    body_y = k_y if is_ducking else k_y + 15
    
    # Body (Scan-Line)
    body = [(k_x-k_w//2, body_y), (k_x+k_w//2, body_y), (k_x+k_w//2, body_y+h), (k_x-k_w//2, body_y+h)]
    draw_polygon_scanline(body, 0.6, 0.6, 0.65)
    
    # Head (Midpoint Circle)
    head_y = body_y + h + 10
    draw_circle_midpoint(k_x, head_y, 12, 0.8, 0.8, 0.8)

    # Sword Slash Effect (Scan-line + DDA)
    if is_slashing:
        blade_color = (0.2, 0.8, 1.0) if power_up_active else (0.9, 0.9, 0.9)
        blade = [(k_x+10, body_y+h//2), (k_x+70, body_y+h//2-10), (k_x+75, body_y+h//2), (k_x+70, body_y+h//2+10)]
        draw_polygon_scanline(blade, *blade_color)
        draw_line_dda(k_x+30, body_y+h+20, k_x+80, body_y-20, 1.0, 1.0, 1.0) # Motion wind

def draw_castle():
    # Main Tower
    castle_poly = [(WIDTH-120, ground_y), (WIDTH, ground_y), (WIDTH, ground_y+150), (WIDTH-120, ground_y+150)]
    draw_polygon_scanline(castle_poly, 0.3, 0.3, 0.35)
    
    # Battlements (Bresenham Lines)
    for i in range(4):
        bx = WIDTH - 120 + (i * 30)
        draw_line_bresenham(bx, ground_y+150, bx, ground_y+170, 0.5, 0.5, 0.5)
        draw_line_bresenham(bx, ground_y+170, bx+15, ground_y+170, 0.5, 0.5, 0.5)
        draw_line_bresenham(bx+15, ground_y+170, bx+15, ground_y+150, 0.5, 0.5, 0.5)

    # Window (Midpoint Ellipse)
    draw_ellipse_midpoint(WIDTH-60, ground_y+80, 15, 30, 0.1, 0.1, 0.1)

    # Cannon sight laser (Cohen-Sutherland)
    clip_and_draw_laser(WIDTH-120, ground_y+50, -500, ground_y+50 - (200 if is_ducking else 0))

    # Banner (Flood Fill)
    draw_flood_filled_banner()

def spawn_projectile():
    if len(projectiles) < 4:
        p_type = 'rock' if random.random() > 0.4 else 'fireball'
        # Height: high (aimed at head/jump) or low (aimed at feet)
        y_pos = ground_y + 15 if random.random() > 0.5 else ground_y + 60
        speed = random.uniform(5.5, 8.5)
        if p_type == 'rock':
            projectiles.append({'x': WIDTH-120, 'y': y_pos, 'type': 'rock', 'r': 12, 'speed': speed})
        else:
            projectiles.append({'x': WIDTH-120, 'y': y_pos, 'type': 'fireball', 'rx': 18, 'ry': 10, 'speed': speed + 2})

def write_text(x, y, text):
    glRasterPos2i(int(x), int(y))
    for ch in text: glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

# --- Main Display & Update ---
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    # Ground & UI (Bresenham)
    draw_line_bresenham(0, ground_y, WIDTH, ground_y, 0.3, 0.7, 0.3)
    draw_line_bresenham(20, HEIGHT-60, 200, HEIGHT-60, 0.8, 0.8, 0.8)
    draw_line_bresenham(20, HEIGHT-60, 20, HEIGHT-20, 0.8, 0.8, 0.8)
    
    draw_castle()
    draw_knight()

    # Draw Projectiles
    for p in projectiles:
        if p['type'] == 'rock':
            draw_circle_midpoint(p['x'], p['y'], p['r'], 0.4, 0.4, 0.4)
        else:
            draw_ellipse_midpoint(p['x'], p['y'], p['rx'], p['ry'], 1.0, 0.4, 0.1)

    # Text UI
    glColor3f(1, 1, 1)
    write_text(30, HEIGHT-45, f"SCORE: {score}")
    if power_up_active:
        glColor3f(0.2, 0.8, 1.0)
        write_text(30, HEIGHT-80, "ENCHANTED SWORD ACTIVE!")
    
    if game_over:
        glColor3f(1.0, 0.2, 0.2)
        write_text(WIDTH//2 - 100, HEIGHT//2, "GAME OVER! Press 'R'")
        
    glutSwapBuffers()

def update(value):
    global k_y, vy, is_jumping, is_slashing, slash_timer, score, game_over, power_up_active

    if not game_over:
        # Physics
        if is_jumping:
            k_y += vy
            vy += gravity
            if k_y <= ground_y:
                k_y = ground_y
                is_jumping = False
                vy = 0

        # Slash Timer
        if is_slashing:
            slash_timer -= 1
            if slash_timer <= 0: is_slashing = False

        # Power Up Check
        if score >= power_threshold: power_up_active = True

        # Projectile Logic
        if random.random() < 0.02: spawn_projectile()

        for p in projectiles[:]:
            p['x'] -= p['speed']
            
            # Hitboxes
            p_left = p['x'] - (p['r'] if p['type']=='rock' else p['rx'])
            p_right = p['x'] + (p['r'] if p['type']=='rock' else p['rx'])
            p_bot = p['y'] - (p['r'] if p['type']=='rock' else p['ry'])
            p_top = p['y'] + (p['r'] if p['type']=='rock' else p['ry'])

            k_hit_h = k_h // 2 if is_ducking else k_h + 20
            
            # 1. Check Sword Collision
            if is_slashing and (k_x < p_left < k_x + 85) and (k_y <= p['y'] <= k_y + k_hit_h):
                if p['type'] == 'rock':
                    projectiles.remove(p)
                    score += 10
                    continue
                elif p['type'] == 'fireball' and power_up_active:
                    projectiles.remove(p)
                    score += 20
                    continue

            # 2. Check Player Body Collision
            if (k_x - k_w//2 < p_right and k_x + k_w//2 > p_left):
                if (k_y < p_top and k_y + k_hit_h > p_bot):
                    game_over = True

            # Offscreen
            if p['x'] < -50 and p in projectiles:
                projectiles.remove(p)
                score += 5 # Dodged

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

# --- Input Handling ---
def keyboard_down(key, x, y):
    global is_slashing, slash_timer, game_over, score, projectiles, power_up_active
    if key == b' ' and not is_slashing and not game_over:
        is_slashing = True
        slash_timer = 12
    elif key in (b'r', b'R') and game_over:
        score, game_over, power_up_active = 0, False, False
        projectiles.clear()

def special_down(key, x, y):
    global is_jumping, is_ducking, vy
    if key == GLUT_KEY_UP and not is_jumping:
        is_jumping = True
        vy = 14.0
    elif key == GLUT_KEY_DOWN:
        is_ducking = True

def special_up(key, x, y):
    global is_ducking
    if key == GLUT_KEY_DOWN:
        is_ducking = False

def main():
    global banner_pixels
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Pixel Knight - Complete CG Algorithms")
    glClearColor(0.1, 0.1, 0.15, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    
    # Precompute Flood Fill to maintain 60 FPS in loop
    banner_pixels = precompute_flood_fill(WIDTH-60, ground_y+120, 20, 30)

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_down)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutTimerFunc(0, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()