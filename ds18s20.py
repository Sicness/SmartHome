# idea and same code I took from:
# http://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software

from time import sleep

class ds18b20:
    def __init__(self, adr):
        self.__dev_adr = adr

    def read_temp_raw(self):
        try:
            f = open(self.__dev_adr, 'r')
        except:
            raise
        lines = f.readlines()
        f.close()
        return lines

    def read_c(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c

    def read_f(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_f

    def read_temp(self):
        """ Read temperature from sensor
        and return turpe (c, f) """
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f

# same tests
if __name__ == '__main__':
    ds = ds18b20('/sys/bus/w1/devices/10-0008025b6d03/w1_slave')

    print "read_c returned: ", ds.read_c()
    print "read_f returned: ", ds.read_f()
    print "read_temp returned: ", ds.read_temp()
