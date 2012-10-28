
from os import environ as env
from collections import Iterable
from sys import exit
from trans import Message

import pygame

#import image     ## Will be adding later for a wider support of image formats.
#import pymedia   ## Will be adding later for a wider support of audio formats.

IMAGE_TYPES = ('.jpg', '.jpeg', '.png')

class JsonMessage(Message):
    def __init__(self, payload):
        from datetime import datetime
        payload.update({'timestamp':datetime.now().isoformat()})
        super(JsonMessage, self).__init__(payload)
    def __unicode__(self):
        return u'%s' % str(self)
    def __str__(self):
        from json import dumps
        return dumps(self.payload)
class ImgMessage(JsonMessage):
    def __init__(self, img,seq,fn,principal):
        super(ImgMessage, self).__init__({
            'principal': principal,
            'img': img,
            'seq': seq,
            'file': fn
        })
class KpMessage(JsonMessage):
    _KEYS = {
        pygame.K_KP0 : 0,
        pygame.K_KP1 : 1,
        pygame.K_KP2 : 2,
        pygame.K_KP3 : 3,
        pygame.K_KP4 : 4,
        pygame.K_KP5 : 5,
        pygame.K_KP6 : 6,
        pygame.K_KP7 : 7,
        pygame.K_KP8 : 8,
        pygame.K_KP9 : 9,
        pygame.K_KP_ENTER : -1
    }
    @classmethod
    def isValidKey(cls, key):
        return cls._KEYS.has_key(key)
    @classmethod
    def getKey(cls, key):
        return cls._KEYS.get(key)
    def __init__(self, key,seq, img,principal):
        if not KpMessage.isValidKey(key):
            raise Exception('Das Fak !')
        super(KpMessage, self).__init__({
            'principal': principal,
            'key': KpMessage.getKey(key),
            'seq': seq,
            'img': img
        })

class SlideShow(object):
    def __init__(self,
                 resolution=(400,300),
                 fullscreen=True,
                 path= '%(HOME)s/Pictures/' % env,
                 recursive=True,
                 order=False,
                 delay=5,
                 transition='None',
                 img_callback = None,
                 kp_callback = None,
                 principal = None):
        self.resolution =  resolution
        self.fullscreen = fullscreen
        self.delay = delay
        self.transition = transition
        self.img_callback = img_callback
        self.kp_callback = kp_callback
        self.principal = principal

        if callable(order):
            orderfnc = order
        elif order:
            orderfnc = lambda x: tuple(i for i in x)
        else:
            from numpy.random import permutation
            orderfnc = lambda x: permutation(x).tolist() if isinstance(x,Iterable) else x

        self.paths = orderfnc(self._getFilePaths(path, IMAGE_TYPES, recursive))

    def _getFilePaths(self, path, fileTypes, recursive=True):
        import os
        ## Returns list containing paths of files in /path/ that are of a file type in /fileTypes/,
        ##	if /recursive/ is False subdirectories are not checked.
        paths = []
        if recursive:
            for root, folders, files in os.walk(path, followlinks=True):
                for file in files:
                    for fileType in fileTypes:
                        if file.endswith(fileType):
                            paths.append(os.path.join(root, file))
        else:
            for item in os.listdir(path):
                for fileType in fileTypes:
                    if item.endswith(fileType):
                        paths.append(os.path.join(root, item))
        return paths

    def _rationalSizer(self, image, area):
        from pygame.transform import scale
        ## Returns /image/ resized for /area/ maintaining origional aspect ratio.
        ## Returns tuple containing x and y displacement to center resized /image/ correctly on /area/.
        width = float(image.get_width())
        height = float(image.get_height())
        xSizer = width / area[0]
        ySizer = height / area[1]
        if xSizer >= ySizer:
            sizer = xSizer
            yDisplace = int((area[1] - height/xSizer) / 2)
            xDisplace = 0
        else:
            sizer = ySizer
            xDisplace = int((area[0] - width/ySizer) / 2)
            yDisplace = 0
        return scale(image, (int(width/sizer),int(height/sizer))), (xDisplace, yDisplace)

    def __call__(self, *args, **kwargs):
        from  pygame import display
        from libtrans import transitions
        from os.path import basename
        import re
        display.init()
        if self.fullscreen:
            resolution = display.list_modes()[0]
            main_surface = display.set_mode(resolution, pygame.FULLSCREEN)
        else:
            resolution = self.resolution
            main_surface = display.set_mode(resolution)
        #main_surface.blit(pygame.image.load('/usr/share/pypicslideshow/img/loadingimages.png'), (100,50))
        pygame.display.update()
        if not len(self.paths) > 0:
            print '\n####  Error: No images found. Exiting!\n'
            exit(1)

        delay = self.delay * 1000
        if not delay > 0:
            print '\n##  Warning: Delay too short. Continuing with delay of 10s...'
            delay = 10000
        transition = self.transition
        if transition not in transitions.keys():
            print '\n##  Warning: ' + transition + ' is not a valid transition. Continuing with no transition...'
            transition = 'None'

        pygame.time.set_timer(pygame.USEREVENT + 1, int(delay))

        i = 0
        seq = 1
        img = None
        if callable(self.img_callback):
            self.img_callback.__call__(ImgMessage(None,None,None,self.principal))
        while True:
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    pygame.quit()
                    return -1
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return 0
                    elif KpMessage.isValidKey(event.key):
                        print '\nKeypress:   ' + event.unicode
                        if callable(self.kp_callback):
                            self.kp_callback.__call__(KpMessage(event.key,seq,img,self.principal))
                        seq += 1
                elif event.type == pygame.USEREVENT + 1:
                    seq = 1
                    i += 1
                    if i >= len(self.paths):
                        print '\nFinished.'
                        pygame.quit()
                        return i
                    fn = basename(self.paths[i])
                    img = re.match(r'(.*)[.][^.]+', fn).group(1).replace('.','')
                    print '\nShowing:   ' + self.paths[i]
                    if callable(self.img_callback):
                        self.img_callback.__call__(ImgMessage(img,i,fn,self.principal))
                    blitdata = self._rationalSizer(pygame.image.load(self.paths[i]), resolution)
                    main_surface = transitions[transition](main_surface, blitdata)
            pygame.time.wait(100)

