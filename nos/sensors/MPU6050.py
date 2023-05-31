#===================================================================
# file: MPU6050.py
# desc: gyro&accel data.
# dev : nos
# mcu :
#   * rpi pico v2
#===================================================================
from nos.util.i2c import NosI2CDevice
from math import atan2, degrees,sqrt
import time

class MPU6050(NosI2CDevice):
    DEF_ADDR        = 0x68
    
    # read write
    RW_SMPLRT_DIV   = 25    # sample rate
    RW_GYRO_CONFIG  = 27
    RW_ACCEL_CONFIG = 28
    RW_INT_ENABLE   = 56
    RW_PWR_MGMT_1   = 107
    RW_PWR_MGMT_2   = 108
    
    # read
    R_INT_STATUS    = 57
    R_ACCEL_XOUT_H  = 59
    R_ACCEL_XOUT_L  = 60
    R_ACCEL_YOUT_H  = 61
    R_ACCEL_YOUT_L  = 62
    R_ACCEL_ZOUT_H  = 63
    R_ACCEL_ZOUT_L  = 64
    R_TEMP_H        = 65
    R_TEMP_L        = 66
    R_GYRO_XOUT_H   = 67
    R_GYRO_XOUT_L   = 68
    R_GYRO_YOUT_H   = 69
    R_GYRO_YOUT_L   = 70
    R_GYRO_ZOUT_H   = 71
    R_GYRO_ZOUT_L   = 72
    R_WHO_AM_I      = 117
    
    class UNIT_EXCEPTION(Exception):pass
    class RANGE_ERROR(Exception):pass
    
    def init(self):
        """ some setup """
        self.accel_lsb = 0x4000
        self.gyro_lsb = 0x83
        
        # wake. set 7th to 1 to reset.
        self.write_reg(self.RW_PWR_MGMT_1,0x0)   
        
        # setup gyro and accel
        data = self.read_reg(self.RW_GYRO_CONFIG,1)
        fs_sel = int.from_bytes(data,'big')>>3&0b11
        self.gyro_lsb = [131,65.5,32.8,16.4][fs_sel]
        
        data = self.read_reg(self.RW_ACCEL_CONFIG,1)
        afs_sel = int.from_bytes(data,'big')>>3&0b11
        self.accel_lsb = [16384,8192,4096,2048][afs_sel]
        
        self.set_gyro_range(0)
        self.set_accel_range(0)
        
        time.sleep(0.1)
        self.__t0 = time.ticks_us()
        self.__rz=0
        
        self.__rg=[0,0,0]
        self.__drift=[0,0,0]
        
    def write_reg(self,reg,data):
        data=data.to_bytes(2,'big')
        self.i2c.write_reg(self.addr,reg,data)
    def read_reg(self,reg,nbytes=1):
        return self.i2c.read_reg(self.addr,reg,nbytes)
    
    def set_accel_range(self,r:int):
        """ set accelerometer full scale range based on datasheet
        * r (`int`): 0-3
        """
        if r not in range(4): raise self.RANGE_ERROR
        self.write_reg(self.RW_GYRO_CONFIG,r<<3)
        self.accel_lsb = [16384,8192,4096,2048][r]
        
    def set_gyro_range(self,r:int):
        """ set gyro full scale range based on datasheet
        * r (`int`): 0-3
        """
        if r not in range(4): raise self.RANGE_ERROR
        self.write_reg(self.RW_ACCEL_CONFIG,r<<3)
        self.gyro_lsb = [131,65.5,32.8,16.4][r]
    
    def __xyz(self,d,divisor=1):
        x=int.from_bytes(d[0:2],'big')
        y=int.from_bytes(d[2:4],'big')
        z=int.from_bytes(d[4:6],'big')
        
        if x>=0x8000: x+=-0xffff-1
        if y>=0x8000: y+=-0xffff-1
        if z>=0x8000: z+=-0xffff-1
        
        return x/divisor,y/divisor,z/divisor
    def get_data(self):
        """ Gets all data and parses into dict """
        data = self.read_reg(self.R_ACCEL_XOUT_H,14)
        t1 = time.ticks_us()
        dt = (t1-self.__t0)/1000000
        self.__t0 = t1
        
        # temperature 
        t = int.from_bytes(data[6:8],'big')
        if t>=0x8000: t+=-0xffff-1
        c=t/340+36.53
        
        # accel and gyro. units: g(9.8m/s^2) and º/s
        ax,ay,az = self.__xyz(data[0:6],self.accel_lsb)
        wx,wy,wz = self.__xyz(data[8:14],self.gyro_lsb)
        
        # angle without accounting gravity
        # rx=degrees(atan2(ay,az))
        # ry=degrees(atan2(ax,az))
        # self.__rz+=gz*dt
        
        # angles with accounting gravity
        # rx=degrees(atan2(ay,sqrt(ax*ax+az*az)))
        # ry=degrees(-atan2(ax,sqrt(ay*ay+az*az)))
        # self.__rz+=gz*dt
        
        # angles with some filtering. basic complimentary. with gravity. 
        self.__c = 0.80
        rx = degrees(atan2(ay,sqrt(ax**2+az**2)))
        ry = degrees(atan2(-ax,sqrt(ay**2+az**2)))
        self.__rg[0]+=wx*dt
        self.__rg[1]+=wy*dt
        self.__rg[2]+=wz*dt
        
        self.__rg[0]=self.__c * (self.__rg[0] - self.__drift[0]) + (1-self.__c) * rx
        self.__rg[1]=self.__c * (self.__rg[1] - self.__drift[1]) + (1-self.__c) * ry
        self.__rg[2]=self.__rg[2] - 0.18
        
        res = {
            'acceleration'      : {'x':ax,'y':ay,'z':az},
            'angular_velocity'  : {'x':wx,'y':wy,'z':wz},
            'angle'             : {'x':self.__rg[0],'y':self.__rg[1],'z':self.__rg[2]}
        }
        return res
    
    
if __name__ == "__main__":
    from nos.util.i2c import NosI2C
    i2c=NosI2C(scl=5,sda=4)
    mpu=MPU6050(0x68,i2c=i2c)
    while True:
        time.sleep(0.1)
        d=mpu.get_data()
        print(d['angle'])

        
        
        