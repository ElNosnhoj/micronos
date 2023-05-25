#===================================================================
# file: TCA9548A.py
# desc: i2c multiplexor.
# dev : nos
# mcu :
#   * rpi pico v2
#===================================================================
from nos.util.i2c import NosI2CDevice

class TCA9548A(NosI2CDevice):
    def set_channels(self,b):
        """ sets the multiplexor channel
        * b (`int`): 8 bit. each channel represents a bit.
        """
        if b>0xff: b=0xff
        self.i2c.writeto(self.addr,b.to_bytes(1,'big'))
    def get_channels(self):
        """ gets channel status """
        res = self.i2c.readfrom(self.addr,1)
        return res.hex()
    channels=property(get_channels,set_channels)
    
