# aphytcomm
This is a library for communicating with industrial devices using Python.

Consider to be pre-alpha

Current development effort is to create Omron Ethernet/IP communications to NX and NJ controllers.

## Communicating with Omron Sysmac Controllers Using Ethernet/IP

The current release of this software implements the core functionality of reading and writing numeric and Boolean variables to an Omron NX or NJ controller using symbolic names. The key method that goes beyond CIP type requests is update_variable_dictionary. This method uses an Ethernet/IP explicit connection to get the names and data type codes of all published variables, both system and user defined. This information is then used to allow the programmer to use Python based Boolean and numeric data types to write to variables, as well as properly format the data received when reading variables. The example code below demonstrates how to establish the explicit Ethernet/IP connection and then read and write variables to a test project in the NJ or NX controller.
Currently Supported Data Types

    BOOLEAN
    SINT (1-byte signed binary)
    INT (1-word signed binary)
    DINT (2-word signed binary)
    LINT (4-word signed binary)
    USINT (1-byte unsigned binary)
    UINT (1-word unsigned binary)
    UDINT (2-word unsigned binary)
    ULINT (4-word unsigned binary)
    REAL 2-word floating point)
    LREAL (4-word floating point)

## Future Development

The plan is to support all CIP and Omron specific data types, including derived data types like arrays and structures. From there, development efforts will go to reading and writing to logical segments and supporting additional devices transparently.
Example Code

## Example Use

    import eip.n_series
    
    fake_eip_instance = eip.n_series.NSeriesEIP()
    fake_eip_instance.connect_explicit('192.168.250.13')
    fake_eip_instance.register_session()
    fake_eip_instance.update_variable_dictionary()
    
    reply = fake_eip_instance.read_variable('TestBoolFalse')
    print("TestBoolFalse: " + str(reply))
    reply = fake_eip_instance.write_variable('TestBoolFalse', True)
    reply = fake_eip_instance.read_variable('TestBoolFalse')
    print("TestBoolFalse: " + str(reply))
    reply = fake_eip_instance.write_variable('TestBoolFalse', False)
    reply = fake_eip_instance.read_variable('TestBoolFalse')
    print("TestBoolFalse: " + str(reply))
    
    reply = fake_eip_instance.read_variable('TestBoolTrue')
    print("TestBoolTrue: " + str(reply))
    
    reply = fake_eip_instance.read_variable('TestInt1')
    print("TestInt1: " + str(reply))
    reply = fake_eip_instance.write_variable('TestInt1', 2)
    reply = fake_eip_instance.read_variable('TestInt1')
    print("TestInt1: " + str(reply))
    reply = fake_eip_instance.write_variable('TestInt1', 1)
    reply = fake_eip_instance.read_variable('TestInt1')
    print("TestInt1: " + str(reply))
    
    reply = fake_eip_instance.read_variable('TestLREAL')
    print("TestLREAL: " + str(reply))
    reply = fake_eip_instance.write_variable('TestLREAL', 63.12)
    reply = fake_eip_instance.read_variable('TestLREAL')
    print("TestLREAL: " + str(reply))
    reply = fake_eip_instance.write_variable('TestLREAL', 3.4)
    reply = fake_eip_instance.read_variable('TestLREAL')
    print("TestLREAL: " + str(reply))
    
    fake_eip_instance.close_explicit()