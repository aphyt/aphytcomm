__author__ = 'Joseph Ryan'
__license__ = "GPLv2"
__maintainer__ = "Joseph Ryan"
__email__ = "jr@aphyt.com"

from cip.cip_datatypes import *
import unittest


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
