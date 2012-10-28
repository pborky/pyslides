

class Message(object):
    def __init__(self, payload, *args, **kwargs):
        self.payload = payload
        self.args = args
        self.kwargs = kwargs
    def __unicode__(self):
        return u'%s' % self.payload
    def __str__(self):
        return '%s' % self.payload

class Transceiver(object):
    def __init__(self):
        from Queue import Queue
        print 'Initialising queue.'
        self.queue = Queue()
    def _get_name(self):
        from threading import currentThread
        return currentThread().getName()
    def enqueue(self, msg):
        from Queue import Full
        if not isinstance(msg, Message):
            raise Exception('%s: Das Fak !' % self._get_name())
        try:
            print '%s: Enqueue %s.'  % (self._get_name(),msg)
            #self.queue.put(msg,block=True,timeout=1.0)
            self.queue.put_nowait(msg)
        except Full:
            print '%s: Queue busy. Dropping %s.' % (self._get_name(),msg)
    def _process(self, msg):
        raise Exception('Not implemented.')
    def __call__(self, *args, **kwargs):
        from Queue import Empty
        while True:
            try:
                msg = self.queue.get(block=True)
            except Empty:
                continue
            self._process(msg)

class StdOutTransceiver(Transceiver):
    def _process(self,msg):
        print '%s: Message received: %s' % (self._get_name(),msg)

class JsonTransceiver(Transceiver):
    def __init__(self, fn):
        super(JsonTransceiver, self).__init__()
        import json
        try:
            f = open(fn,'a')
            f.close()
        except IOError as e:
            print 'File %s cannot be opened.' % fn
            raise e
        self.fn = fn
    def _process(self,msg):
        import json
        f = open(self.fn,'r')
        try:
            try:
                o = json.load(f)
                o.append(msg.payload)
            except ValueError:
                o = [msg.payload]
        finally:
            f.close()
        f = open(self.fn,'w')
        try:
            json.dump(o,f,indent=True)
        finally:
            f.close()

        print '%s: Message stored: %s' % (self._get_name(),msg)
class GpioTransceiver(Transceiver):
    def __init__(self, pin, bcd=True): # pin = 25 or 23
        super(GpioTransceiver, self).__init__()
        self.pin = pin
        self.bcd = bcd
        try:self._init(pin)
        except: pass
    def _init(self,pin):
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.OUT)
    def _send(self,data):
        import RPi.GPIO as GPIO
        from time import sleep
        GPIO.output(self.pin, GPIO.LOW)
        sleep(0.1)
        GPIO.output(self.pin, GPIO.HIGH)
        sleep(0.1)
        for i in data:
            for j in i:
                GPIO.output(self.pin, GPIO.LOW)
                sleep(0.01 if j == '0' else 0.04)
                GPIO.output(self.pin, GPIO.HIGH)
                sleep(0.04 if j == '0' else 0.01)
            sleep(0.1)
        GPIO.output(self.pin, GPIO.LOW)
    def _process(self,msg):
        data = []
        if self.bcd:
            data = msg.payload.get('img')
            if not data:
                data = msg.payload.get('principal')
            try:
                data = [bin(int(i))[2:].rjust(4,'0') for i in data]
            except:
                data = ['1010']
        else:
            data = msg.payload.get('key')
            if not data:
                data = ['']
            elif isinstance(data,int):
                data = ''.join('0' for i in range(data))
            else:
                data = ['']
        try: 
            self._send(data)
            print '%s: Message sent to pin %s: %s' % (self._get_name(), self.pin,data)
        except: 
            print '%s: Message FAILED to be sent: %s' % (self._get_name(),data)
