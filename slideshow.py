
from os import environ as env
from sys import exit
from trans import Message

import pygame

#import image     ## Will be adding later for a wider support of image formats.
#import pymedia   ## Will be adding later for a wider support of audio formats.

IMAGE_TYPES = ('.jpg', '.jpeg', '.png')

def iterable(x):
    from collections import Iterable
    return isinstance(x,Iterable)

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
    _KEYS = { pygame.K_KP0 : 2, pygame.K_KP_PERIOD : 0, pygame.K_KP_ENTER : 1 }
    _VOTES = { 1: 'red', 2: 'green', 0: 'gray' }
    _COLORS = { 'red': (100,0,0), 'green': (0,100,0), 'gray': (50,50,50), 'black': (0,0,0) }
    @classmethod
    def isValidKey(cls, key):
        return cls._KEYS.has_key(key)
    @classmethod
    def getKey(cls, key):
        return cls._KEYS.get(key)
    @classmethod
    def getVote(cls, key):
        return cls._VOTES.get(key)
    @classmethod
    def getColor(cls, key):
        return cls._COLORS.get(key)
    def __init__(self, key, color, seq, img,principal):
        if not KpMessage.isValidKey(key):
            raise Exception('Das Fak !')
        super(KpMessage, self).__init__({
            'principal': principal,
            'key': KpMessage.getKey(key),
            'seq': seq,
            'img': img,
            'color': color
        })

class SlideShow(object):
    def __init__(self,
                 resolution=(400,300),
                 fullscreen=True,
                 path= '%(HOME)s/Pictures/' % env,
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
        self.paths = self._getFilePaths(path,order)

    def _getFilePaths(self, path, order):
        if callable(order):
            orderfnc = order
        elif order:
            orderfnc = lambda x: tuple(i for i in x)
        else:
            from numpy.random import permutation
            orderfnc = lambda x: permutation(x).tolist() if iterable(x) else x,
        return orderfnc(path)

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
    def _refresh(self, surface, blit, bg):
        surface.fill(bg)
        surface.blit(*blit)
        pygame.display.update()
        return surface
    def __call__(self, *args, **kwargs):
        from  pygame import display
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

        pygame.time.set_timer(pygame.USEREVENT + 1, int(delay))

        i = 0
        seq = 1
        img = None
        blitdata = None
        if callable(self.img_callback):
            self.img_callback.__call__(ImgMessage(None,None,None,self.principal))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return -1
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return 0
                    elif KpMessage.isValidKey(event.key):
                        print '\nKeypress:   ' + event.unicode
                        if callable(self.kp_callback):
                            color = KpMessage.getVote(KpMessage.getKey(event.key)) if KpMessage.isValidKey(event.key) else 'black'
                            self.kp_callback.__call__(KpMessage(event.key,color,seq,img,self.principal))
                            background = KpMessage.getColor(color)
                            if blitdata and background:
                                self._refresh(main_surface, blitdata, background)
                        seq += 1
                elif event.type == pygame.USEREVENT + 1:
                    if i >= len(self.paths):
                        if callable(self.img_callback):
                            self.img_callback.__call__(ImgMessage(None,None,None,self.principal))
                        print '\nFinished.'
                        pygame.quit()
                        return i
                    fn = basename(self.paths[i])
                    img = re.match(r'(.*)[.][^.]+', fn).group(1).replace('.','')
                    print '\nShowing:   ' + self.paths[i]
                    blitdata = self._rationalSizer(pygame.image.load(self.paths[i]), resolution)
                    main_surface = self._refresh(main_surface, blitdata, KpMessage.getColor('black'))
                    if callable(self.img_callback):
                        self.img_callback.__call__(ImgMessage(img,i,fn,self.principal))
                    i += 1
                    seq = 1
            pygame.time.wait(100)
