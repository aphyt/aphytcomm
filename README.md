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
    STRING

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
    
    tale_of_two_cities_string_1 = \
        'In England, there was scarcely an amount of order and protection to justify much national boasting. ' \
        'Daring burglaries by armed men, and highway robberies, took place in the capital itself every night; ' \
        'families were publicly cautioned not to go out of town without removing their furniture to upholsterers' \
        ' warehouses for security; the highwayman in the dark was a City tradesman in the light, and, being ' \
        'recognised and challenged by his fellow-tradesman whom he stopped in his character of \"the Captain,\" ' \
        'gallantly shot him through the head and rode away; the mail was waylaid by seven robbers, and the guard shot ' \
        'three ' \
        'dead, and then got shot dead himself by the other four, \"in consequence of the failure of his ammunition:\" ' \
        'after which the mail was robbed in peace; that magnificent potentate, the Lord Mayor of London, was made to ' \
        'stand and deliver on Turnham Green, by one highwayman, who despoiled the illustrious creature in sight of ' \
        'all his retinue; prisoners in London gaols fought battles with their turnkeys, and the majesty of the law ' \
        'fired blunderbusses in among them, loaded with rounds of shot and ball; thieves snipped off diamond crosses ' \
        'from the necks of noble lords at Court drawing-rooms; musketeers went into St. Giles\'s, to search for ' \
        'contraband goods, and the mob fired on the musketeers, and the musketeers fired on the mob, and nobody thought ' \
        'any of these occurrences much out of the common way. In the midst of them, the hangman, ever busy and ' \
        'ever worse than useless, was in constant requisition; now, stringing up long rows of miscellaneous criminals; ' \
        'now, hanging a housebreaker on Saturday who had been taken on Tuesday; now, burning people in the hand ' \
        'at Newgate by the dozen, and now burning pamphlets at the door of Westminster Hall; to-day, taking the ' \
        'life of an atrocious murderer, and to-morrow of a wretched pilferer who had robbed a farmer\'s boy of sixpence.'
    tale_of_two_cities_string_2 = \
        'Two other passengers, besides the one, were plodding up the hill by the side of the mail. All three were ' \
        'wrapped to the cheekbones and over the ears, and wore jack-boots. Not one of the three could have said, ' \
        'from anything he saw, what either of the other two was like; and each was hidden under almost as many ' \
        'wrappers from the eyes of the mind, as from the eyes of the body, of his two companions. In those days, ' \
        'travellers were very shy of being confidential on a short notice, for anybody on the road might be a robber ' \
        'or in league with robbers. As to the latter, when every posting-house and ale-house could produce ' \
        'somebody in \"the Captain\'s\" pay, ranging from the landlord to the lowest stable non-descript, it was ' \
        'the likeliest thing upon the cards. So the guard of the Dover mail thought to himself, that Friday night ' \
        'in November, one thousand seven hundred and seventy-five, lumbering up Shooter\'s Hill, as he stood on his ' \
        'own particular perch behind the mail, beating his feet, and keeping an eye and a hand on the arm-chest before ' \
        'him, where a loaded blunderbuss lay at the top of six or eight loaded horse-pistols, deposited on a substratum ' \
        'of cutlass.'
    
    reply = fake_eip_instance.read_variable('TestString_Copy')
    print(reply)
    fake_eip_instance.write_variable('TestString_Copy', tale_of_two_cities_string_2)
    reply = fake_eip_instance.read_variable('TestString_Copy')
    print(reply)
    fake_eip_instance.write_variable('TestString_Copy', tale_of_two_cities_string_1)
    reply = fake_eip_instance.read_variable('TestString_Copy')
    print(reply)
    
    fake_eip_instance.close_explicit()