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

# pin name -> (weakref to base TBS, weakref to its parameter tree, pinned clone).
# The clone is held strongly so it survives across simulations; the
# weakref to the base is used to detect that the base system changed
# (e.g. a reformed system in another test), in which case the entry is
# rebuilt. Using a weakref (rather than id() alone) also guards against
# id reuse after the base system is garbage-collected.
#
# The parameter tree is tracked separately because a shared-policy system
# keeps its identity while swapping its tree: a reform detaches a private
# copy in place (see policyengine_us.spm.SharedParameterPolicy), so a pin
# built before that reform would otherwise be reused after it.
_PINNED_TBS_CACHE = {}


def _get_pinned_tbs(base_tbs, pin_name, pin_fn):
    entry = _PINNED_TBS_CACHE.get(pin_name)
    parameters = base_tbs.parameters
    if entry is not None and entry[0]() is base_tbs and entry[1]() is parameters:
        return entry[2]
    pinned = base_tbs.clone()
    pin_fn(pinned)
    _PINNED_TBS_CACHE[pin_name] = (
        weakref.ref(base_tbs),
        weakref.ref(parameters),
        pinned,
    )
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


def _pin_2020_irc(tbs):
    # Alabama Act 2022-37 (HB 231) recomputes the federal Child Tax Credit,
    # Child and Dependent Care Credit, and Earned Income Credit "as if the
    # individual paid the federal income tax that would otherwise have been
    # paid under the provisions of the Internal Revenue Code in effect on
    # December 31, 2020," using the current-year information. This applied only
    # to tax year 2021 (the one-year ARPA expansion); the 2022+ Alabama
    # worksheets are Part I only. Pin those three credits' parameters to their
    # 2020 vintage for TY2021.
    pin_date = instant("2020-01-01")
    start = instant("2021-01-01")
    stop = instant("2021-12-31")
    credits = tbs.parameters.gov.irs.credits
    for subtree in (credits.eitc, credits.ctc, credits.cdcc):
        for param in subtree.get_descendants():
            if isinstance(param, Parameter):
                try:
                    param.update(start=start, stop=stop, value=param(pin_date))
                except Exception:
                    pass
    # ARPA added the CDCC to the list of refundable credits in 2021; restore the
    # 2020 membership so the recomputed CDCC is non-refundable (limited by tax).
    try:
        credits.refundable.update(
            start=start, stop=stop, value=credits.refundable(pin_date)
        )
    except Exception:
        pass
    # The 2020 CTC & ODC Worksheet (Pub. 972, p.7) uses the CDCC before the CTC
    # when computing the CTC's tax-liability limit, so the recomputed CDCC must
    # reduce that limit inside `ctc_limiting_tax_liability`, which reads the
    # non-refundable-credits list. The 2021 list omits `cdcc` (it was refundable
    # under ARPA). Add `cdcc` to the current 2021 membership rather than pinning
    # the whole 2020 list, which would drop `new_clean_vehicle_credit` (2021+).
    try:
        non_refundable_2021 = list(credits.non_refundable(start))
        if "cdcc" not in non_refundable_2021:
            non_refundable_2021 = ["cdcc"] + non_refundable_2021
        credits.non_refundable.update(start=start, stop=stop, value=non_refundable_2021)
    except Exception:
        pass


def get_pre_arpa_eitc_tbs(base_tbs):
    """Pre-ARPA (2020-pinned) EITC system for NY's TY2021 decoupling."""
    return _get_pinned_tbs(base_tbs, "ny_pre_arpa_eitc", _pin_pre_arpa_eitc)


def get_2020_irc_tbs(base_tbs):
    """2020-IRC-pinned EITC/CTC/CDCC system for Alabama's Act 2022-37 recompute."""
    return _get_pinned_tbs(base_tbs, "al_2020_irc", _pin_2020_irc)


def get_pre_tcja_ctc_tbs(base_tbs):
    """Pre-TCJA (2017-pinned) CTC system for the NY Empire State Child Credit."""
    return _get_pinned_tbs(base_tbs, "ny_pre_tcja_ctc", _pin_pre_tcja_ctc)
