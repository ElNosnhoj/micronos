#===================================================================
# file: TCA9548A.py
# desc: i2c multiplexor.
# dev : nos
# mcu :
#   * rpi pico v2
#===================================================================
from nos.util.i2c import NosI2CDevice

class TCA9548A(NosI2CDevice):
    DEF_ADDR = 0x70
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
    

if __name__ == "__main__":
    from nos.util.i2c import NosI2C
    i2c=NosI2C(scl=5,sda=4)
    tca =TCA9548A(TCA9548A.DEF_ADDR,i2c=i2c)
    
    tca.channels = 0x3
    i2c.scan()
    
    
