import unittest
import nastran_pch_reader


class TestStaticOutputNotImplemented(unittest.TestCase):
    def test_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            nastran_pch_reader.PchParser('test-data/sol101_not_implemented.pch')


class TestStaticOutput(unittest.TestCase):
    def setUp(self):
        self.parser = nastran_pch_reader.PchParser('test-data/sol101.pch')

    def test_subcases(self):
        self.assertListEqual(self.parser.get_subcases(), [100, 200, 300])

    def test_displacements(self):
        displacements_sc1 = self.parser.get_displacements(100)
        self.assertListEqual(displacements_sc1[2001],
                             [4.462737E-06, -1.781939E-06, 1.273970E-05, 2.820892E-04, 4.496019E-04, -6.605602E-05])

        displacements_sc3 = self.parser.get_displacements(300)
        self.assertListEqual(displacements_sc3[2019],
                             [2.042521E-06, -2.708797E-04, 1.606910E-03, 2.706233E-02,  2.130588E-04, 9.613780E-05])

    def test_mpcf(self):
        mpcf_sc3 = self.parser.get_mpcf(300)
        self.assertListEqual(mpcf_sc3[999999],
                             [-1.574110E-11, -1.004177E-10, 5.542533E+01, 3.391945E+00, 1.079242E-11, -3.451865E-12])

    def test_celas_force(self):
        force_sc3 = self.parser.get_forces(300)
        self.assertEqual(force_sc3[4002][0], -1.214054E+01)

    def test_spcf_and_mpcf(self):
        spcf_sc3 = self.parser.get_spcf(300)
        mpcf_sc3 = self.parser.get_mpcf(300)
        for i in range(6):
            self.assertAlmostEqual(spcf_sc3[999999][i], -mpcf_sc3[999999][i])


class TestFrequencyResponse(unittest.TestCase):
    def setUp(self):
        self.parser_sort1_ri = nastran_pch_reader.PchParser('test-data/sol111_sort1_real.pch')
        self.parser_sort2_ri = nastran_pch_reader.PchParser('test-data/sol111_sort2_real.pch')
        self.parser_sort1_mp = nastran_pch_reader.PchParser('test-data/sol111_sort1_phase.pch')
        self.parser_sort2_mp = nastran_pch_reader.PchParser('test-data/sol111_sort2_phase.pch')

    def test_subcases(self):
        self.assertEqual(self.parser_sort1_ri.get_subcases(), [1, 2, 3])
        self.assertEqual(self.parser_sort2_ri.get_subcases(), [1, 2, 3])
        self.assertEqual(self.parser_sort1_mp.get_subcases(), [1, 2, 3])
        self.assertEqual(self.parser_sort2_mp.get_subcases(), [1, 2, 3])

    def test_displacements_lower_bound(self):
        # node 2001
        # subcase 1
        # frequency = 5Hz
        displacement_2001_sc1 = [-9.939638E-03 + 1j*-1.075396E-09,
                                 2.198712E-08 + 1j*1.291198E-11,
                                 -1.270445E-07 + 1j*1.026846E-10,
                                 -2.518057E-06 + 1j*1.291944E-09,
                                 -3.480340E-06 + 1j*1.776345E-09,
                                 3.246033E-07 + 1j*-1.688139E-10]
        displacements_1 = self.parser_sort1_ri.get_displacements(1)
        displacements_2 = self.parser_sort2_ri.get_displacements(1)
        displacements_3 = self.parser_sort1_mp.get_displacements(1)
        displacements_4 = self.parser_sort2_mp.get_displacements(1)
        self.assertListAlmostEqual(displacements_1[2001][0], displacement_2001_sc1)
        self.assertListAlmostEqual(displacements_2[2001][0], displacement_2001_sc1)
        self.assertListAlmostEqual(displacements_3[2001][0], displacement_2001_sc1)
        self.assertListAlmostEqual(displacements_4[2001][0], displacement_2001_sc1)

    def test_displacements_upper_bound(self):
        # node 2019
        # subcase 3
        # frequency 300Hz
        displacement_2019_sc3 = [1.660987E-08 + 1j*-1.620602E-12,
                                 -9.562576E-07 + 1j*-1.649483E-08,
                                 2.037582E-06 + 1j*1.076404E-07,
                                 9.530941E-05 + 1j*1.651252E-06,
                                 2.126992E-06 + 1j*-5.775603E-09,
                                 7.811522E-07 + 1j*-4.473947E-11]
        displacements_1 = self.parser_sort1_ri.get_displacements(3)
        displacements_2 = self.parser_sort2_ri.get_displacements(3)
        displacements_3 = self.parser_sort1_mp.get_displacements(3)
        displacements_4 = self.parser_sort2_mp.get_displacements(3)
        self.assertListAlmostEqual(displacements_1[2019][295], displacement_2019_sc3)
        self.assertListAlmostEqual(displacements_2[2019][295], displacement_2019_sc3)
        self.assertListAlmostEqual(displacements_3[2019][295], displacement_2019_sc3)
        self.assertListAlmostEqual(displacements_4[2019][295], displacement_2019_sc3)

    def test_acceleration(self):
        # node 2019
        # subcase 3
        # frequency 300Hz
        accel_2019_sc3 = [-5.901583E-02 + 1j*5.758094E-06,
                          3.397639E+00 + 1j*5.860707E-02,
                          -7.239647E+00 + 1j*-3.824526E-01,
                          -3.386399E+02 + 1j*-5.866992E+00,
                          -7.557324E+00 + 1j*2.052105E-02,
                          -2.775479E+00 + 1j*1.589619E-04]
        accelerations_1 = self.parser_sort1_ri.get_accelerations(3)
        accelerations_2 = self.parser_sort2_ri.get_accelerations(3)
        accelerations_3 = self.parser_sort1_mp.get_accelerations(3)
        accelerations_4 = self.parser_sort2_mp.get_accelerations(3)
        self.assertListAlmostEqual(accelerations_1[2019][295], accel_2019_sc3)
        self.assertListAlmostEqual(accelerations_2[2019][295], accel_2019_sc3)
        self.assertListAlmostEqual(accelerations_3[2019][295], accel_2019_sc3)
        self.assertListAlmostEqual(accelerations_4[2019][295], accel_2019_sc3)

    def test_elforce_lower_bound(self):
        # element 3000
        # subcase 1
        # frequency 5Hz
        # compare FX
        forces_1 = self.parser_sort1_ri.get_forces(1)
        forces_2 = self.parser_sort2_ri.get_forces(1)
        forces_3 = self.parser_sort1_mp.get_forces(1)
        forces_4 = self.parser_sort2_mp.get_forces(1)
        value = 1.812245E-03 + 1j*-9.088075E-07
        self.assertAlmostEqual(forces_1[3000][0][0], value)
        self.assertAlmostEqual(forces_2[3000][0][0], value)
        self.assertAlmostEqual(forces_3[3000][0][0], value)
        self.assertAlmostEqual(forces_4[3000][0][0], value)

    def test_elforce_celas(self):
        # element 4002
        # subcase 3
        # frequency 300Hz
        # compare CELAS
        forces_1 = self.parser_sort1_ri.get_forces(3)
        forces_2 = self.parser_sort2_ri.get_forces(3)
        forces_3 = self.parser_sort1_mp.get_forces(3)
        forces_4 = self.parser_sort2_mp.get_forces(3)
        value = -2.556116E-02 + 1j*-1.003306E-03
        self.assertAlmostEqual(forces_1[4002][295][0], value)
        self.assertAlmostEqual(forces_2[4002][295][0], value)
        self.assertAlmostEqual(forces_3[4002][295][0], value)
        self.assertAlmostEqual(forces_4[4002][295][0], value)

    def assertListAlmostEqual(self, list1, list2, eps=1.0e-6):
        for a, b in zip(list1, list2):
            self.assertTrue(abs((a-b)/a) < eps)

    def test_frequencies(self):
        self.assertListAlmostEqual(self.parser_sort1_mp.get_frequencies(1), list(range(5, 301)))
        self.assertListAlmostEqual(self.parser_sort2_mp.get_frequencies(1), list(range(5, 301)))
        self.assertListAlmostEqual(self.parser_sort1_ri.get_frequencies(1), list(range(5, 301)))
        self.assertListAlmostEqual(self.parser_sort2_ri.get_frequencies(1), list(range(5, 301)))


if __name__ == '__main__':
    unittest.main()
