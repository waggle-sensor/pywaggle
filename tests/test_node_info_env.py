#!/usr/bin/env python3
"""Unit tests for the node-info env reader.

Manually merged into pywaggle repo from original source: https://github.com/flint-pete/pywaggle2-nodeinfo/blob/v0.1.2/tests/test_node_info_env.py
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from waggle.data.node_info_env import read_node_info, NodeInfo  # noqa: E402


# --- real values pass through -------------------------------------------------

def test_real_values_resolve():
    ni = read_node_info(env={
        "WAGGLE_NODE_VSN": "H00F",
        "WAGGLE_NODE_ID": "00004cbb4701d16c",
        "WAGGLE_NODE_GPS_LAT": "41.7179852752395",
        "WAGGLE_NODE_GPS_LON": "-87.98271513806043",
        "WAGGLE_NODE_MOBILITY": "static",
    })
    assert ni == NodeInfo(
        vsn="H00F", node_id="00004cbb4701d16c",
        lat=41.7179852752395, lon=-87.98271513806043,
        mobility="static", vsn_is_placeholder=False,
    )


def test_zero_is_a_real_coordinate_not_a_sentinel():
    # 0.0 is the equator/prime meridian -- must NOT be treated as missing.
    ni = read_node_info(env={"WAGGLE_NODE_GPS_LAT": "0", "WAGGLE_NODE_GPS_LON": "0"})
    assert ni.lat == 0.0 and ni.lon == 0.0


# --- vsn sentinels ------------------------------------------------------------

@pytest.mark.parametrize("raw", ["0", "", "   ", None])
def test_vsn_sentinels_to_none_and_placeholder(raw):
    env = {} if raw is None else {"WAGGLE_NODE_VSN": raw}
    ni = read_node_info(env=env)
    assert ni.vsn is None
    assert ni.vsn_is_placeholder is True


def test_vsn_v999_is_real_not_sentinel():
    # only bare "0" is the sentinel; a real (test) vsn like V999 passes through.
    ni = read_node_info(env={"WAGGLE_NODE_VSN": "V999"})
    assert ni.vsn == "V999" and ni.vsn_is_placeholder is False


# --- coord sentinels: range-based, catches 999 AND garbage --------------------

@pytest.mark.parametrize("lat,lon", [
    ("999", "999"),          # the explicit sentinel
    ("", ""),                # missing
    ("  ", "  "),            # whitespace
    ("nan", "not-a-number"), # unparseable
    ("91", "181"),           # just out of range -> garbage
])
def test_coord_sentinels_and_garbage_to_none(lat, lon):
    ni = read_node_info(env={"WAGGLE_NODE_GPS_LAT": lat, "WAGGLE_NODE_GPS_LON": lon})
    assert ni.lat is None and ni.lon is None


def test_coord_range_boundaries_inclusive():
    ni = read_node_info(env={"WAGGLE_NODE_GPS_LAT": "90", "WAGGLE_NODE_GPS_LON": "-180"})
    assert ni.lat == 90.0 and ni.lon == -180.0


def test_never_fabricate_coords_invariant():
    # The load-bearing rule: a plugin building an EXIF geotag must get None (and
    # OMIT the tag), never a bogus coordinate.
    ni = read_node_info(env={"WAGGLE_NODE_GPS_LAT": "999", "WAGGLE_NODE_GPS_LON": "999"})
    assert ni.lat is None and ni.lon is None


# --- node_id ------------------------------------------------------------------

@pytest.mark.parametrize("raw,expect", [("abc123", "abc123"), ("", None), ("  ", None)])
def test_node_id(raw, expect):
    assert read_node_info(env={"WAGGLE_NODE_ID": raw}).node_id == expect


# --- mobility tri-state (never None) ------------------------------------------

@pytest.mark.parametrize("raw,expect", [
    ("static", "static"),
    ("mobile", "mobile"),
    ("", "unknown"),
    ("   ", "unknown"),
    ("bogus", "unknown"),     # unrecognized -> conservative unknown, not passthrough
])
def test_mobility_tristate(raw, expect):
    assert read_node_info(env={"WAGGLE_NODE_MOBILITY": raw}).mobility == expect


def test_mobility_missing_is_unknown():
    assert read_node_info(env={}).mobility == "unknown"


# --- empty env: everything sentinel ------------------------------------------

def test_empty_env_all_none_but_mobility_unknown():
    ni = read_node_info(env={})
    assert ni == NodeInfo(vsn=None, node_id=None, lat=None, lon=None,
                          mobility="unknown", vsn_is_placeholder=True)


# --- reads os.environ when no env passed --------------------------------------

def test_defaults_to_os_environ(monkeypatch):
    monkeypatch.setenv("WAGGLE_NODE_VSN", "W042")
    monkeypatch.delenv("WAGGLE_NODE_ID", raising=False)
    assert read_node_info().vsn == "W042"
