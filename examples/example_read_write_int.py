import time
from aphyt import omron


if __name__ == '__main__':
    eip_conn = omron.NSeries('192.168.250.9')
    for i in range(10):
        print(eip_conn.read_variable('TestInt'))
        eip_conn.write_variable('TestInt', 24)
        print(eip_conn.read_variable('TestInt'))
        eip_conn.write_variable('TestInt', 7)
        time.sleep(.5)
    eip_conn.close_explicit()
