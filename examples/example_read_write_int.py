import time
from aphyt import omron


if __name__ == '__main__':
    with omron.NSeries('192.168.250.9') as eip_conn:
        for i in range(10):
            print(eip_conn.read_variable('test_Int'))
            eip_conn.write_variable('test_Int', 24)
            print(eip_conn.read_variable('test_Int'))
            eip_conn.write_variable('test_Int', 7)
            time.sleep(.5)
