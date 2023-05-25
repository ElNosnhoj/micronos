#===================================================================
# file: udp_stream.py
# desc: sets up a basic udp server that streams data
# dev : nos
#===================================================================
import socket
import machine      #type: ignore
import errno
import time

class UDP_STREAM:
    def __init__(self,host='0.0.0.0',port=65000,hook=lambda:"",hz=None):
        self.connected=[]
        self.host=host
        self.port=port
        self.hook=hook
        self.hz=hz
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind((host, port))
        self.udp.setblocking(False)
        
        print("UDP server @%s:%s" % (host,port))
        
    def __msg(self):
        msg=self.hook()
        if msg==None: return
        try: msg.decode('utf-8')
        except: msg=msg.encode('utf-8')
        return msg
    def start(self):
        while True:
            try:
                msg,addr=self.udp.recvfrom(1024)
                print("%s --> %s" % (addr[0],msg))
                if msg==b'start':
                    if addr in self.connected: pass   # already in
                    else: self.connected.append(addr)
                elif msg==b'stop':
                    if addr in self.connected:
                        self.connected.remove(addr)
                elif msg==b'once':
                    if addr in self.connected: continue
                    else: self.udp.sendto(self.__msg(), addr)
                        
                    
                        
            except OSError as e:
                if e.errno==errno.EAGAIN: pass
                else: raise Exception("aksjdlask")
            
            if len(self.connected)>0:
                msg=self.__msg()
                if self.hz: time.sleep(1/self.hz)
                for c in self.connected:
                    self.udp.sendto(msg, c)


if __name__ == "__main__":
    # adc setup
    vref=3.271
    scale=vref/65535
    adc = machine.ADC(28)
    get_adc = lambda: str(round(scale*adc.read_u16(),3)).encode('utf-8')
    print({'v':123})
    
    import nos.util.wifi as wifi
    wifi.connect("NOSNET","handsome")
    wifi.check()
    print(wifi.get_ipv4())
    
    
    udp=UDP_STREAM(hook=get_adc)
    # udp.start()
    
    
