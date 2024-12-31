from dataclasses import dataclass

import utils.unix_millis as unix_millis
import unittest


class TestUnixMillis(unittest.TestCase):
    def test_millis_e2e_now(self):
        now = unix_millis.current_time_millis()
        dt = unix_millis.millis_to_datetime(now)
        now_again = unix_millis.iso_to_millis(dt.isoformat())

        self.assertEquals(now, now_again)

    def test_millis_e2e_known_time_from_rfc3339(self):

        # -4 is the correct offset for America/Detroit in February
        known_time_rfc3339 = "2024-04-01T16:08:10+00:00"
        t1 = unix_millis.iso_to_millis(known_time_rfc3339)
        dt = unix_millis.millis_to_datetime(t1)
        t2 = unix_millis.iso_to_millis(dt.isoformat())

        self.assertEquals(t1, t2)

    def test_millis_e2e_known_time_from_millis(self):
        # From RFC3330:
        known_time_millis = 1711987690000
        dt = unix_millis.millis_to_datetime(known_time_millis)
        t = unix_millis.iso_to_millis(dt.isoformat())
        self.assertEquals(known_time_millis, t)

    def test_rfc3339_to_millis(self):
        @dataclass
        class TestCase:
            name: str
            input: str
            expected: int

        testcases = [
            TestCase(name="GMT", input="2024-04-01T16:08:10+00:00", expected=1711987690000),
            TestCase(name="GMT no colon", input="2024-04-01T16:08:10+0000", expected=1711987690000),
            TestCase(name="GMTZ", input="2024-04-01T16:08:10Z", expected=1711987690000),
            TestCase(name="America/Detroit", input="2024-04-01T12:08:10-04:00", expected=1711987690000),
            TestCase(name="America/Detroit + millis", input="2024-04-01T12:08:10.000000-04:00", expected=1711987690000),
        ]

        for case in testcases:
            actual = unix_millis.iso_to_millis(case.input)
            self.assertEqual(
                case.expected,
                actual,
                'failed test {} expected {}, actual {}'.format(
                    case.name, case.expected, actual
                ),
            )