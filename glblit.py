import pygame
import os

from OpenGL.GL import *
from OpenGL.GLU import *


def initializeDisplay(w, h):
    screen = pygame.display.set_mode((w,h), pygame.OPENGL | pygame.DOUBLEBUF)
    # pygame.HWSURFACE | pygame.FULLSCREEN

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity();
    # this puts us in quadrant 1, rather than quadrant 4
    gluOrtho2D(0, w, h, 0)
    glMatrixMode(GL_MODELVIEW)

    # set up texturing
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    return screen


def loadImage(image):
    textureSurface = pygame.image.load(image)

    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)

    width = textureSurface.get_width()
    height = textureSurface.get_height()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
        GL_UNSIGNED_BYTE, textureData)

    return texture, width, height


def SurfaceClip(surface, rect):
    textureSurface = surface.subsurface(rect)

    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)

    width = textureSurface.get_width()
    height = textureSurface.get_height()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
        GL_UNSIGNED_BYTE, textureData)

    return texture, width, height


def delTexture(texture):
    glDeleteTextures(texture)


def createTexDL(texture, width, height):
    newList = glGenLists(1)
    glNewList(newList,GL_COMPILE);
    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)

    # Bottom Left Of The Texture and Quad
    glTexCoord2f(0, 0); glVertex2f(0, 0)

    # Top Left Of The Texture and Quad
    glTexCoord2f(0, 1); glVertex2f(0, height)

    # Top Right Of The Texture and Quad
    glTexCoord2f(1, 1); glVertex2f( width,  height)

    # Bottom Right Of The Texture and Quad
    glTexCoord2f(1, 0); glVertex2f(width, 0)
    glEnd()
    glEndList()

    return newList


def delDL(list):
    glDeleteLists(list, 1)


class GL_Texture:
    def __init__(s, texname=None, texappend=".png"):
        filename = os.path.join('data', texname)
        filename += texappend

        s.texture, s.width, s.height = loadImage(filename)
        s.displaylist = createTexDL(s.texture, s.width, s.height)

    def __del__(self):
        if self.texture != None:
            delTexture(self.texture)
            self.texture = None
        if self.displaylist != None:
            delDL(self.displaylist)
            self.displaylist = None

    def __repr__(s):
        return s.texture.__repr__()


class Surface_Texture:
    def __init__(s, surface, rect):
        s.texture, s.width, s.height = SurfaceClip(surface, rect)
        s.displaylist = createTexDL(s.texture, s.width, s.height)

    def __del__(self):
        if self.texture != None:
            delTexture(self.texture)
            self.texture = None
        if self.displaylist != None:
            delDL(self.displaylist)
            self.displaylist = None

    def __repr__(s):
        return s.texture.__repr__()


class Textureset:
    """Texturesets contain and name textures."""

    def __init__(s):
        s.textures = {}
    def load(s, texname=None, texappend=".png"):
        s.textures[texname] = GL_Texture(texname, texappend)
    def set(s, texname, data):
        s.textures[texname] = data
    def delete(s, texname):
        del s.textures[texname]
    def __del__(s):
        s.textures.clear()
        del s.textures
    def get(s, name):
        return s.textures[name]


class GL_Image:
    def __init__(self, texset, texname):
        self.texture = texset.get(texname)
        self.width = self.texture.width
        self.height = self.texture.height
        self.abspos=None
        self.relpos=None
        self.color=(1,1,1,1)
        self.rotation=0
        self.rotationCenter=None

    def draw(self, abspos=None, relpos=None, width=None, height=None,
            color=None, rotation=None, rotationCenter=None):
        if color==None:
            color = self.color

        glColor4fv(color)

        if abspos:
            glLoadIdentity()
            glTranslate(abspos[0],abspos[1],0)
        elif relpos:
            glTranslate(relpos[0],relpos[1],0)

        if rotation==None:
            rotation=self.rotation

        if rotation != 0:
                if rotationCenter == None:
                    rotationCenter = (self.width / 2, self.height / 2)
                # (w,h) = rotationCenter
                #glTranslate(rotationCenter[0],rotationCenter[1],0)
                glTranslate(0,rotationCenter[1],0)
                glRotate(rotation,-1,0,0)
                glTranslate(0,-rotationCenter[1],0)

        if width or height:
            if not width:
                width = self.width
            elif not height:
                height = self.height

            glScalef(width/(self.width*1.0), height/(self.height*1.0), 1.0)


        glCallList(self.texture.displaylist)

        if rotation != 0: # reverse
            # glTranslate(rotationCenter[0],rotationCenter[1],0)
            glTranslate(0,rotationCenter[1],0)
            glRotate(-rotation,-1,0,0)
            glTranslate(0,-rotationCenter[1],0)


if __name__=="__main__":
    pass
