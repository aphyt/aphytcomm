# aphyt
This is a library for communicating with Omron NX and NJ industrial PLC and motion controllers using Ethernet/IP.

## Communicating with Omron Sysmac Controllers Using Ethernet/IP

This software implements the core functionality of reading and writing numeric, Boolean, string, structure and array variables to an Omron NX or NJ controller using symbolic names. The read_variable and write_variable methods allow the programmer to use Python based data types to write to variables, as well as properly format the data received when reading variables. The example code below demonstrates how to establish the explicit Ethernet/IP connection and then read and write variables to a test project in the NJ or NX controller.

## Example Use

### Installation

This package is on PyPI so the user can install using:

    pip install aphyt

### Getting Started

In order to connect to an Omron N-Series controller for data exchange using Ethernet/IP, the programmer should import omron from the aphyt module and instantiate an instance from the NSeries or NSeriesThreadDispatcher object using a context manager or by assignment. If the program supplies the host to the object, it is not necessary to explicitly connect to the IP address of the controller, and register a session. If the object is created without a host, the connection and session registration must be done explicitly.

```python
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

```
## Other Ethernet/IP Libraries
### Omron EIP for NodeJS
For users that want to communicate with an Omron NX/NJ controller from NodeJS or NodeRed, [omron-eip](https://github.com/ucsballen/omron-eip) has implemented similar functionality to aphyt for use in those environments.
### Python EIP for Rockwell Controllers
For Python users that need to communicate with Rockwell controllers, [Pylogix](https://github.com/dmroeder/pylogix) is a fully featured communications driver. Rockwell and Omron diverge on many vendor specific Ethernet/IP implementation details, so this is a better project if that is your target controller
### C EIP Library with Wrappers
[libplctag](https://github.com/libplctag/libplctag) is a library written in C with wrappers for many other languages including C++ and C#. They have implemented Omron specific functionality in addition to Rockwell. Since this library is written in C, it is very appropriate for applications where resource usage is limited.