# -*- coding: utf-8 -*-
"""
LSystem.py
"""
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

class LSystem(Model):
    '''
    The main part of the LSystem is in set_grammar. The rule set contains
    initial symbol and the production rules separated semi-colon.

    set_grammar(): Interprets the L-system rules and performs parallel rewrite.
                    The end result is a string containing a sequence of draw commands.
    draw_scene() : Walks through the production string and executes draw commands. 
            This is also a function for any Scene class. 
    exec_draw_cmd(): OGL drawing routine for each command.
    '''
    def __init__(self, grammar_str, bVerbose = False):
        Model.__init__(self)
        self.bVerbose = bVerbose      # used for tracing. True: prints output
        self.set_grammar(grammar_str) # set the string and extract the ruleset
        self.pQuadric = None
        
    def get_grammar(self):
        return self.grammar_str
    
    def set_grammar(self, gstr):
        '''
        Expand the production using the provided rule set. The non-terminals
        are expanded in parallel (i.e. the previous production is traversed sequentially
        and if a non-terminal is found it's expanded and written to a new string
        otherwise the terminal symbol is just copied to the new string).
        '''
        self.grammar_str = gstr
        self.depth = self.grammar_str['depth']
        self.angle = gstr.get('angle', 0)
        self.growth_factor = gstr.get('growth_factor', 0.5)
        self.init_angle_axis = gstr.get('init_angle_axis')
        self.init_translate = gstr.get('init_translate')
        self.XZScale = gstr.get('XZScale', 1)
        self.YScale = gstr.get('YScale', 1)
        
        # extract rule set
        rule_list = gstr['rule'].split(';')
        prod = dict()
        for rule in rule_list:
            rule_parts = rule.split('->')
            prod[rule_parts[0]] = rule_parts[1]
    
        self.prod_rules = prod
        
        # expand rules
        production = self.grammar_str['init']
        if self.bVerbose: print(0, production)
        for n in range(self.depth):
            newProd = ''
            for char in production:
                if(prod.has_key(char)):
                    newProd += prod[char]
                else:
                    newProd += char
            production = newProd
            if self.bVerbose: print(n+1, production)
        self.production = production    
        if self.bVerbose: print('set_grammar', self.prod_rules, self.production)
        
    grammar = property(get_grammar, set_grammar)
    
    def exec_draw_cmd(self, cmd):
        '''
        Implement the draw commands.
        '''
        if cmd == 'F':
            glBegin(GL_LINES)
            glVertex3f(0., 0., 0.)
            glVertex3f(1., 0., 0.)
            glEnd()
            glTranslatef(1, 0, 0)
        elif cmd == 'f':
            glTranslatef(1, 0, 0)
        #TODO ----------- BEGIN SOLUTION ---------------
        elif cmd == 'L':
            glBegin(GL_QUADS)            
            glColor3f(0.0,  1.0, 0.0) # green
            glVertex3f(0.1,0.1,-0.1)
            glVertex3f(0.1,0.1,0.1)
            glVertex3f(-0.1,0.1,0.1)
            glVertex3f(-0.1,0.1,-0.1)
            glColor3f(1.0, 1.0, 1.0)
            glEnd()
        elif cmd == 'B':
            glColor3f(0.545,0.271,0.075) # brown
            glPushMatrix()
            glRotatef(90, 0, 1.0, 0)
            self.pQuadric = gluNewQuadric()
            gluCylinder(self.pQuadric,0.1,0.1,1.0,32,32)
            glPopMatrix()
            glTranslatef(1, 0, 0)
            glColor3f(1.0, 1.0, 1.0)
        elif cmd == 'W':
            glScalef(self.XZScale, 1, self.XZScale)
        elif cmd == 'w':
            glScalef(1.0/self.XZScale, 1, 1.0/self.XZScale)
        elif cmd == 'S':
            glScalef(1, self.YScale, 1)
        elif cmd == 's':
            glScaef(1, 1.0/self.YScale, 1)
        elif cmd == 'P':
            glRotatef(self.angle, 1, 0, 0)
        elif cmd == 'p':
            glRotatef(-self.angle, 1, 0, 0)
        elif cmd == 'Y':
            glRotatef(self.angle, 0, 1, 0)
        elif cmd == 'y':
            glRotatef(-self.angle, 0, 1, 0)
        elif cmd == 'R' or cmd == '+': 
            glRotatef(self.angle, 0, 0, 1)
        elif cmd == 'r' or cmd == '-':
            glRotatef(-self.angle, 0, 0, 1)
        elif cmd == '[':
            glPushMatrix()
        elif cmd == ']':
            glPopMatrix()
        else:
            pass
        #-------- END SOLUTION -------------
        
    def draw_scene(self):
        '''
        Go over the production string and draw the scene
        '''
        glPushMatrix()
        
        if self.init_translate is not None:
            glTranslatef(self.init_translate[0], self.init_translate[1], self.init_translate[2])
        
        if self.init_angle_axis is not None:
            axis = self.init_angle_axis['axis']
            glRotatef(self.init_angle_axis['angle'], axis[0], axis[1], axis[2])

        scale_factor = pow(self.growth_factor, self.depth)
        glScalef(scale_factor, scale_factor, scale_factor)

        for cmd in self.production:
            self.exec_draw_cmd(cmd)
        glPopMatrix()


# ----------- The following is only for rendering L-systems -----------
class LSystem3DScene(Model):
    '''
    Scene with multiple 3D L-System and a checkerboard as ground-plane
    subscene_list is a list of dictionaries that contains the (x, y) position 
    on the ground plane and the L-system.
    '''
    def __init__(self, subscene_list = []):
        Model.__init__(self)
        self.subscene_list = subscene_list
    
    def add_subscene(self, subscene):
        self.subscene_list.append(subscene)
        
    def draw_scene(self):
        glPushMatrix()
        draw3DCoordinateAxes()
        glPopMatrix()
        
        glPushMatrix()
        glRotate(-90, 1, 0, 0)
        drawCheckerBoard(scale = [8, 8], 
                         check_colors = [[0.8, 0.8, 0.8], [0.2, 0.2, 0.2]])
        glPopMatrix()
        
        for scene in self.subscene_list:
            glPushMatrix()
            pos = scene['pos']
            glTranslate(pos[0], pos[1], pos[2])
            scene['model'].draw_scene()
            glPopMatrix()
            

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)

    #TODO ---------- BEGIN SOLUTION -------------

    '''
    Add your own L-system specification here by replacing the following 
    sample specification. You can use the provided code for LSystem3DScene
    for visualizing your own trees. Be sure to copy your L-system specification
    to GardenScene.py main() function for rendering your L-systems for Q5.
    '''    

    # L-system specification
    '''Note that these specifications are plain python dictionary. The objects
    are created with expression LSystem(specification) '''
    # Tree2D = {'init': 'F', 
    #           'rule' : 'F->FF-[-F+F+F]+[+F-F-F]', 
    #           'depth': 3, 'angle': 22.5, 'growth_factor': .5,
    #           'init_angle_axis': {'angle': 90, 'axis':[0, 0, 1]},
    #           }
    
    # Tree3D = {'init' : 'X',
    #            'rule' : 'X->wFL[[RX][PX][YX]]F[[rX][pX][yX]]RLrLPLpLYLyLX;F->FWF',
    #            'depth': 3, 'angle': 20, 'growth_factor': .6,
    #            'init_angle_axis':{'angle':90, 'axis': [0, 0, 1]},
    #           }

    # Tree3DBranchAndLeaves = {'init' : 'X',
    #                  'rule' : 'X->BB;B->BBr[LrBRBRBL]LR[LRBrBrBL]LrrLYY[LRBrBrBL]LyPPL[LRBrBrBL]',
    #                  'depth': 2, 'angle': 22.5, 'growth_factor': .8,
    #                  'init_angle_axis':{'angle':90, 'axis': [0, 0, 1]},
    #                 }

    Tree2D = {'init' : 'X',
                'rule' : 'X->F[+yX][++PX][-YX]FX;F->FF', # modified from Algorithmic Botany, p.25
                'depth' : 7, 'angle': 25.7, 'growth_factor': .53, 'XZScale': 2,
                'init_angle_axis': {'angle':90, 'axis':[0, 0, 1]},
                } 

    Tree3D = {'init' : 'X',
                'rule' : 'X->wFL[RX][rX[pX]X]X[YX][yX];F->FWF', # adapted from Algorithmic Botany, p.24 + Tree3D
                'depth' : 4, 'angle': 22.5, 'growth_factor': .6,
                'init_angle_axis': {'angle':90, 'axis': [0, 0, 1]},
                }

    Tree3DBranchAndLeaves = {'init' : 'X',
                        'rule' : 'X->BLr[[XL]RyXXL]pBL[PBX]YXL;B->BB', # adapted from Algorithmic Botany, p.25
                        'depth': 4, 'angle': 22.5, 'growth_factor': .55,
                        'init_angle_axis':{'angle':90, 'axis':[0, 0, 1]},
                        }

    #----------- END SOLUTION -------------
    ''' 
    The following list of dictionaries is used by LSystem3DScene to position
    an L-system and render it.
    '''
    ModelList = [{'pos':[0, 0, 0], 'model': LSystem(Tree2D)},
                 {'pos':[-1, 0, 1], 'model': LSystem(Tree3D)}, # I moved this one because it was in front of Tree2D
                 {'pos':[1, 0, -1], 'model': LSystem(Tree3DBranchAndLeaves)}
                ]
    '''
    cam_spec provides the camera specification for the View class.
    '''
    cam_spec = {'eye' : [4, 4, 4], 'center' : [0, 0, 0], 'up' : [0, 1, 0], 
                 'fovy': 60, 'aspect': 1.0, 'near' : 0.01, 'far' : 200.0}

    cam = View(LSystem3DScene(ModelList), cam_spec)
    GLUTWindow('3D plants', cam, window_size = (512, 512), window_pos = (0, 0))
    
    glutMainLoop()
        
if __name__ == '__main__':
    main()
    