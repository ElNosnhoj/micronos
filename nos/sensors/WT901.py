#===================================================================
# file: WT901.py
# desc: gyro, accel, magn, and angle from sensor
# dev : nos
# mcu :
#   * rpi pico v2
#===================================================================
from nos.util.i2c import NosI2CDevice
from math import atan2, radians as rad, floor
import time

class WT901(NosI2CDevice):
    DEF_ADDR    = 0x50
    
    R_SAVE 		= 0x00
    R_CALSW 	= 0x01
    R_RSW 		= 0x02
    R_RRATE		= 0x03
    R_BAUD 		= 0x04
    R_AXOFFSET	= 0x05
    R_AYOFFSET	= 0x06
    R_AZOFFSET	= 0x07
    R_GXOFFSET	= 0x08
    R_GYOFFSET	= 0x09
    R_GZOFFSET	= 0x0a
    R_HXOFFSET	= 0x0b
    R_HYOFFSET	= 0x0c
    R_HZOFFSET	= 0x0d
    R_D0MODE	= 0x0e
    R_D1MODE	= 0x0f
    R_D2MODE	= 0x10
    R_D3MODE	= 0x11
    R_D0PWMH	= 0x12
    R_D1PWMH	= 0x13
    R_D2PWMH	= 0x14
    R_D3PWMH	= 0x15
    R_D0PWMT	= 0x16
    R_D1PWMT	= 0x17
    R_D2PWMT	= 0x18
    R_D3PWMT	= 0x19
    R_IICADDR	= 0x1a
    R_LEDOFF 	= 0x1b
    R_GPSBAUD	= 0x1c
    R_YYMM		= 0x30
    R_DDHH		= 0x31
    R_MMSS		= 0x32
    R_MS		= 0x33
    R_AX		= 0x34
    R_AY		= 0x35
    R_AZ		= 0x36
    R_GX		= 0x37
    R_GY		= 0x38
    R_GZ		= 0x39
    R_HX		= 0x3a
    R_HY		= 0x3b
    R_HZ		= 0x3c
    R_Roll		= 0x3d
    R_Pitch		= 0x3e
    R_Yaw		= 0x3f
    R_TEMP		= 0x40
    R_D0Status	= 0x41
    R_D1Status	= 0x42
    R_D2Status	= 0x43
    R_D3Status	= 0x44
    R_PressureL	= 0x45
    R_PressureH	= 0x46
    R_HeightL	= 0x47
    R_HeightH	= 0x48
    R_LonL		= 0x49
    R_LonH		= 0x4a
    R_LatL		= 0x4b
    R_LatH		= 0x4c
    R_GPSHeight = 0x4d
    R_GPSYAW    = 0x4e
    R_GPSVL		= 0x4f
    R_GPSVH		= 0x50
    R_Q0        = 0x51
    R_Q1        = 0x52
    R_Q2        = 0x53
    R_Q3        = 0x54
    
    class UNIT_EXCEPTION(Exception):pass
    class RANGE_ERROR(Exception):pass
    
    def __xyz(self,d,scalar=1):
        """ takes 6 bytes and splits by 2. little endian """
        x=int.from_bytes(d[0:2],'little')
        y=int.from_bytes(d[2:4],'little')
        z=int.from_bytes(d[4:6],'little')
        if x>=0x8000: x+=-0xffff-1
        if y>=0x8000: y+=-0xffff-1
        if z>=0x8000: z+=-0xffff-1
        return x*scalar,y*scalar,z*scalar
    
    def get_angles(self,unit='d'):
        """ Get roll,pitch,yaw """
        if unit not in ['d', 'r']: raise self.UNIT_EXCEPTION
        
        data = self.read_reg(self.R_Roll,6)
        roll,pitch,yaw = self.__xyz(data,180/32768)
        if unit=='d': return roll,pitch,yaw
        else: return rad(roll),rad(pitch),rad(yaw)
        
    def get_angular_velocity(self): # wx,wy,wz in °/s
        return self.__xyz(self.read_reg(self.R_GX,6),2000/32768)
    
    def get_acceleration(self): # ax,ay,az in g = 9.8m/s^2
        return self.__xyz(self.read_reg(self.R_AX,6),16/32768)
    
    def get_magnetic(self):
        return self.__xyz(self.read_reg(self.R_HX,6))
    
    def get_data(self):
        """ Gets all data and parses into dict """
        data = self.read_reg(self.R_AX,24)
        ax,ay,az=self.__xyz(data[0:6],16/32768)
        wx,wy,wz=self.__xyz(data[6:12],2000/32768)
        mx,my,mz=self.__xyz(data[12:18])
        rx,ry,rz=self.__xyz(data[18:24],180/32768)
        
        d = {
            'acceleration'      : {'x':ax,'y':ay,'z':az},
            'angular_velocity'  : {'x':wx,'y':wy,'z':wz},
            'magnetic'          : {'x':mx,'y':my,'z':mz},
            'angle'             : {'x':rx,'y':ry,'z':rz}
        }
        return d
    
if __name__ == "__main__":
    from nos.util.i2c import NosI2C
    from math import degrees,sqrt
    i2c=NosI2C(scl=5,sda=4)
    i2c.scan()
    wt = WT901(0x50,i2c=i2c)
    # print(wt.get_angles())
    rg=[0,0,0]
    dt=0.1
    while True:
        time.sleep(0.1)
        d=wt.get_data()
        
        rx = degrees(atan2(d['acceleration']['y'],sqrt(d['acceleration']['x']**2+d['acceleration']['z']**2)))
        ry = degrees(atan2(d['acceleration']['x'],sqrt(d['acceleration']['y']**2+d['acceleration']['z']**2)))
        rg[0]+=d['angular_velocity']['x']*dt
        rg[1]+=d['angular_velocity']['y']*dt
        rg[2]+=d['angular_velocity']['z']*dt
        
        c=0.80
        rg[0]=c * (rg[0] - 0) + (1-c) * rx
        rg[1]=c * (rg[1] - 0) + (1-c) * ry
        print("given: %s"%d['angle'])
        print("check: %s"%{'x':rg[0],'y':rg[1],'z':rg[2]})
        
    
