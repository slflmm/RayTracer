'''
This file contains the Scene class which has the renderScene() method that
needs to be implemented for the assignment. Look for the tags 
#------ Implement <method-name> 
to find the location where you need to add code.

This file also contains a basic scene at the end of the file which gets 
rendered whenever this file is executed. When starting out you'd find it useful
to simply execute this file. Once you're ready to try other scenes that are in
the ./scenes/ folder you should use A3App.py (see the comments in that file).
'''

from __future__ import division
from Ray import Ray, IntersectionResult
from HelperClasses import Camera, Render, Light, Material
import GeomTransform as GT

import math
import numpy as np


class Scene:
  """
    
  The scene class contains the renderer, the list of lights, the list of intersectable
  surfaces and a value for the ambient light.
  
  The renderScene() method is called by the main() function after the scene has been
  properly initialized.
  
  """
    
  def __init__(self, render = Render()):
    self.render = render # The camera will be set by the parser.
    self.lights = [] #empty lists of lights, needs to be populated by the parser.
    self.surfaces = [] #empty list of surfaces, needs to be populated by the parser.
    self.ambient = np.array([0.1, 0.1, 0.1]) # scene ambient value can be overridden by the xml file spec
  
  def set_params(self, params):
      self.ambient = np.array(params.get('ambient', self.ambient))
      # force scene ambient to have 3 values (some xmls have 4)
      self.ambient = self.ambient[:3]
      
#----- Implement create_ray
  def create_ray(self,row,col):
      ''' 
      Create ray (i.e. origin and direction) from a pixel specified by (row, col).
      The ray originates at the camera's eye and goes through the point in space
      that corresponds to the image pixel coordinate (row, col). Take a look at
      the Camera class to see the variables that can be used here.
      '''
      ray = Ray() # construct an empty ray
      '''
      The ray origin is set in this starter code. You need to compute and set
      the ray.viewDirection variable inside the solution block below.
      Note: GeomTransform.py implements a function called normalize for 
      normalizing vectors (with appropriate check for division by zero). 
      For a vector v, you can get the normalized vector as:
      normalized_v = GT.normalize(v)
      '''
      cam = self.render.camera # use a local variable to save some typing
      ray.eyePoint = cam.pointFrom # origin of the ray

      #TODO ====== BEGIN SOLUTION ======

      # get the camera coordinates
      cam_x = col*(cam.right-cam.left)/cam.imageWidth + cam.left
      cam_y = row*-(cam.top-cam.bottom)/cam.imageHeight + cam.top
      cam_z = cam.near

      xa = cam.cameraXAxis
      ya = cam.cameraYAxis
      za = cam.cameraZAxis
      R = [ [xa[0], ya[0], za[0], 0],
            [xa[1], ya[1], za[1], 0],
            [xa[2], ya[2], za[2], 0],
            [0, 0, 0, 1] ]
      T = [ [1, 0, 0, -cam.pointFrom[0]], 
            [0, 1, 0, -cam.pointFrom[1]],
            [0, 0, 1, -cam.pointFrom[2]],
            [0, 0, 0, 1] ]

      cam_to_world = np.linalg.inv(np.dot(np.transpose(R),T))

      world_pixels = np.dot( cam_to_world, [cam_x, cam_y, cam_z, 1] )
      #world_pixels = world_pixels/world_pixels[3]
      ray.viewDirection = GT.normalize(world_pixels[0:3] - ray.eyePoint)

      # ===== END SOLUTION =====
      return ray    

#----- Implement blinn_phong_shading      
  def blinn_phong_shading_per_light(self,viewer_direction,light,isect):
      '''
      Compute the color of the pixel for the given light source, viewer direction
      and intersection point.
      viewer_direction: a numpy array of size 3 containing the direction of the viewer
      light: is of type Light which should be used for shading
      isect: is of type IntersectionResult that contains the intersection point,
             normal and material.
      '''
      
      # Compute the color only for this instance. The caller is responsible for
      # mixing colors for different lights.
      color = np.array([0., 0., 0.])
      #TODO ====== BEGIN SOLUTION =====

      # some important bits
      l = GT.normalize(light.pointFrom - isect.p)
      v = viewer_direction
      H =  GT.normalize(l + v)

      # calculate the diffuse component
      I_diffuse = np.multiply(light.color*light.power, isect.material.diffuse) * max(np.dot(isect.n, l), 0)

      # and get the specular component
      I_specular = np.multiply(light.color*light.power, isect.material.specular) * np.dot(H, isect.n)**isect.material.hardness

      color = I_diffuse + I_specular

      # ===== END SOLUTION HERE =====
      return color

#----- Implement get_nearest_object_intersection
  def get_nearest_object_intersection(self,ray):
      ''' 
      Find the nearest object that the ray intersects and return the result of
      the intersection. Scene.surfaces contain a list of surfaces. A surface
      can be any of the type specified in Intersectable.py. More specifically
      they are Sphere, Plane, Box, and SceneNode.
      The result of the intersection should be returned in a variable of type
      IntersectionResult() which is defined in Ray.py file. IntersectionResult
      contains the point of intersection (p), the surface normal (n) at the 
      intersection point, material at the intersection point (material) and 
      distance (t) of the intersection point from the ray origin (i.e. ray.eyePoint)
      '''
      # Here we initialize the variable that should be computed and returned
      # Note that by default nearest_intersection.t = inf which corresponds to no intersection
      nearest_intersection = IntersectionResult() 
      #TODO ======= BEGIN SOLUTION =========

      # loop through intersectable objects in the scene
      # do the ray, get the t
      # if t is smaller, nearest_intersection is that one
      for surface in self.surfaces:
        r = surface.intersect(ray)
        # print r.t
        if r.t < nearest_intersection.t:
          nearest_intersection = r
        

      #======= END SOLUTION ========
      #at this point nearest_intersection should contain 
      #the updated values corresponding to the nearest intersection point.
      #If there was no intersection then it should have the same initial values.
      return nearest_intersection 

#----- Implement get_visible_lights  
  def get_visible_lights(self, isect):
      ''' 
      isect is variable of type IntersectionResult. isect.p contains the 
      intersection point. This function should return a python list containing
      all the lights that are "visible" from isect.p position. A light source
      is visible if there are no objects between the point and the light source.
      All light sources are of type Light (Light class is defined in HelperClasses.py).
      The light sources in the scene is stored in the variable Scene.lights
      (accessed using self.lights). Your returned list should be a subset
      of self.lights
      '''
     
      #you need to loop over the lights and return those that are visible from the position in result
      visibleLights = []
      #TODO ====== BEGIN SOLUTION =====

      # loop over self.lights, build a ray from isect.p to the light's location
      # and then check that get_nearest_object_intersection with that ray is the light
      for light in self.lights:
        ray = Ray(isect.p, GT.normalize(light.pointFrom - isect.p))
        nearest_isect = self.get_nearest_object_intersection(ray)
        # find time of intersection with the light
        # note that p_intersect = ray_start + t*ray_dir
        # so t = (p_intersect - ray_start)/ray_dir
        if (ray.viewDirection[0] != 0):
          light_t = (light.pointFrom[0] - isect.p[0])/ray.viewDirection[0] 
        elif (ray.viewDirection[1] != 0):
          light_t = (light.pointFrom[1] - isect.p[1])/ray.viewDirection[1]
        else:
          light_t = (light.pointFrom[2] - isect.p[2])/ray.viewDirection[2]  
        # consider the light if it is closer than the first object you hit
        if light_t <= nearest_isect.t:
          visibleLights.append(light)

      # ===== END SOLUTION HERE =====
      return visibleLights

  def renderScene(self):
    """
    
    The method renderScene is called once to draw all the pixels of the scene.  For each
    pixel, a ray is cast from the eye position through the location of the pixel on the
    near plane of the frustrum. The closest intersection is then computed by intersecting
    the ray with all the objects of the scene.  From that intersection point, rays are
    casted towards all the lights of the scene.  Based on if the point is exposed to the
    light, the shadow and the diffuse and specular lighting contributions can be computed
    and summed up for all lights.
    
    """
    
    # Initialize the renderer.
    self.render.init(self.render.camera.imageWidth, self.render.camera.imageHeight)
    
    for pixel in self.render.getPixel():
        '''
        pixel is a list containing the image coordinate of a pixel i.e. 
        pixel = [col, row] 
        '''
       
        # create a ray from the eye position and goes through the pixel
        ray = self.create_ray(pixel[1], pixel[0])
        
        # set the default color to the background color
        color = self.render.bgcolor
        
        nearest_isect = self.get_nearest_object_intersection(ray)

        if nearest_isect.is_valid_intersection(): # valid intersection
            color = self.ambient[:3] * nearest_isect.material.ambient[:3] # ambient color is used when the point is in shadow
            # get a list of light sources that are visible from the nearest intersection point
            visible_lights = self.get_visible_lights(nearest_isect)
            nearest_isect.n = GT.normalize(nearest_isect.n) # ensure that the returned normals are normalized
            if len(visible_lights) > 0: # light-shadow
                '''
                Compute the color based on the material found in nearest_isect.material
                and the light sources visible from nearest_isect.p position.
                '''
                for light in visible_lights:
                    color += self.blinn_phong_shading_per_light(-ray.viewDirection, light, nearest_isect)
        
        #At this point color should be a floating-point numpy array of 3 elements
        #and is the final color of the pixel.
        self.render.setPixel(pixel, color)
        
    self.render.save()  

#############################################################################
'''
When you're getting started with implementing the main loop you might find
it easier to just execute this file which will render scene provided in
test_red_sphere_blue_background(). The expected results during the initial
steps can be found in ./images_sol/test_image_getting_started/ folder.
Also see the README file.
'''
def test_red_sphere_blue_background():
    from Intersectable import Sphere
    
    scene = Scene()
    
    #Materials
    red = Material()
    
    #Lights
    light = Light({'color':[0.8, 0.2, 0.2], 'from':[0, 0, 10], 'power':0.6})
    scene.lights.append(light)
  
    #Surfaces
    sphere = Sphere({'radius':1, 'center':[0, 0, 0], 'material':red})
    scene.surfaces.append(sphere)
  
    #Camera
    camera = Camera({'from':[0,0,4], 'to':[0,0,0], 'up':[0,1,0], 'fov':45, 'width':160, 'height':120})
    render = Render({'camera':camera, 'bgcolor': [.2, .2, .8], 'output':'red_sphere_blue_background.png'})
    scene.render = render
    scene.renderScene()

if __name__ == '__main__':
    test_red_sphere_blue_background()
    