# cSpell:ignore
# pylint:disable=missing-function-docstring
import pytest

import numpy as np

import astropy.units as u

from kcexo.transit import Transit
from kcexo.calc.util import equal_times

from .fixture_stars_planets import obs, stars, planets, exoclock_json  # pylint:disable=unused-import


def compare_transit_times(transits: list, times: list, time_delta: u.Quantity["time"]) -> bool:
    td_sec = time_delta.to(u.s)
    for t1, t2 in zip(transits, times):
        assert equal_times(t1.pre_ingress, t2[0], td_sec)
        assert equal_times(t1.ingress, t2[1], td_sec)
        assert equal_times(t1.mid, t2[2], td_sec)
        assert equal_times(t1.egress, t2[3], td_sec)
        assert equal_times(t1.post_egress, t2[4], td_sec)

@pytest.mark.parametrize("star, transit_times, t12, mf_time, has_problems", stars)
def test_transit_t12_problems(star, transit_times, t12, mf_time, has_problems, obs):  # pylint:disable=redefined-outer-name
    observer = obs
    tran = Transit(transit_times[0], transit_times[1], 
                   transit_times[2], 
                   transit_times[3], transit_times[4],
                   t12,
                   star,
                   observer,
                   True)
    
    assert np.abs((tran.meridian_crossing - mf_time).to(u.min).value) < Transit.TRANSIT_MARGIN.to(u.min).value
    assert tran.problem_meridian_crossing == has_problems[0]
    assert tran.problem_twilight_astronomical == has_problems[1]
    assert tran.problem_twilight_nautical == has_problems[2]
    assert tran.problem_twilight_civil == has_problems[3]


@pytest.mark.parametrize("planet, start_time, end_time, expected_transits, expected_transits_sso", planets)
@pytest.mark.parametrize("sunset_only", [False, True])
def test_transit_transits(planet, start_time, end_time, expected_transits, expected_transits_sso, obs, sunset_only):  # pylint:disable=redefined-outer-name

    transits = planet.get_transits(start_time, end_time, obs, sunset_only)
    if sunset_only:
        compare_transit_times(transits, expected_transits_sso, Transit.TRANSIT_MARGIN)
    else:
        compare_transit_times(transits, expected_transits, Transit.TRANSIT_MARGIN)
