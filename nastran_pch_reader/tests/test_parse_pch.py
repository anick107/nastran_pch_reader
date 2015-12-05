import unittest
import nastran_pch_reader


class TestStaticOutput(unittest.TestCase):
    def setUp(self):
        self.parser = nastran_pch_reader.PchParser('data/nsa_1012_ug.pch')

    def testSubcaseNumber(self):
        self.assertListEqual(self.parser.get_subcases(), [1, 2, 3])

    """
    check boundary values
    """
    def testValues(self):
        forces = self.parser.get_forces(1)
        self.assertListEqual(forces[66008947],
                             [-0.3086368,  -0.04711712, 0.0008220575, -8.683135e-06, 7.214578e-05, 9.478482e-05])

        forces = self.parser.get_forces(3)
        self.assertListEqual(forces[70256346],
                             [-5.520462E-02, -5.823757E-02, -2.389058E-02, 1.035513E-04, -1.877879E-04, -3.983908E-05])


class TestFrequencyResponseOutputSort1(unittest.TestCase):
    def setUp(self):
        self.parser = nastran_pch_reader.PchParser('data/sine_gyro.pch')

    def testSubcaseNumber(self):
        self.assertListEqual(self.parser.get_subcases(), [1, 2, 3])

    """
    check boundary values
    """
    def testValues(self):
        accelerations = self.parser.get_accelerations(1)
        self.assertEqual(abs(accelerations[3000001][0][0]), 4.064976E+00)

        accelerations = self.parser.get_accelerations(3)
        self.assertEqual(abs(accelerations[3000006][2276][2]), 1.000748E-02)

    def testNodes(self):
        accelerations = self.parser.get_accelerations(1)
        self.assertListEqual(sorted(accelerations.keys()), [3000001, 3000002, 3000003, 3000004, 3000005, 3000006])
        accelerations = self.parser.get_accelerations(2)
        self.assertListEqual(sorted(accelerations.keys()), [3000001, 3000002, 3000003, 3000004, 3000005, 3000006])
        accelerations = self.parser.get_accelerations(3)
        self.assertListEqual(sorted(accelerations.keys()), [3000001, 3000002, 3000003, 3000004, 3000005, 3000006])


class TestFrequencyResponseOutputSort2Displacement(unittest.TestCase):
    def setUp(self):
        self.parser = nastran_pch_reader.PchParser('data/SGEO_PFM_79_v08_sine_closures.pch')

    def testSubcaseNumber(self):
        self.assertListEqual(self.parser.get_subcases(), [1, 2, 3])

    """
    check boundary values
    """
    def testValues(self):
        displacements = self.parser.get_displacements(1)
        self.assertEqual(displacements[200001][0][0], -1.057051E-02 + 1j*8.361023E-06)

        displacements = self.parser.get_displacements(2)
        self.assertEqual(displacements[300002][4][1], -5.722504E-03 + 1j*1.270270E-05)

        displacements = self.parser.get_displacements(3)
        self.assertEqual(displacements[1252024][1482][5], 4.814706E-05 + 1j*-6.976266E-05)


if __name__ == '__main__':
    unittest.main()
