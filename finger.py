import time
from machine import UART,Pin
import struct


HEADER = b"\xEF\x01"
DEVICE_ADDR = b"\xFF\xFF\xFF\xFF"
FINGERPRINT_NUMBER = b"\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x1d\x00\x21"
BREATH_LED = b"\xef\x01\xff\xff\xff\xff\x01\x00\x07\x3c\x01\x02\x04\x64\x00\xaf"
BLUE_LED = b"\xef\x01\xff\xff\xff\xff\x01\x00\x07\x3c\x03\x01\x01\x05\x00\x4e"
RED_LED = b"\xef\x01\xff\xff\xff\xff\x01\x00\x07\x3c\x03\x04\x04\x01\x00\x50"
GREEN_LED = b"\xef\x01\xff\xff\xff\xff\x01\x00\x07\x3c\x03\x02\x02\x01\x00\x4c"
OFF_LED = b"\xef\x01\xff\xff\xff\xff\x01\x00\x07\x3c\x03\x00\x00\x01\x00\x48"
#SEARCH_FINGER= b"\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x08\x32\x01\x00\x01\x00\x02\x00\x3F"
#SEARCH_FINGER= b"\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x08\x32\x01\xFF\xFF\x00\x02\x02\x3C"
#SEARCH_FINGER= b"\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x08\x32\x01\xFF\xFF\x00\x00\x02\x3a"
SEARCH_FINGER= b"\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x08\x32\x01\xFF\xFF\x00\x20\x02\x5a"
REGISTER_FINGER_HEADER = b"\xEF\x01\xff\xff\xff\xff\x01\x00\x08\x31"
REGISTER_TAIL = b"\x04\x00\x2A"
REGISTER_FINGER_HEADER_VALUE = b"\x01\x00\x08\x31"
REGISTER_FINGER_ID = None
REGISTER_VERIFY_VALUE= None
GRANT_FINGER=b'\x08\x00\x05'
#REGISTER_FINALL_CMD = REGISTER_FINGER_HEADER + REGISTER_FINGER_ID + REGISTER_TAIL + REGISTER_VERIFY_VALUE
SENSOR_STAT = b"\xEF\x01\xFF\xFF\xFF\xFF\x01\x00\x03\x36\x00\x3A"
TIME_STAMP = time.time()
PASTTIME = 0
#ADMINLIST = [""]


class FINGER():
    def __init__(self,uart=1,rx=22,tx=23,freq=57600):
        self.rx = rx#yellow wire is rx
        self.tx = tx#black wire is tx
        self.uart = uart
        self.freq = freq
        self.finger_uart = UART(1,57600,rx = 22,tx =23)
        self.finger_uart.init(57600,bits = 8,parity = None,stop = 1)


    def write_cmd(self,cmd):
        self.finger_uart.write(cmd)
        time.sleep(0.1)

    
    def read_cmd(self):
        return(self.finger_uart.read())


    def calibrate_spawn(self,calibrate_value):
        try:
            empty_list = list()
            for i in calibrate_value:
                empty_list.append(i)
            calibrated_value = sum(empty_list)
            return struct.pack("B",calibrated_value)
        except BaseException as e:
            return "calibrate_spawn error"
    
    def query_savednum(self):
        try:
            self.write_cmd(FINGERPRINT_NUMBER)
            time.sleep(0.001)
            callback = int.from_bytes(self.read_cmd()[10:12],"big")
            return callback
        except BaseException as e:
            return "query_savednum error"


    def query_sensorstat(self):
        try:
            self.write_cmd(SENSOR_STAT)
            time.sleep(0.01)
            stat = self.read_cmd()
            if stat is None:
                return False
            else:
                return True
        except BaseException as e:
            return "sensor_stat error"

    
    def register_fingerprinter(self):

            register_cmd = REGISTER_FINGER_HEADER + self.finger_print_nextnum() + REGISTER_TAIL + self.spawn_finger_sumverify()
            print(register_cmd)
            self.write_cmd(register_cmd)
            time.sleep(3)
            callback = self.read_cmd()
            print(callback)

    def search_fingerprinter(self):
        self.write_cmd(SEARCH_FINGER)
        try:
            callback = self.read_cmd()
            #print(callback)
            ifgrant = callback[8:11]
            finger_id = callback[11:13]
            return ifgrant,finger_id
        except BaseException as e:
            return "SEARCH_ERROR"
            
    
    
    def verify_finger(self):
        global TIME_STAMP
        global PASTTIME
        #global ADMINLIST
        current_timestamp = time.time()
        try:
            ifgrant,finger_id  = self.search_fingerprinter()
            if ifgrant == GRANT_FINGER:
                PASTTIME = current_timestamp - TIME_STAMP
                TIME_STAMP = time.time()
                #print(finger_id)


                return finger_id,"Grant succes",True,PASTTIME
            else:
                return finger_id,"Grant fail",False
        except BaseException as e:
            return "verify_finger error ,maybe the sensor is erroneous or no finger on the sensor",False

    def finger_print_nextnum(self):
        try:
            current_finger_num = int(self.query_savednum())
            next_finger_id = current_finger_num + 1
            return b"\x00"+ struct.pack("B",next_finger_id)
        except BaseException as e:
            return "finger_print_nextnum error"

    def spawn_finger_sumverify(self):
        try:

            current_id = self.finger_print_nextnum()
            print(current_id)
            sumvalue = sum(REGISTER_FINGER_HEADER_VALUE+current_id+REGISTER_TAIL)

            print(b"\x00"+ struct.pack("B",sumvalue))

            return b"\x00"+ struct.pack("B",sumvalue)
        except BaseException as e:
            return"spawn_finger_sumverify error"
        

    def breath_led(self):
        try:
            self.write_cmd(BREATH_LED)
            time.sleep(0.001)
            self.read_cmd()
        except BaseException as e:
            return "breath_led error"

    def red_led(self):
        try:
            self.write_cmd(RED_LED)
            time.sleep(0.001)
            self.read_cmd()
        except BaseException as e:
            return "red_led error"

    def blue_led(self):
        try:
            self.write_cmd(BLUE_LED)
            time.sleep(0.001)
            self.read_cmd()
        except BaseException as e:
            return "blue_led error"

    def green_led(self):
        try:
            self.write_cmd(GREEN_LED)
            time.sleep(0.001)
            self.read_cmd()
        except BaseException as e:
            return "green_led error"

    def off_led(self):
        try:
            self.write_cmd(OFF_LED)
            time.sleep(0.001)
            self.read_cmd()
        except BaseException as e:
            return "off_led error"