__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from aphyt.cip.cip_datatypes import *
from aphyt.eip import *
import unittest
from unittest.mock import Mock
from unittest.mock import patch


class TestCipDataTypes(unittest.TestCase):
    def test_cip_boolean_true(self):
        cip_boolean = CIPBoolean()
        cip_boolean.from_value(True)
        self.assertEqual(cip_boolean.data, b'\x01\x00')

    def test_cip_boolean_false(self):
        cip_boolean = CIPBoolean()
        cip_boolean.from_value(False)
        self.assertEqual(cip_boolean.data, b'\x00\x00')

    def test_cip_boolean_true_bytes(self):
        cip_boolean = CIPBoolean()
        cip_boolean.from_value(True)
        self.assertEqual(cip_boolean.value(), True)

    def test_cip_boolean_false_bytes(self):
        cip_boolean = CIPBoolean()
        cip_boolean.from_value(False)
        self.assertEqual(cip_boolean.value(), False)

    def test_cip_short_integer_low(self):
        cip_short_integer = CIPShortInteger()
        cip_short_integer.from_value(-128)
        self.assertEqual(cip_short_integer.data, b'\x80')

    def test_cip_short_integer_high(self):
        cip_short_integer = CIPShortInteger()
        cip_short_integer.from_value(127)
        self.assertEqual(cip_short_integer.data, b'\x7f')

    def test_cip_integer_low(self):
        cip_short_integer = CIPInteger()
        cip_short_integer.from_value(-32768)
        self.assertEqual(cip_short_integer.data, b'\x00\x80')

    def test_cip_integer_high(self):
        cip_integer = CIPInteger()
        cip_integer.from_value(32767)
        self.assertEqual(cip_integer.data, b'\xff\x7f')

    def test_cip_double_integer_low(self):
        cip_double_integer = CIPDoubleInteger()
        cip_double_integer.from_value(-2147483648)
        self.assertEqual(cip_double_integer.data, b'\x00\x00\x00\x80')

    def test_cip_double_integer_high(self):
        cip_double_integer = CIPDoubleInteger()
        cip_double_integer.from_value(2147483647)
        self.assertEqual(cip_double_integer.data, b'\xff\xff\xff\x7f')

    def test_cip_long_integer_low(self):
        cip_long_integer = CIPLongInteger()
        cip_long_integer.from_value(-9223372036854775808)
        self.assertEqual(cip_long_integer.data, b'\x00\x00\x00\x00\x00\x00\x00\x80')

    def test_cip_long_integer_high(self):
        cip_long_integer = CIPLongInteger()
        cip_long_integer.from_value(9223372036854775807)
        self.assertEqual(cip_long_integer.data, b'\xff\xff\xff\xff\xff\xff\xff\x7f')

    def test_cip_unsigned_short_integer_low(self):
        cip_short_integer = CIPUnsignedShortInteger()
        cip_short_integer.from_value(0)
        self.assertEqual(cip_short_integer.data, b'\x00')

    def test_cip_unsigned_short_integer_high(self):
        cip_short_integer = CIPUnsignedShortInteger()
        cip_short_integer.from_value(255)
        self.assertEqual(cip_short_integer.data, b'\xff')

    def test_cip_unsigned_integer_low(self):
        cip_short_integer = CIPUnsignedInteger()
        cip_short_integer.from_value(0)
        self.assertEqual(cip_short_integer.data, b'\x00\x00')

    def test_cip_unsigned_integer_high(self):
        cip_integer = CIPUnsignedInteger()
        cip_integer.from_value(65535)
        self.assertEqual(cip_integer.data, b'\xff\xff')

    def test_cip_unsigned_double_integer_low(self):
        cip_double_integer = CIPUnsignedDoubleInteger()
        cip_double_integer.from_value(0)
        self.assertEqual(cip_double_integer.data, b'\x00\x00\x00\x00')

    def test_cip_unsigned_double_integer_high(self):
        cip_double_integer = CIPUnsignedDoubleInteger()
        cip_double_integer.from_value(4294967295)
        self.assertEqual(cip_double_integer.data, b'\xff\xff\xff\xff')

    def test_cip_unsigned_long_integer_low(self):
        cip_long_integer = CIPUnsignedLongInteger()
        cip_long_integer.from_value(0)
        self.assertEqual(cip_long_integer.data, b'\x00\x00\x00\x00\x00\x00\x00\x00')

    def test_cip_unsigned_long_integer_high(self):
        cip_long_integer = CIPUnsignedLongInteger()
        cip_long_integer.from_value(18446744073709551615)
        self.assertEqual(cip_long_integer.data, b'\xff\xff\xff\xff\xff\xff\xff\xff')

    def test_cip_real_zero(self):
        cip_real = CIPReal()
        cip_real.data = b'\x00\x00\x00\x00'
        self.assertAlmostEqual(cip_real.value(), 0.0)

    def test_cip_real_low(self):
        cip_real = CIPReal()
        cip_real.data = b'\xff\xff\x7f\xff'
        self.assertAlmostEqual(cip_real.value(), -3.4028234663852886e+38)

    def test_cip_real_high(self):
        cip_real = CIPReal()
        cip_real.data = b'\xff\xff\x7f\x7f'
        self.assertAlmostEqual(cip_real.value(), 3.4028234663852886e+38)

    def test_eip_commands(self):
        eip_test = EIPConnectedCIPDispatcher()
        eip_test.send_command = Mock()
        eip_test.list_services('')
        args = eip_test.send_command.call_args
        self.assertEqual(args.args[0].bytes(),
                         b'\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
                         b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    def test_structure(self):
        cip_structure = CIPStructure()
        cip_structure.variable_name = "Yes"
        cip_structure.variable_type_name = 'LREALisREAL'
        cip_structure.add_member('lreal_member', CIPLongReal())
        cip_structure['lreal_member'] = 34.12121212
        self.assertEqual(cip_structure.data, b'\xb1\xa3\xf5\xe0\x83\x0fA@')

    def test_structure2(self):
        cip_structure = CIPStructure()
        cip_structure.variable_name = "Yes"
        cip_structure.variable_type_name = 'LREALisREAL'
        cip_structure.add_member('lreal_member', CIPLongReal())
        cip_structure['lreal_member'].data = b'\xb1\xa3\xf5\xe0\x83\x0fA@'
        self.assertAlmostEqual(cip_structure['lreal_member'].value(), 34.12121212)

    def test_structure3(self):
        """
        Given a CIPStructure, a variable is updated, the structure data must be updated accordingly.
        """
        cip_structure = CIPStructure()
        cip_structure.variable_name = "Yes"
        cip_structure.variable_type_name = 'YesType'
        cip_structure.add_member('bool_1', CIPBoolean())
        cip_structure['bool_1'] = True
        cip_structure.add_member('bool_2', CIPBoolean())
        cip_structure['bool_2'] = False
        cip_structure.add_member('bool_3', CIPBoolean())
        cip_structure['bool_3'] = True

        self.assertEqual(cip_structure.data, b'\x01\x00\x00\x00\x01\x00')  # This is just to be sure

        cip_structure['bool_3'] = False

        self.assertEqual(cip_structure.data, b'\x01\x00\x00\x00\x00\x00')  # This is the real test assert

    def test_structure_contents_update_updates_data(self):
        """

        Given a CIPStructure, a variable is updated, the structure data must be updated accordingly.

        """
        cip_structure = CIPStructure()
        cip_structure.variable_name = "Yes"
        cip_structure.variable_type_name = 'LREALisREAL'
        cip_structure.add_member('lreal_member', CIPLongReal())
        cip_structure['lreal_member'] = 0.00123

        self.assertEqual(cip_structure.data, b'\xd7\x86\x8a\x71\xfe\x26\x54\x3f')  # This is just to be sure

        cip_structure['lreal_member'] = 34.12121212

        self.assertEqual(cip_structure.data, b'\xb1\xa3\xf5\xe0\x83\x0fA@')  # This is the real test assert

    def test_structure_with_structure_inside(self):
        """

        Given a CIPStructure that has a CIPStructure inside, the structure data must exist.

        """
        cip_structure = CIPStructure()
        cip_structure.size = 6
        cip_structure.variable_name = "outer_struct"
        cip_structure.variable_type_name = 'OuterStruct'

        inner_struct_key = 'inner_struct'
        cip_structure.add_member(inner_struct_key, CIPStructure())
        cip_structure[inner_struct_key].size = 6
        cip_structure[inner_struct_key].variable_type_name = 'StructWithBoolsInside'
        cip_structure[inner_struct_key].add_member('bool_1', CIPBoolean())
        cip_structure[inner_struct_key]['bool_1'] = False
        cip_structure[inner_struct_key].add_member('bool_2', CIPBoolean())
        cip_structure[inner_struct_key]['bool_2'] = True
        cip_structure[inner_struct_key].add_member('bool_3', CIPBoolean())
        cip_structure[inner_struct_key]['bool_3'] = False

        cip_structure.from_value(cip_structure)
        print(f"{cip_structure=}")
        # output -> cip_structure=outer_struct { type: OuterStruct | members: {'inner_struct':
        # { type: StructWithBoolsInside | members: {'bool_1': False, 'bool_2': True, 'bool_3': False} }} }

        print(f'before {binascii.hexlify(cip_structure.data, "-")=}')
        # output -> before binascii.hexlify(cip_structure.data, "-")=b''

        cip_structure.from_value(cip_structure)  # are we supposed to do this to update cip_structure.data ?

        print(f'after {binascii.hexlify(cip_structure.data, "-")=}')
        # output -> after binascii.hexlify(cip_structure.data, "-")=b'00-00-01-00-00-00'

        self.assertEqual(cip_structure.data, b'\x00\x00\x01\x00\x00\x00')  # This is just to be sure

        cip_structure[inner_struct_key]['bool_3'] = True

        # Using the following line does not work, neither using it (but gives different result).
        cip_structure.from_value(cip_structure)  # are we supposed to do this to update cip_structure.data ?

        self.assertEqual(cip_structure.data, b'\x00\x00\x01\x00\x01\x00')  # This is the real test assert
