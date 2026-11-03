#!/usr/bin/env python3
"""
node_info_env.py -- the reader for the WES-injected node identity.

This is the small piece of pywaggle2 that consumes the env vars the WES change
produces (via the `wes-identity` ConfigMap, EnvFrom-projected into every plugin pod).
It implements the sentinel->None normalization from the pywaggle2 design doc sec 2.2.3
(https://github.com/flint-pete/sage-design-planning/blob/master/pywaggle2-design.md) so
plugin authors never see 0/999/"" -- only real values or None.

Scope: this is ONLY the env-tier reader (Tier-1 static identity from env). Live GPS
(Tier-2, gpsd) and the curated node-info.json file fallback are separate; this module
is what proves the ~5 env vars are usable end-to-end once WES injects them.

Design contract (sec 2.2.3):
  VSN sentinel      : "0" (and "", missing)      -> None
  node_id sentinel  : "" / missing               -> None
  lat/lon sentinel  : by RANGE |lat|>90 |lon|>180 (covers the 999 sentinel and
                      any garbage); also "", missing, unparseable -> None
  mobility          : missing/"" -> "unknown"; else "static"/"mobile" passthrough

Manually merged into pywaggle repo from original source: https://github.com/flint-pete/pywaggle2-nodeinfo/blob/v0.1.2/tests/test_node_info_env.py
"""
import os
from typing import NamedTuple, Optional


class NodeInfo(NamedTuple):
    vsn: Optional[str]
    node_id: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    mobility: str            # "static" | "mobile" | "unknown" (never None)
    vsn_is_placeholder: bool


def _clean_str(v, sentinels=("",)):
    if v is None:
        return None
    v = v.strip()
    return None if v in sentinels else v


def _clean_coord(v, limit):
    """Return float in range, else None. Range check catches the 999 sentinel AND
    any off-globe garbage -- more robust than matching a literal (design sec 2.2.3)."""
    if v is None or v.strip() == "":
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if abs(f) <= limit else None


def read_node_info(env=None) -> NodeInfo:
    e = os.environ if env is None else env
    vsn = _clean_str(e.get("WAGGLE_NODE_VSN"), sentinels=("", "0"))
    node_id = _clean_str(e.get("WAGGLE_NODE_ID"))
    lat = _clean_coord(e.get("WAGGLE_NODE_GPS_LAT"), 90.0)
    lon = _clean_coord(e.get("WAGGLE_NODE_GPS_LON"), 180.0)
    mobility = _clean_str(e.get("WAGGLE_NODE_MOBILITY")) or "unknown"
    if mobility not in ("static", "mobile", "unknown"):
        mobility = "unknown"
    return NodeInfo(
        vsn=vsn,
        node_id=node_id,
        lat=lat,
        lon=lon,
        mobility=mobility,
        vsn_is_placeholder=(vsn is None),
    )


if __name__ == "__main__":
    import json
    ni = read_node_info()
    print(json.dumps(ni._asdict()))
