# -*- coding: utf-8 -*-
"""
Garden Scene
"""
from OpenGL.GL import *
import numpy as np
from GLDrawHelper import *

from ModelViewWindow import Model
from LSystem import LSystem
from BicubicPatch import BicubicPatch
from FlythroughCamera import FlythroughCamera
from HermiteCurve import HermiteCurve

class GardenScene(Model):
    '''
    Scene with multiple 3D L-System and a checkerboard as ground-plane
    subscene_list is a list of dictionaries that contains the (x, y) position 
    on the ground plane and the L-system.
    '''
    def __init__(self, terrain_model, subscene_list = []):
        Model.__init__(self)
        self.terrain_model = terrain_model
        self.subscene_list = subscene_list
    
    def init(self):
        Model.init(self)
        if(hasattr(self.terrain_model, 'init')):
            self.terrain_model.init()
        for scene in self.subscene_list:
            if(hasattr(scene, 'init')):
                scene.init()
            
    def add_subscene(self, subscene):
        self.subscene_list.append(subscene)
        
    def draw_scene(self):
        '''
        Draw the garden scene here. A sample solution is provided. You can
        build on top of it or replace it with your own approach.
        '''
        #TODO ----------- BEGIN SOLUTION ---------------

        # draw 3D coordinate axes
        glPushMatrix()
        glScalef(.25, .25, .25)
        draw3DCoordinateAxesQuadrics(self.pQuadric)
        glPopMatrix()
        
        # Replace the following checkerboard ground with your terrain and draw
        # a tiled pathway
        # glPushMatrix()
        # glRotate(-90, 1, 0, 0)
        # drawCheckerBoard(scale = [8, 8], check_colors = [[0.8, 0.8, 0.8], [0.2, 0.2, 0.2]])
        # glPopMatrix()
        
        ''' An example of how the Bicubic patch can be drawn and then the resulting
        points and tangents being retrieved '''

        # made the sky blue
        glClearColor(102./255, 178./255, 1, 1)

        # xz plane scaling
        xz_scale = 5


        glPushMatrix()

        # The argument 'False' is because we don't want to draw the coordinate axes
        glScalef(xz_scale, 1, xz_scale) # stretch the patch in the xz direction
        (X, Y, Z, DsX, DsY, DsZ, DtX, DtY, DtZ) = self.terrain_model.draw_scene(False)   
        glPopMatrix()

        # here is the wonderful and beautiful tiled pathway 
        tile_count = len(Y)/4
        tile_scale = 1.0/13
        for i in range(tile_count):

            glPushMatrix()

            x_proportion = 5*len(X)/8 # select x coordinates for the terrain as 5/8 through
            y_spacing = len(X[x_proportion])/tile_count # keep the spacing between tiles large enough

            # magic number in translate, ds and dt:
            # 2 --> start the path far enough from the terrain's edge that tiles aren't half-off the terrain
            # + 0.5*tile_scale in the y position --> so that the tile lies on top of the plane
            glTranslatef(xz_scale*X[x_proportion][2+i*y_spacing], Y[x_proportion][2+i*y_spacing]+0.5*tile_scale, xz_scale*Z[x_proportion][2+i*y_spacing])

            ds = [xz_scale*DsX[x_proportion][2+i*y_spacing], DsY[x_proportion][2+i*y_spacing], xz_scale*DsZ[x_proportion][2+i*y_spacing]]
            dt = [xz_scale*DtX[x_proportion][2+i*y_spacing], DtY[x_proportion][2+i*y_spacing], xz_scale*DtZ[x_proportion][2+i*y_spacing]]

            normal = np.cross(dt, ds) # so the normal faces the right way
            normal /= np.linalg.norm(normal)

            normal_ = np.cross(normal, [0, 1, 0])

            # only rotate if you're not already at the normal
            if (not(normal_[0] == 0 and normal_[1] == 0 and normal[2] == 0)):

                normal_ /= np.linalg.norm(normal_)

                normal__ = np.cross(normal_, normal)
                normal__ /= np.linalg.norm(normal__)

                R = np.zeros((4,4))
                R[0][2] = normal__[0]
                R[1][2] = normal__[1]
                R[2][2] = normal__[2]

                R[0][1] = normal[0]
                R[1][1] = normal[1]
                R[2][1] = normal[2]

                R[0][0] = normal_[0]
                R[1][0] = normal_[1]
                R[2][0] = normal_[2]

                R[3][3] = 1

                # also only rotate if you have a proper rotation matrix
                # use epsilon = 0.0000001 for precision issues
                if (abs(np.linalg.det(R)-1) < 0.0000001):
                    glMultMatrixf(np.transpose(R))

            # magic numbers in scale: 
            # do terrain scaling
            # 1/13 for a good-looking tile size
            glScalef(xz_scale*tile_scale, tile_scale, xz_scale*tile_scale)

            glutSolidCube(1);
            
            glPopMatrix()

        
        for counter, scene in enumerate(self.subscene_list):
            glPushMatrix()
            pos = scene['pos']
            # choose the tree's x-location as 1/4, 2/4, 3/4 of the samples
            x_idx = (counter+1)*len(X)/4
            # choose the z-location to be at 1/3 of the samples always
            z_idx = len(X[0])/3
            # multiplying x and z positions by 5 to match terrain scaling
            glTranslate(pos[0]+5*X[x_idx][z_idx], pos[1]+Y[x_idx][z_idx], pos[2]+5*Z[x_idx][z_idx])
            scene['model'].draw_scene()
            glPopMatrix()
        #------------- END SOLUTION ----------------
            

def main():
    from OpenGL.GLUT import glutInit, glutInitDisplayMode, GLUT_DOUBLE, GLUT_RGBA
    from ModelViewWindow import GLUTWindow, View
    
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    #TODO -------- COPY CODE FROM LSystem.py ----------
    ''' Replace the following L-system speicfication with the one you did
    in LSystem.py '''
    # L-system specification
    Tree1 = {'init' : 'X',
                'rule' : 'X->F[+yX][++PX][-YX]FX;F->FF', # modified from Algorithmic Botany, p.25
                'depth' : 7, 'angle': 25.7, 'growth_factor': .53, 'XZScale': 2,
                'init_angle_axis': {'angle':90, 'axis':[0, 0, 1]},
                } 

    Tree2 = {'init' : 'X',
                'rule' : 'X->wFL[RX][rX[pX]X]X[YX][yX];F->FWF', # adapted from Algorithmic Botany, p.24 + Tree3D
                'depth' : 4, 'angle': 22.5, 'growth_factor': .6,
                'init_angle_axis': {'angle':90, 'axis': [0, 0, 1]},
                }

    Tree3 = {'init' : 'X',
                        'rule' : 'X->BLr[[XL]RyXXL]pBL[PBX]YXL;B->BB', # adapted from Algorithmic Botany, p.25
                        'depth': 4, 'angle': 22.5, 'growth_factor': .55,
                        'init_angle_axis':{'angle':90, 'axis':[0, 0, 1]},
                        }

    '''
    ModelList is a convenient way to add all the models with their position
    in a python list of dictionaries which can be used by the GardenScene class.
    NOTE that using this is optional. If you want you can add all the transformation
    code in GardenScene.draw_scene() 
    '''
    ModelList = [{'pos':[0, 0, 0], 'model': LSystem(Tree1)},
                {'pos': [0, 0, 0], 'model': LSystem(Tree2)},
                {'pos': [0, 0, 0], 'model' :LSystem(Tree3)}
                ]
    #--------------------------------------------------
                
    #TODO ---------------- BEGIN SOLUTION ----------------- 

    '''
    Represent the terrain using a Bicubic patch. Replace the
    control points below with the control points for your terrain.
    '''
    control_points = np.zeros((16, 3))
    # uniform grid with different ranges, as asked
    # note grid is on xz plane, and y gets height values
    control_points[:,0] = np.transpose([0, 0, 0, 0,  2, 2, 2, 2,  4, 4, 4, 4,  6, 6, 6, 6])
    control_points[:,2] = np.transpose([1, 2, 4, 6,  0, 2, 4, 6,  0, 2, 4, 6,  0, 2, 4, 6])
    control_points[:,1] = np.transpose([-1, 0, 2, 1,  1, 1, 0, 0, 0, 2, 3, 1, -1, 0, 1, -1]) 
    BCPatch = BicubicPatch(control_points)
    # ------------ END SOLUTION ------------------------
    # main camera
    cam_spec = {'eye' : [0, 4.5, 4], 'center' : [0, 2, 0], 'up' : [0, 1, 0], 
                 'fovy': 40, 'aspect': 1.0, 'near' : 0.1, 'far' : 100.0}
    
    cam = FlythroughCamera(GardenScene(BCPatch, ModelList), 
                           cam_spec, HermiteCurve())
    GLUTWindow('Garden Scene', cam, window_size = (640 * 1.2, 480), window_pos = (320, 0))
    
    # external camera
    cam_spec2 = {'eye' : [5, 5, 5], 'center' : [0, 1, 0], 'up' : [0, 1, 0], 
                 'fovy': 60, 'aspect': 1.0, 'near' : 0.1, 'far' : 200.0}
    external_cam = View(cam, cam_spec2)
    GLUTWindow("External Camera View", external_cam, window_size = (640 * 1.2, 480), window_pos = (320, 520))
    
    glutMainLoop()
        
if __name__ == '__main__':
    main()
