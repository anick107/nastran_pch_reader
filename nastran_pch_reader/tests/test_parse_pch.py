import unittest
import parse_pch


class TestStaticOutput(unittest.TestCase):
    def setUp(self):
        parser = parse_pch.PchParser('tests/nsa_1012_ug.pch')
        self.data = parser.get_data()

    def tearDown(self):
        del self.data

    def testSubcaseNumber(self):
        self.assertListEqual(sorted(self.data['ELEMENT FORCES'].keys()), [1, 2, 3])

    """
    check boundary values
    """
    def testValues(self):
        self.assertDictEqual(self.data['ELEMENT FORCES'][1][66008947],
                             {
                                 'FX': -0.3086368,
                                 'FY': -0.04711712,
                                 'FZ': 0.0008220575,
                                 'MX': -8.683135e-06,
                                 'MY': 7.214578e-05,
                                 'MZ': 9.478482e-05
                             })

        self.assertDictEqual(self.data['ELEMENT FORCES'][3][70256346],
                             {
                                 'FX': -5.520462E-02,
                                 'FY': -5.823757E-02,
                                 'FZ': -2.389058E-02,
                                 'MX': 1.035513E-04,
                                 'MY': -1.877879E-04,
                                 'MZ': -3.983908E-05
                             })


class TestFrequencyResponseOutputSort1(unittest.TestCase):
    def setUp(self):
        parser = parse_pch.PchParser('tests/sine_gyro.pch')
        self.data = parser.get_data()

    def tearDown(self):
        del self.data

    def testSubcaseNumber(self):
        self.assertListEqual(sorted(self.data['ACCELERATION'].keys()), [1, 2, 3])

    """
    check boundary values
    """
    def testValues(self):
        self.assertEqual(abs(self.data['ACCELERATION'][1][3000001][0.2000000E+02]['TX']), 4.064976E+00)
        self.assertEqual(abs(self.data['ACCELERATION'][3][3000006][0.2000000E+04]['TZ']), 1.000748E-02)

    def testNodes(self):
        self.assertListEqual(sorted(self.data['ACCELERATION'][1].keys()), [3000001, 3000002, 3000003, 3000004, 3000005, 3000006])
        self.assertListEqual(sorted(self.data['ACCELERATION'][2].keys()), [3000001, 3000002, 3000003, 3000004, 3000005, 3000006])
        self.assertListEqual(sorted(self.data['ACCELERATION'][3].keys()), [3000001, 3000002, 3000003, 3000004, 3000005, 3000006])

class TestFrequencyResponseOutputSort2Displacement(unittest.TestCase):
    def setUp(self):
        parser = parse_pch.PchParser('tests/SGEO_PFM_79_v08_sine_closures.pch')
        self.data = parser.get_data()

    def tearDown(self):
        del self.data

    def testSubcaseNumber(self):
        self.assertListEqual(sorted(self.data['DISPLACEMENTS'].keys()), [1, 2, 3])

    """
    check boundary values
    """
    def testValues(self):
        self.assertEqual(self.data['DISPLACEMENTS'][1][200001][5.000000E+00]['TX'], -1.057051E-02 + 1j*8.361023E-06)
        self.assertEqual(self.data['DISPLACEMENTS'][2][300002][7.000000E+00]['TY'], -5.722504E-03 + 1j*1.270270E-05)
        self.assertEqual(self.data['DISPLACEMENTS'][3][1252024][1.000000E+02]['RZ'], 4.814706E-05 + 1j*-6.976266E-05)


if __name__ == '__main__':
    unittest.main()
