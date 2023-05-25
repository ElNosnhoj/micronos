#===================================================================
# file: i2c.py
# desc: uses SoftI2C.
# dev : nos
#===================================================================
from machine import Pin,SoftI2C #type: ignore
class NosI2C(SoftI2C):
    class NO_ADDR_PROVIDED(Exception):pass
    def __init__(self,scl:Pin,sda:Pin):
        """ NosI2C
        * scl (`int`)   : scl pin 
        * sda (`int`)   : sda pin 
        """
        if type(scl)!=Pin: scl=Pin(scl)
        if type(sda)!=Pin: sda=Pin(sda)
        
        self.__scl=scl
        self.__sda=sda
        
        super().__init__(scl,sda)
    
    def write_reg(self,addr,reg,data):
        """ write data to register 
        * addr  (`int`): address of device
        * reg   (`int`): register to write to
        * data  (`int`): data to write. should be 8bits    
        """
        self.writeto_mem(addr,reg,data)
        
    def read_reg(self,addr,reg,nbytes=1):
        """ read nbytes from reg
        * addr  (`int`): address of device
        * reg    (`int`): register to read from
        * nbytes (`int`): number of bytes to read  
        """
        return self.readfrom_mem(addr,reg,nbytes)   
     
    def scan(self):
        """ Prints detected addresses on the bus """
        res=super().scan() 
        print("scanned addresses: %s" % ([hex(i) for i in res]))
        return res
         
class NosI2CDevice:
    class INIT_ERROR(Exception):pass
    def __init__(self,addr,**kwargs):
        """ NosI2CDevice. Just stores address. Can share i2c
        * scl (`int`)   : scl pin 
        * sda (`int`)   : sda pin 
        * i2c (`NosI2C`): i2c object. scl and sda ignored if provided
        """
        self.addr=addr
        scl=kwargs.pop("scl",None)
        sda=kwargs.pop("sda",None)
        i2c=kwargs.pop("i2c",None)
        if i2c: 
            self.i2c=i2c        
        else:
            if scl and sda:
                self.i2c=NosI2C(scl,sda)
            else:
                raise NosI2CDevice.INIT_ERROR
        self.init()
    def init(self):
        pass
    
    def read_reg(self,reg,nbytes=1):
        """ read nbytes from reg
        * reg    (`int`): register to read from
        * nbytes (`int`): number of bytes to read  
        """
        return self.i2c.readfrom_mem(self.addr,reg,nbytes)
    
    

