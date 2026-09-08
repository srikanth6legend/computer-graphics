from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10

import numpy as np

rot_angle = 0.0

def init_scene():
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [3.0, 4.0, 4.0, 1.0]) # Light position
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    
    # 4x4 Grid procedural texture
    grid = np.zeros((4, 4, 3), dtype=np.uint8)
    for i in range(4):
        for j in range(4):
            grid[i, j] = [210, 210, 210] if (i + j) % 2 == 0 else [60, 120, 180]
    
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 4, 4, 0, GL_RGB, GL_UNSIGNED_BYTE, grid)
    glEnable(GL_TEXTURE_2D)

def draw_watermarks_2d():
    glDisable(GL_LIGHTING); glDisable(GL_TEXTURE_2D); glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, 600, 0, 600)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(0.85, 0.85, 0.87)
    for y in [30, 80, 520, 560]:
        for x in [30, 320]:
            glRasterPos2i(x, y)
            for ch in "ALLEN CHRIST A - 2411021061266": glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(ch))
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING); glEnable(GL_TEXTURE_2D)

def display():
    global rot_angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0, 2, 5, 0, 0, 0, 0, 1, 0)
    
    glPushMatrix()
    glRotatef(rot_angle, 0.5, 1.0, 0.0) # Rotation animation
    glBegin(GL_QUADS)
    for nx, ny, nz, v in [(0,0,1,[(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]), (0,1,0,[(-1,1,-1),(-1,1,1),(1,1,1),(1,1,-1)])]:
        glNormal3f(nx, ny, nz) # Shading
        glTexCoord2f(0,0); glVertex3fv(v[0]) # Texture coordinates
        glTexCoord2f(1,0); glVertex3fv(v[1])
        glTexCoord2f(1,1); glVertex3fv(v[2])
        glTexCoord2f(0,1); glVertex3fv(v[3])
    glEnd()
    glPopMatrix()
    
    draw_watermarks_2d()
    glutSwapBuffers()

def update(v):
    global rot_angle
    rot_angle += 1.0
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(600, 600)
glutCreateWindow(b"Mini Project: Shading, Texture and Animation")
init_scene()
glMatrixMode(GL_PROJECTION); gluPerspective(45.0, 1.0, 1.0, 20.0); glMatrixMode(GL_MODELVIEW)
glutDisplayFunc(display)
glutTimerFunc(0, update, 0)
glutMainLoop()
