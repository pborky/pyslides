# coding=utf-8
from pygtk import require
require('2.0')
import gtk

def iterable(x):
    from collections import Iterable
    return isinstance(x,Iterable)

class Base(object):
    def __init__(self):
        from gtk import Window,WINDOW_TOPLEVEL,Button,Label,HBox,Entry,VBox,VSeparator
        self.window =  Window(WINDOW_TOPLEVEL)
        self.window.set_title("Slideshow")
        self.window.connect("delete_event", self.delete_event)
        self.window.set_border_width(10)
        self.vbox = VBox(False, 0)
        self.window.add(self.vbox)
        self.hbox1 = HBox(False, 0)
        self.vbox.pack_start(self.hbox1, True, True, 1)
        self.hbox = HBox(False, 0)
        self.vbox.pack_start(self.hbox, False, False, 1)
        self.hbox2 = HBox(False, 0)
        self.vbox.pack_start(self.hbox2, True, True, 1)
        self.label = Label('Identifikační číslo:')
        self.hbox.pack_start(self.label, False, False, 1)
        self.label.show()
        self.editable = Entry()
        self.editable.connect('key_press_event', self.key_press_event)
        self.hbox.pack_start(self.editable, True, True, 1)
        self.editable.show()
        self.button = Button("Začít")
        self.button.connect("clicked", self.callback)
        self.button.set_receives_default(True)
        self.button.set_can_focus(True)
        self.hbox.pack_start(self.button, False, False, 1)
        self.button.show()
        self.hbox1.show()
        self.hbox.show()
        self.hbox2.show()
        self.vbox.show()
        self.window.show()
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
    def key_press_event(self, widget, event):
        from gtk.gdk import keyval_from_name,keyval_name
        if event.keyval in (keyval_from_name('Return'),keyval_from_name('KP_Enter')):
            self.callback(widget)
    def _getFilePaths(self, fileTypes, recursive=True):
        import os
        import re
        from sys import argv
        pt = re.compile(r'.*([%(0)s][^%(0)s]*)'%{'0':os.path.extsep})
        path = [a for m,a in ((pt.match(os.path.basename(a)),a) for a in argv[1:]) if m and m.group(1) in fileTypes]
        if not path:
            path = '/home/pi/img/*.jpg'
        if isinstance(path, str):
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
        elif iterable(path):
            return path
        else:
            return []
    def _init_cb(self,trans):
        from threading import Thread
        if not iterable(trans):
            trans = trans,
        callbacks  = []
        for name,cb in trans:
            t = Thread(target=cb, name='%sThread'%name)
            t.daemon = True
            t.start()
            callbacks.append(cb.enqueue)
        def wrap(msg):
            for cb in callbacks:
                if not cb(msg):
                    return False
            return True
        return wrap
    def callback(self, widget):
        from slideshow import SlideShow
        from trans import Message,GpioTransceiver,JsonTransceiver

        if not self.editable.get_text():
            return False
        img_cbs = self._init_cb([('ImgGpioCallback',GpioTransceiver(24)),('ImgJsonCallback',JsonTransceiver('img.json'))])
        kp_cbs = self._init_cb([('KpGpioCallback',GpioTransceiver(24)),('KpJsonCallback',JsonTransceiver('img.json'))])
        def ordfnc(path):
            from numpy.random import permutation
            gray = path[0]
            result = []
            for p in permutation(path[1:]):
                result.append(p)
                #result.append(gray)
            return result
        slide = SlideShow(
            path=self._getFilePaths(('.jpg', '.jpeg', '.png')),
            transition='None',
            fullscreen=True,
            delay=10,
            order=ordfnc,
            principal=self.editable.get_text(),
            img_callback = img_cbs,
            kp_callback = kp_cbs,
        )
        self.editable.set_text('')
        slide()
    def __call__(self):
        gtk.main()
if __name__ == '__main__':
    base = Base()
    base()
