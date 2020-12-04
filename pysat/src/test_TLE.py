# coding: utf-8

import unittest

import TLE


class TLETest(unittest.TestCase):
    def test_init(self):
        tle_str = ("ISS (ZARYA)\n"
                   "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927\n"
                   "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537\n"
                   )

        tle = TLE.TLE(tle_str)
        self.assertEqual("25544", tle.sat_number)
        self.assertEqual("U", tle.classification)
        self.assertEqual("98", tle.launch_year)
        self.assertEqual("067", tle.launch_number_of_the_year)
        self.assertEqual("A", tle.piece_of_the_launch)
        self.assertEqual("08", tle.epoch_year)
        self.assertEqual("264.51782528", tle.epoch)
        self.assertEqual(-0.00002182, tle.first_derivative_of_mean_motion)
        self.assertEqual(0., tle.second_derivative_of_mean_motion)
        self.assertEqual(-0.11606e-4, tle.BSTAR)
        self.assertEqual(0, tle.ephemeris_type)
        self.assertEqual(292, tle.element_set_number)
        self.assertEqual(51.6416, tle.inclination)
        self.assertEqual(247.4627, tle.right_ascension_of_the_ascending_node)
        self.assertEqual(0.0006703, tle.eccentricity)
        self.assertEqual(130.5360, tle.argument_of_perigee)
        self.assertEqual(325.0288, tle.mean_anomaly)
        self.assertEqual(15.72125391, tle.mean_motion)
        self.assertEqual(56353, tle.revolution_number_at_epoch)


if __name__ == '__main__':
    unittest.main()
