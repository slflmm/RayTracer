# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 15:43:06 2015

@author: Michael
"""
from __future__ import division
import sys
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
except:
    print('ERROR: PyOpenGL not installed properly.')
    sys.exit()

from ModelViewWindow import *        
from GLDrawHelper import *
from numpy import arccos as acos
from numpy import pi

class KochPyramid(Model):
    
    def init(self):
        '''
        This init method gets called after OpenGL context creation. This is
        because glut doesn't create opengl context until a window is actually 
        created. On the other hand python's __init__ gets called during object
        instantiation which might happen before opengl context is created.
        '''
        Model.init(self) # since we are overriding Model.init by creating an init() function
                        # we need to first let Model.init initialize itself (basically creates display list)
        initGL()
        
    def draw_scene(self):
        '''
        View class takes care of setting the projection matrix and lookat.
        Adding them here would override those calls and won't let mouse/keyboard
        to work...because the mouse and keyboard functions only know about the View's api.
        '''
        #'''       
        
        #  The light source position should be defined here so that it is in world
        #  coordinates and undergoes the same transformation as the pyramid.
        
        glLightfv(GL_LIGHT0,GL_POSITION,[ -0.2, -0.1, 1., 1. ] )

        glPushMatrix()
        glTranslate(0, 0, .5)  #
        glScalef(1/16.0, 1/16.0, 1/16.0)

        #  Show a little shiny sphere in the scene so that you can get a better sense of where
        #  the light source is.
        
        gluSphere(self.pQuadric,.5, 20, 20)

        glPopMatrix()
        #'''
        glPushMatrix()
        glTranslate(-1./2, -sqrt(3)/4, 0)
        
        self.drawKochPyramid(3)    #   You may change this line to draw the Koch pyramid to different levels.
        glPopMatrix()
        
    def  basicTriangle(self):     #  has one vertex at origin, one at (1,0,0), ...
        glNormal3f(0, 0, 1)
        glVertex(0, 0, 0)
        glVertex(1.0, 0, 0)
        glVertex( 1/2.0, sqrt(3)/2.0, 0)

    '''
    Helper method!
    Draws the pyramid's faces.
    '''
    def drawFaces(self, level):
        glPushMatrix()
        glRotatef(180, 0, 0, 1) # let these be the upper face of pyramid
        glRotatef(acos(1.0/3.0)*(180.0/pi), 1,0,0) # apply the dihedral angle
        self.drawKochPyramid(level - 1)
        glPopMatrix()

        glPushMatrix()
        glTranslate(-1,0,0)
        glRotatef(300, 0, 0, 1) # let these be the upper face of pyramid
        glRotatef(acos(1.0/3.0)*(180.0/pi), 1,0,0) # apply the dihedral angle
        self.drawKochPyramid(level - 1)
        glPopMatrix()

        glPushMatrix()
        glTranslate(-1/2.0, -sqrt(3)/2.0, 0)
        glRotatef(420, 0, 0, 1) # let these be the lower right face of pyramid
        glRotatef(acos(1.0/3.0)*(180.0/pi), 1,0,0) # apply the dihedral angle
        self.drawKochPyramid(level - 1)
        glPopMatrix()

    def drawKochPyramid(self, level):
        if (level == 0):
            glBegin(GL_TRIANGLES)
            self.basicTriangle()
            glEnd()
        else: 

#TODO  ---------------   BEGIN SOLUTION:  ADD YOUR CODE HERE ------------------------------
            glPushMatrix()
            glScalef(1.0/3.0, 1.0/3.0, 1.0/3.0)

            # first, draw the non-pyramidal faces
            self.drawKochPyramid(level-1)
            
            glPushMatrix()
            glTranslate(1/2.0, sqrt(3)/2.0, 0)
            self.drawKochPyramid(level-1)
            glTranslate(1/2.0, sqrt(3)/2.0, 0)
            self.drawKochPyramid(level-1)
            glPopMatrix()

            glPushMatrix()
            glTranslate(1.0, 0, 0)
            self.drawKochPyramid(level-1)

            glPushMatrix()
            glTranslate(1.0, 0, 0)
            self.drawKochPyramid(level-1)
            glPopMatrix()
            
            glTranslate(1/2.0, sqrt(3)/2.0, 0)
            self.drawKochPyramid(level-1)
            glPopMatrix()

            # next, draw the pyramids
            glPushMatrix()

            # start with the lower left pyramid and draw its three faces
            glTranslate(1/2.0 + 1, sqrt(3)/2.0, 0)
            self.drawFaces(level) # see helper method

            # do the upper pyramid
            glPushMatrix()
            glTranslate(1/2.0, sqrt(3)/2.0, 0)
            self.drawFaces(level)
            glPopMatrix()

            # do the lower right pyramid
            glTranslate(1, 0, 0)
            self.drawFaces(level)

            glPopMatrix()

            glPopMatrix()

#  ---------------    END SOLUTION ------------------------------

   
def initGL():
    glClearColor(1.0, 1.0, 1.0, 1.0)   #  defines background color when you run glClear(GL_COLOR_BUFFER_BIT)
    glClearDepth(1)                    #  defines background depth when you run glClear(GL_DEPTH_BUFFER_BIT)
    glDisable(GL_CULL_FACE)    
    glEnable(GL_LIGHTING)
            
    glEnable(GL_NORMALIZE)
    glLightModelf(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
    glLightfv(GL_LIGHT0,GL_POSITION,[ 0.4, 0.5, 1., 1. ] )
    glLightfv(GL_LIGHT0,GL_AMBIENT,[ 1.0, 1.0, 1.0, 1.0 ])
    glLightfv(GL_LIGHT0,GL_DIFFUSE,[ 1.0, 1.0, 1.0, 1.0 ])
    glLightfv(GL_LIGHT0,GL_SPECULAR,[ 1.0, 1.0, 1.0, 1.0 ])
    
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, [0, 0,  1])
    '''
    glLightf( GL_LIGHT0, GL_SPOT_EXPONENT,  80.0)
    glLightf( GL_LIGHT0, GL_SPOT_CUTOFF,    4.0)
    '''
    glLightf( GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1)
    glLightf( GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.0)
    glLightf( GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.05) 
    
    glEnable(GL_LIGHT0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glShadeModel(GL_SMOOTH)    
  
    matColor =  [0.0, 0.9, 0.9, 1.0]
    specColor = [.9, 0.0, 0.0, 1.0]
    ambColor =  [0.1, 0.1, 0.1, 1.0]
    nshininess = [128, 128.0, 128, 1 ]

    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE,   matColor)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  specColor)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT,   ambColor)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, nshininess)
    


def main():
    # glutInit and glutInitDisplayMode needs to be called because GLUTWindow
    # only deals with inidividual windows
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    
    
    cam_spec = {'eye' : [0, -1, 1.5], 'center' : [0, 0, 0], 'up' : [0, 1, 0], 
                 'fovy': 40, 'aspect': 1.0, 'near' : 0.01, 'far' : 200.0}

    kp = KochPyramid()
    cam = View(kp, cam_spec)    
    GLUTWindow('Koch Pyramid', cam, window_size = (512, 512), window_pos =(520, 0))
    glutMainLoop()

        
if __name__ == '__main__':
    main()



