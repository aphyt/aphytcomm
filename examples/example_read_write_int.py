import time
from aphyt import omron


if __name__ == '__main__':
    with omron.NSeries('192.168.250.9') as eip_conn:
        for i in range(10):
            print(eip_conn.read_variable('TestInt'))
            eip_conn.write_variable('TestInt', 24)
            print(eip_conn.read_variable('TestInt'))
            eip_conn.write_variable('TestInt', 7)
            time.sleep(.5)
