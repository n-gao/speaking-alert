import pyaudio
import audioop
import numpy as np
import inspect
import operator
import pyglet

FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
CHUNK = 256
BATCH_SECONDS = 0.2

BATCH_SIZE = int(RATE/CHUNK * BATCH_SECONDS)

class MyWindow(pyglet.window.Window):
    def __init__(self, screen):
        super().__init__(screen=screen, fullscreen=True)
        self.label = pyglet.text.Label('ZU LAUT!',
                          font_name='impact',
                          font_size=36,
                          x=self.width//2, y=self.height//2,
                          anchor_x='center', anchor_y='center')
        self.image = pyglet.image.SolidColorImagePattern((255, 0, 0, 255))\
                        .create_image(self.width, self.height)

    def on_draw(self):
        self.clear()
        self.image.blit(0, 0)
        self.label.draw()
                        

class MyEventLoop(pyglet.app.EventLoop):
    def __init__(self):
        super().__init__()
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                        rate=RATE, input=True,
                                        frames_per_buffer=CHUNK)
        self.batch = np.zeros((BATCH_SIZE, CHUNK))
        self.i = 0

    def idle(self):
        pyglet.clock.tick(poll=True)

        data = self.stream.read(CHUNK, exception_on_overflow=False)
        numpydata = np.fromstring(data, dtype=np.float32)
        self.batch[self.i] = numpydata
        self.i = (self.i+1) % BATCH_SIZE
        if self.i == 0:
            for window in pyglet.app.windows:
                window.set_visible(self.batch.max() > 0.6)

        for window in pyglet.app.windows:
            window.switch_to()
            window.dispatch_event('on_draw')
            window.flip()

        
        return pyglet.clock.get_sleep_time(sleep_idle=False)


display = pyglet.window.get_platform().get_default_display()
screens = display.get_screens()

windows = [MyWindow(screens[1]), MyWindow(screens[2])]

MyEventLoop().run()
