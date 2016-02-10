# -*- coding: utf-8 -*-
"""
BicubicPatch.py
---------------
This file implements the BicubicPatch class. Code needs to be added in 
evaluate(st_param): returns a list of point and tangent values for a given 
                    parameter [s, t]

"""
from __future__ import division
import numpy as np
from ModelViewWindow import Model
from OpenGL.GL import *
from GLDrawHelper import *

class BicubicPatch(Model):
    '''
    Bicubic surface patch defined by 16 points. The 16 points on a 4x4 (s, t) 
    grid is provided during instantiation. 
    '''
    def __init__(self, data_points, num_samples_rendering = (34, 34)):
        '''
        data_points is in row major order, namely the 16 rows of the array
        correspond to (s,t) values (0,0), (0,1),(0,2), (0,3), (1, 0), (1,1),...
        and so on.
        num_samples_rendering refers to the number of samples that would be used
        by the draw_scene() function when rendering the patch
        '''
        Model.__init__(self)
        self.data_points = data_points
        self.num_samples_rendering = num_samples_rendering
        
        self.B = np.linalg.inv( [ [0, 1, 8, 27], [0, 1, 4, 9], [0, 1, 2, 3], [1, 1, 1, 1]])
        self.MatX = np.dot( np.transpose(self.B), np.dot( np.reshape(data_points[:,0], (4,4)), self.B ))
        self.MatY = np.dot( np.transpose(self.B), np.dot( np.reshape(data_points[:,1], (4,4)), self.B ))
        self.MatZ = np.dot( np.transpose(self.B), np.dot( np.reshape(data_points[:,2], (4,4)), self.B )) 
        
    def evaluate(self, st_param):
        '''
        st_param = [s, t] where
        s in [0, 3] and t in [0, 3]
        For a given set of parameters return 
        [x(s,t), y(s,t), z(s,t), 
        dsx(s,t), dsy(s,t), dsz(s,t), 
        dtx(s,t), dty(s,t), dtz(s,t)]
        '''
        s = st_param[0]
        t = st_param[1]
        assert(0. <= s <= 3. and 0. <= t <= 3.)
        x = y = z = dsx = dsy = dsz = dtx = dty = dtz = 0.
        #TODO ---------   BEGIN SOLUTION --------

        # first solve for (x, y, z)
        x = np.dot(np.dot([s**3, s**2, s, 1], self.MatX), [t**3, t**2, t, 1])
        y = np.dot(np.dot([s**3, s**2, s, 1], self.MatY), [t**3, t**2, t, 1])
        z = np.dot(np.dot([s**3, s**2, s, 1], self.MatZ), [t**3, t**2, t, 1])

        # now for (dsx, dsy, dsz)
        dsx = np.dot(np.dot([3*s**2, 2*s, 1, 0], self.MatX), [t**3, t**2, t, 1])
        dsy = np.dot(np.dot([3*s**2, 2*s, 1, 0], self.MatY), [t**3, t**2, t, 1])
        dsz = np.dot(np.dot([3*s**2, 2*s, 1, 0], self.MatZ), [t**3, t**2, t, 1])

        # and finally for (dtx, dty, dtz)
        dtx = np.dot(np.dot([s**3, s**2, s, 1], self.MatX), [3*t**2, 2*t, 1, 0])
        dty = np.dot(np.dot([s**3, s**2, s, 1], self.MatY), [3*t**2, 2*t, 1, 0])
        dtz = np.dot(np.dot([s**3, s**2, s, 1], self.MatZ), [3*t**2, 2*t, 1, 0])

        #-------------- END SOLUTION -------------
        return [x, y, z, dsx, dsy, dsz, dtx, dty, dtz]
    
    def get_samples(self, samples = (7, 7)):
        '''
        Returns an array of values. samples is a tuple that has to be at least (2, 2)
        '''
        assert(samples[0] >= 2 and samples[1] >= 2)
        X = np.zeros(samples)
        Y = np.zeros(samples)
        Z = np.zeros(samples)
        DsX = np.zeros(samples)
        DsY = np.zeros(samples)
        DsZ = np.zeros(samples)
        DtX = np.zeros(samples)
        DtY = np.zeros(samples)
        DtZ = np.zeros(samples)
        
        for i in range(samples[0]):
            for j in range(samples[1]):
                p = self.evaluate([3.*i/(samples[0] - 1.), 3.*j/(samples[1] - 1.)])
                X[i][j] = p[0]
                Y[i][j] = p[1]
                Z[i][j] = p[2]
                DsX[i][j] = p[3]
                DsY[i][j] = p[4]
                DsZ[i][j] = p[5]
                DtX[i][j] = p[6]
                DtY[i][j] = p[7]
                DtZ[i][j] = p[8]
                
        return (X, Y, Z, DsX, DsY, DsZ, DtX, DtY, DtZ)

    def set_color_from_XYZ(self, x, y, z):
        '''
        set_color_from_XYZ is the default color scheme for rendering
        bicubic patches. It takes  x, y, z values that are in [0, 1] and sets
        the color based on the normalized XYZ coordinate 
        '''
        assert(0. <= x <= 1. and 0. <= y <= 1. and 0. <= z <= 1.)
        
        #TODO ------- BEGIN SOLUTION ----------

        # dark green near 0, light green near 1
        glColor3f(0, y, 0)
        
        #---------- END SOLUTION --------------
        
    def draw_scene(self, bDrawCoordAxes = True):
        '''
        drawing meshes with normalized values is more generic because the caller
        can then approrpriately scale and translate the mesh.
        '''
        result = self.get_samples(self.num_samples_rendering)
        
        # The following draw3DCoordinateAxesQuadrics can be commented out
        # if bDrawCoordAxes is True:
        #     glPushMatrix()
        #     glScalef(.25, .25, .25)
        #     draw3DCoordinateAxesQuadrics()
        #     glPopMatrix()
        
        #TODO ---------   BEGIN SOLUTION --------

        # normalise the points by finding max and min values in each axis
        x_min = y_min = z_min = np.inf
        x_max = y_max = z_max = -np.inf
        for i in range(len(result[0])):
            for j in range(len(result[0][0])):
                if (result[0][i][j] < x_min):
                    x_min = result[0][i][j]
                elif (result[0][i][j] > x_max):
                    x_max = result[0][i][j]
                if (result[1][i][j] < y_min):
                    y_min = result[1][i][j]
                elif (result[1][i][j] > y_max):
                    y_max = result[1][i][j]
                if (result[2][i][j] < z_min):
                    z_min = result[2][i][j]
                elif (result[2][i][j] > z_max):
                    z_max = result[2][i][j]
        # now normalize the points
        x_normal = np.zeros((len(result[0]), len(result[0][0])))
        y_normal = np.zeros((len(result[0]), len(result[0][0])))
        z_normal = np.zeros((len(result[0]), len(result[0][0])))
        dsx_normal = np.zeros((len(result[0]), len(result[0][0])))
        dsy_normal = np.zeros((len(result[0]), len(result[0][0])))
        dsz_normal = np.zeros((len(result[0]), len(result[0][0])))
        dtx_normal = np.zeros((len(result[0]), len(result[0][0])))
        dty_normal = np.zeros((len(result[0]), len(result[0][0])))
        dtz_normal = np.zeros((len(result[0]), len(result[0][0])))
        for i in range(len(result[0])):
            for j in range(len(result[0][0])):
                x_normal[i][j] = (result[0][i][j]-x_min)/(x_max - x_min)-0.5
                dsx_normal[i][j] = result[3][i][j] / (x_max - x_min)
                dtx_normal[i][j] = result[6][i][j] / (x_max - x_min)
                y_normal[i][j] = (result[1][i][j]-y_min)/(y_max - y_min)-0.5
                dsy_normal[i][j] = result[4][i][j] / (y_max - y_min)
                dty_normal[i][j] = result[7][i][j] / (y_max - y_min)
                z_normal[i][j] = (result[2][i][j]-z_min)/(z_max - z_min)-0.5
                dsz_normal[i][j] = result[5][i][j] / (z_max - z_min)
                dtz_normal[i][j] = result[8][i][j] / (z_max - z_min)
        # change result too, so that the returned values fit what gets drawn
        normalized_result = [x_normal, y_normal, z_normal] 
        result = [x_normal, y_normal, z_normal, dsx_normal, dsy_normal, dsz_normal, dtx_normal, dty_normal, dtz_normal]

        # iterate over samples in result (make 2 triangles for every 4)
        # build triangles 
        glColor3f(1.0, 1.0, 1.0)
        glDisable(GL_CULL_FACE)
        for i in range(len(result[0])-1):
            for j in range(len(result[0][0])-1):
                glBegin(GL_TRIANGLES)

                # note that I add 0.5 to colour coordinates because the patch is centered at the origin in range [-0.5, 0.5]
                # i.e. to ensure coordinates match to [0, 1]
                self.set_color_from_XYZ(normalized_result[0][i][j]+0.5, normalized_result[1][i][j]+0.5, normalized_result[2][i][j]+0.5)
                glVertex(normalized_result[0][i][j], normalized_result[1][i][j], normalized_result[2][i][j])

                self.set_color_from_XYZ(normalized_result[0][i][j+1]+0.5, normalized_result[1][i][j+1]+0.5, normalized_result[2][i][j+1]+0.5)
                glVertex(normalized_result[0][i][j+1], normalized_result[1][i][j+1], normalized_result[2][i][j+1])

                self.set_color_from_XYZ(normalized_result[0][i+1][j]+0.5, normalized_result[1][i+1][j]+0.5, normalized_result[2][i+1][j]+0.5)
                glVertex(normalized_result[0][i+1][j], normalized_result[1][i+1][j], normalized_result[2][i+1][j])
                
                

                self.set_color_from_XYZ(normalized_result[0][i][j+1]+0.5, normalized_result[1][i][j+1]+0.5, normalized_result[2][i][j+1]+0.5)
                glVertex(normalized_result[0][i][j+1], normalized_result[1][i][j+1], normalized_result[2][i][j+1])

                
                self.set_color_from_XYZ(normalized_result[0][i+1][j+1]+0.5, normalized_result[1][i+1][j+1]+0.5, normalized_result[2][i+1][j+1]+0.5)
                glVertex(normalized_result[0][i+1][j+1], normalized_result[1][i+1][j+1], normalized_result[2][i+1][j+1])

                self.set_color_from_XYZ(normalized_result[0][i+1][j]+0.5, normalized_result[1][i+1][j]+0.5, normalized_result[2][i+1][j]+0.5)
                glVertex(normalized_result[0][i+1][j], normalized_result[1][i+1][j], normalized_result[2][i+1][j])

                glEnd()   
        glEnable(GL_CULL_FACE)
        glColor3f(1.0, 1.0, 1.0)
        #-------------- END SOLUTION -------------
        ''' return the result obtained from get_samples so it can be used for
        further processing by the caller if necessary'''
        return result

#### ----- Code for rendering a sample Bicubic Patch ------
def main():
    from OpenGL.GLUT import glutInit, glutInitDisplayMode,  \
                            glutMainLoop, GLUT_DOUBLE, GLUT_RGBA
    
    from ModelViewWindow import View, GLUTWindow
    
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    
    cam_spec = {'eye' : [2, 2, 2], 'center' : [0, 0, 0], 'up' : [0, 1, 0], 
                 'fovy': 30, 'aspect': 1.0, 'near' : 0.01, 'far' : 200.0}
    data_points = np.zeros((16, 3))
    data_points[:,0] = np.transpose([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3])
    data_points[:,1] = np.transpose([0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3])
    data_points[:,2] = np.transpose([0, -2, 2, -3, 0, -2, 2, -3, 0, -2, 2, -3, 0, -2, 2, -3]) 
    
    BCPatch = BicubicPatch(data_points)
    cam = View(BCPatch, cam_spec)    
    GLUTWindow('Bicubic Patch', cam, window_size = (512, 512), window_pos =(520, 0))
    
    glutMainLoop()
        
if __name__ == '__main__':
    main()

    
    