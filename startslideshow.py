# coding=utf-8
from pygtk import require
require('2.0')
import gtk

class Base(object):
    def __init__(self):
        from gtk import Window,WINDOW_TOPLEVEL,Button,Label,HBox,Entry,VBox,VSeparator
        self.window =  Window(WINDOW_TOPLEVEL)
        self.window.set_title("Hello Buttons!")
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
        from gtk.gdk import keyval_from_name
        if event.keyval in (keyval_from_name('Return'),keyval_from_name('Entre')):
            self.callback(widget)
    def callback(self, widget):
        from slideshow import SlideShow
        from trans import Message,GpioTransceiver,JsonTransceiver
        from threading import Thread

        def init_cb(name,trans):
            t = Thread(target=trans, name='%sThread'%name)
            t.daemon = True
            t.start()
            return trans.enqueue
        img_cbs = init_cb('ImgJsonCallback',JsonTransceiver('img.json')),\
                  init_cb('ImgGpioCallback',GpioTransceiver(12))
        kp_cbs = init_cb('KpJsonCallback',JsonTransceiver('kp.json')),\
                 init_cb('KpGpioCallback',GpioTransceiver(13, False))
        slide = SlideShow(
            path='/home/peterb/tmp/rpi/slideshow/img/',
            transition='Superimposition',
            fullscreen=False,
            delay=10,
            principal=self.editable.get_text(),
            img_callback = lambda msg: [cb(msg) for cb in img_cbs],
            kp_callback = lambda msg: [cb(msg) for cb in kp_cbs],
        )
        slide()
    def __call__(self):
        gtk.main()
if __name__ == '__main__':
    base = Base()
    base()