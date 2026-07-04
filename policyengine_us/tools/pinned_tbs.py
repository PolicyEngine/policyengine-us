"""Module-level cache of pinned tax-benefit systems (issue #8114).

The NY EITC/CTC formulas recompute the federal EITC/CTC with parameters
pinned to an earlier vintage (pre-ARPA 2020, pre-TCJA 2017). Cloning the
full tax-benefit system inside the formula deep-copies the entire
parameter tree and variable registry on every call; this cache builds each
pinned system once per process and reuses it across simulations.

The pinned system must be treated as read-only by all callers.
"""

import weakref

from policyengine_core.parameters import Parameter
from policyengine_core.periods import instant

# pin name -> (weakref to base TBS, pinned clone).
# The clone is held strongly so it survives across simulations; the
# weakref to the base is used to detect that the base system changed
# (e.g. a reformed system in another test), in which case the entry is
# rebuilt. Using a weakref (rather than id() alone) also guards against
# id reuse after the base system is garbage-collected.
_PINNED_TBS_CACHE = {}


def _get_pinned_tbs(base_tbs, pin_name, pin_fn):
    entry = _PINNED_TBS_CACHE.get(pin_name)
    if entry is not None and entry[0]() is base_tbs:
        return entry[1]
    pinned = base_tbs.clone()
    pin_fn(pinned)
    _PINNED_TBS_CACHE[pin_name] = (weakref.ref(base_tbs), pinned)
    return pinned


def _pin_pre_arpa_eitc(tbs):
    # NY decoupled from post-March 2020 IRC amendments for TY 2021:
    # pin the federal EITC parameters to their 2020 (pre-ARPA) values.
    pin_date = instant("2020-01-01")
    start = instant("2021-01-01")
    stop = instant("2021-12-31")
    for param in tbs.parameters.gov.irs.credits.eitc.get_descendants():
        if isinstance(param, Parameter):
            try:
                value = param(pin_date)
                param.update(start=start, stop=stop, value=value)
            except Exception:
                pass


def _pin_pre_tcja_ctc(tbs):
    # Pin the federal CTC parameters to their 2017 (pre-TCJA) values.
    for ctc_parameter in tbs.parameters.gov.irs.credits.ctc.get_descendants():
        if isinstance(ctc_parameter, Parameter):
            ctc_parameter.update(
                start=instant("2017-01-01"),
                stop=instant("2035-01-01"),
                value=ctc_parameter("2017-01-01"),
            )


def get_pre_arpa_eitc_tbs(base_tbs):
    """Pre-ARPA (2020-pinned) EITC system for NY's TY2021 decoupling."""
    return _get_pinned_tbs(base_tbs, "ny_pre_arpa_eitc", _pin_pre_arpa_eitc)


def get_pre_tcja_ctc_tbs(base_tbs):
    """Pre-TCJA (2017-pinned) CTC system for the NY Empire State Child Credit."""
    return _get_pinned_tbs(base_tbs, "ny_pre_tcja_ctc", _pin_pre_tcja_ctc)
