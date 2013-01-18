"""Test harness for checking ``jplephem`` against actual JPL results.

This test can be invoked with a simple::

    python -m jplephem.jpltest

"""
import numpy as np
import sys
from .ephem import Ephemeris

def testpo(ephemeris, testpo_path):
    """Compare the positions we calculate against those computed by the JPL."""
    lines = iter(open(testpo_path))

    while next(lines).strip() != 'EOT':
        continue

    successes = 0

    for line in lines:
        de, date, jed, target, center, number, value = [f(v) for f, v
            in zip((str, str, float, int, int, int, float), line.split())]

        if 14 <= target <= 15:
            r = _position(ephemeris, jed, target)
        else:
            tpos = _position(ephemeris, jed, target)
            cpos = _position(ephemeris, jed, center)
            r = (tpos - cpos) / ephemeris.AU

        delta = r[number - 1] - value
        if (target == 15 and number == 3):
            delta = delta / (0.23 * (jed - 2451545.0))
        elif (target == 15 and number == 6):
            delta = delta * 0.01 / (1.0 + (jed - 2451545.0) / 365.25)

        if abs(delta) >= 1e-13:
            print('%s %s %s->%s field %d' % (date, jed, center, target, number))
            print('  JPL result: %.15f' % value)
            print('  Our result: %.15f' % r[number - 1])
            print('    ERROR: difference = %s' % (delta,))

        successes += 1
        break

    print('  %d tests successful' % successes)


def _position(ephemeris, jed, target):
    """Compute position given a JPL test file target integer identifier."""

    if target == 12:
        return np.zeros(6)  # solar system barycenter is the origin

    c = ephemeris.compute

    if target == 1:
        return c('mercury', jed)
    if target == 2:
        return c('venus', jed)
    if target == 3:
        return c('earthmoon', jed) - c('moon', jed) * ephemeris.earth_share
    if target == 4:
        return c('mars', jed)
    if target == 5:
        return c('jupiter', jed)
    if target == 6:
        return c('saturn', jed)
    if target == 7:
        return c('uranus', jed)
    if target == 8:
        return c('neptune', jed)
    if target == 9:
        return c('pluto', jed)
    if target == 10:
        return c('earthmoon', jed) + c('moon', jed) * ephemeris.moon_share
    if target == 11:
        return c('sun', jed)
    #
    if target == 13:
        return c('earthmoon', jed)
    if target == 14:
        return c('nutations', jed)
    if target == 15:
        return c('librations', jed)


def test_all():
    for number in 405, 406, 422, 423:
        name = 'de%d' % number
        module = __import__(name)
        fname = 'ssd.jpl.nasa.gov/pub/eph/planets/ascii/de%d/testpo.%d' % (
            number, number)
        ephemeris = Ephemeris(module)
        print(name, 'AU = %s km' % (ephemeris.AU,))
        testpo(ephemeris, fname)


if __name__ == '__main__':
    try:
        test_all()
    except IOError as e:
        print >>sys.stderr, str(e)
        print >>sys.stderr, """
Cannot find the JPL "testpo" files against which this test suite
validates that the positions it generates are correct. To fetch them,
run these four commands in your current working directory:

    wget -r ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/de405/testpo.405
    wget -r ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/de406/testpo.406
    wget -r ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/de422/testpo.422
    wget -r ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/de423/testpo.423

These commands create a "ssd.jpl.nasa.gov" directory containing the
necessary files. When you are done running the tests, simply remove the
directory.
"""
        print(str(e))
        exit(1)