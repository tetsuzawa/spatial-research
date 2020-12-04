# coding: utf-8

import re


class FormatError(Exception):
    pass


class TLE:
    def __init__(self, tle: str):
        tle_lines = tle.splitlines()

        if len(tle_lines) != 3:
            raise FormatError(
                f"the argument must be 3-line string conforms to the NASA TLE format. got: {len(tle_lines)}-line")

        # satellite name
        sat_name = tle_lines[0]
        if len(sat_name) > 24:
            raise FormatError(
                f"the length of satellite name must be in 24. got length: {len(sat_name)}. got name: {sat_name}")
        self.sat_name = sat_name

        # line 1
        line_1 = tle_lines[1]
        if len(line_1) != 69:
            raise FormatError(
                f"the number of characters in the line 1 must be 69. got number: {len(line_1)}, got: {line_1}")
        # check the line number
        if line_1[0] != "1":
            raise FormatError(f"the line number in line 1 must be 1. got: {line_1[0]}")

        # checksum
        checksum = int(line_1[68])
        sum = 0
        for s in line_1[:68]:
            if re.match("\d", s):
                sum += int(s)
            elif s == "-":
                sum += 1
        if sum % 10 != checksum:
            raise FormatError(f"checksum error in line 1. want: {sum % 10}, got: {checksum}")

        self.sat_number = line_1[2:7].strip()
        self.classification = line_1[7]
        self.launch_year = line_1[9:11]
        self.launch_number_of_the_year = line_1[11:14]
        self.piece_of_the_launch = line_1[14:17].strip()
        self.epoch_year = line_1[18:20]
        self.epoch = line_1[20:32].strip()
        self.first_derivative_of_mean_motion = line_1[33:43].strip()
        self.second_derivative_of_mean_motion = line_1[45:52].strip()
        self.BSTAR = line_1[53:61].strip()
        self.ephemeris_type = line_1[62]
        self.element_set_number = line_1[64:68].strip()

        # line 2
        line_2 = tle_lines[2]
        if len(line_1) != 69:
            raise FormatError(
                f"the number of characters in the line 2 must be 69. got number: {len(line_2)}, got: {line_2}")
        # check the line number
        if line_2[0] != "2":
            raise FormatError(f"the line number in line 2 must be 2. got: {line_2[0]}")

        # checksum
        checksum = int(line_2[68])
        sum = 0
        for s in line_2[:68]:
            if re.match("\d", s):
                sum += int(s)
            elif s == "-":
                sum += 1
        if sum % 10 != checksum:
            raise FormatError(f"checksum error in line 2. want: {sum % 10}, got: {checksum}")

        self.inclination = line_2[8:16].strip()
        self.right_ascension_of_the_ascending_node = line_2[17:25].strip()
        self.eccentricity = line_2[26:33].strip()
        self.argument_of_perigee = line_2[34:42].strip()
        self.mean_anomaly = line_2[43:51].strip()
        self.mean_motion = line_2[52:63].strip()
        self.revolution_number_at_epoch = line_2[63:68].strip()
