
#===================================================================
# file: WS2812x.py
# desc: addressable leds
# dev : nos
# mcu :
#   * rpi pico v2
#   * esp32-wroom
#===================================================================
from machine import Pin,bitstream  # type: ignore

def RGB(r, g, b, a=1.0):
    """ returns int given r,g,b,a values. """
    return int(r*a)<<16 | int(g*a)<<8 | int(b*a)
def getRGB(val):
    """ takes rgb values and extracts r,g,b """
    return ((val>>x&0xff) for x in [16,8,0])
def maprange(x,a,b,c,d):
    return (x-a)/(b-a)*(d-c)+c
def gradient_rainbow(val):
    """ Provides 0-255 gradient rainbow rgb values """
    val = int(val)
    r=g=b=0
    if val<0: return gradient_rainbow(val+0xff)
    if val>255: return gradient_rainbow(val-0xff)
    elif val<85:
        g=int(val*3)
        r=255-g 
    elif val<170:
        val-=85
        b=int(val*3)
        g=255-b
    else:
        val-=170
        r=int(val*3)
        b=255-r
    return RGB(r,g,b)
def RGBA(rgba):
    """ given rgba value, converts to rgb """
    r,g,b=getRGB(rgba>>8)
    a=(rgba&0xff)/0xff
    return RGB(r,g,b,a)
def alpha(rgb,a=1.0):
    """ applies an alpha to an rgb """
    r,g,b=getRGB(rgb)
    return RGB(r,g,b,a)

class WS2812x:
    def __init__(self,pin:int,amnt:int,auto:bool=False, **kwargs):
        """ Controls addressable leds 
        * pin (`int`)   : data pin 
        * amnt (`int`)  : amount of leds you want to control
        * auto (`int`)  : true to auto render when changing values
        """
        self.pin=Pin(pin,Pin.OUT)
        self.amnt=amnt
        self.auto=auto
        
        self.__a=bytearray(amnt*3)

    def __repr__(self) -> str:
        return self.__a

    def __setitem__(self,i,rgb):
        r,g,b=((rgb>>x&0xff) for x in [16,8,0])
        i=i*3
        self.__a[i+0]=g
        self.__a[i+1]=r
        self.__a[i+2]=b
        if self.auto: self.render()

    def __getitem__(self,i):
        i=i*3
        g=self.__a[i+0]
        r=self.__a[i+1]
        b=self.__a[i+2]
        return r<<16 | g<<8 | b
        
    def roll(self,amnt):
        """ shifts list by amnt"""
        __a = self.auto
        self.auto=False
        self.__a[:]=self.__a[amnt*3:]+self.__a[:amnt*3]
        self.auto=__a
        if self.auto: self.render()
        
    def fill(self,rgb):
        """ fills the leds with one color """
        __a = self.auto
        self.auto=False
        for i in range(self.amnt):
            self[i]=rgb
        self.auto=__a
        if self.auto: self.render()
    
    def clear(self):
        __a = self.auto
        self.auto=False
        for i in range(self.amnt):
            self[i]=0
        self.render()
        self.auto=__a
        
    
    def render(self):
        """ render the colors to the strip """
        bitstream(self.pin,0,(400, 850, 800, 450),self.__a) #(800, 1700, 1600, 900)

def ie_cycle_rainbow_fast(strip):
    strip.auto=False
    for i in range(strip.amnt):
        strip[i]=gradient_rainbow(maprange(i,0,strip.amnt,0,255))
        
    strip.auto=True
    while True:
        strip.roll(1)
        # time.sleep(0.1)

if __name__ == "__main__":
    strip=WS2812x(13,8)
    # print(strip[0])
    # strip.auto=True
    # strip.fill(0xff0000)
    ie_cycle_rainbow_fast(strip)
    # strip.roll(-1)
    # time.sleep(1)
    
    # strip.clear()


