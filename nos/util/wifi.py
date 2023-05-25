#===================================================================
# file: wifi.py
# desc: setup wifi
# dev : nos
# mcu :
#   * rpi pico v2
#===================================================================
from nos.util.tools import CTO,CTO_TIMEOUT
import network      #type: ignore
import ubinascii    #type: ignore

class WIFI(network.WLAN):
    def __init__(self,ssid,pswd):
        self.ssid=ssid
        self.pswd=pswd
        super().__init__(network.STA_IF)

    def connect(self,**kwargs):
        """ attempts connection. no checking.
        * ssid (`str`): network ssid.
        * pswd (`str`): password for network
        """
        ssid=kwargs.pop('ssid', self.ssid)
        pswd=kwargs.pop('pswd', self.pswd)
        
        self.active(True)
        super().connect(ssid,pswd)
        
    def check(self):
        """ checks connection. give it 10 seconds """
        if CTO(self.isconnected,10):
            addr=self.ifconfig()[0]
            print("addr: %s" % addr)
            return addr
        else: 
            print("failed to conenct")
            raise CTO_TIMEOUT
        
    def get_mac(self):
        return ubinascii.hexlify(self.config('mac'),':').decode()

    def get_ipv4(self):
        return self.ifconfig()[0]
        
    def get_status(self):
        """ Codes:
        * 0  Down
        * 1  Join
        * 2  NoIp
        * 3  Up
        * -1 Fail
        * -2 NoNet
        * -3 BadAuth
        """
        return self.status()

if __name__ == "__main__":
    wifi=WIFI("NOSNET","handsome")
    wifi.connect()
    wifi.check()
    print(wifi.get_status())
