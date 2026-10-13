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

# Variables without "ctc", "cdcc" or "eitc" in their names that read those
# credits, so a branch that recomputes them under pinned rules must drop these
# too. The residential clean energy credit's limit subtracts the
# non-refundable CTC (26 U.S.C. 25D(c); Form 5695, line 14 worksheet).
CREDIT_DEPENDENT_VARIABLES = ("residential_clean_energy_credit",)

# Variables without "ctc", "cdcc" or "eitc" in their names that the 2020-IRC
# pin changes and the pinned credits read, so the Alabama branch must
# recompute them too. The IRC section 129 exclusion reduces the CDCC's
# section 21(c) dollar limit (Form 2441 Part III, line 28).
IRC_2020_RECOMPUTED_VARIABLES = ("dependent_care_assistance_exclusion",)


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
    # NY decoupled from IRC changes made after March 1, 2020 (ARPA) for
    # TY 2021, but not from the 2021 inflation adjustments, which Rev. Proc.
    # 2020-45 published before ARPA. Pin the federal EITC rules to their 2020
    # (pre-ARPA) values, then restore the inflation-indexed 2021 amounts, with
    # the pre-ARPA childless amounts in place of ARPA's.
    pin_date = instant("2020-01-01")
    start = instant("2021-01-01")
    stop = instant("2021-12-31")
    eitc = tbs.parameters.gov.irs.credits.eitc
    indexed_scales = (eitc.max, eitc.phase_out.start, eitc.phase_out.joint_bonus)
    indexed_2021 = [
        [bracket.amount(start) for bracket in scale.brackets]
        for scale in indexed_scales
    ]
    for param in eitc.get_descendants():
        if isinstance(param, Parameter):
            try:
                value = param(pin_date)
                param.update(start=start, stop=stop, value=value)
            except Exception:
                pass
    for scale, amounts in zip(indexed_scales, indexed_2021):
        for bracket, amount in zip(scale.brackets, amounts):
            bracket.amount.update(start=start, stop=stop, value=amount)
    pre_arpa = tbs.parameters.gov.states.ny.tax.income.credits.eitc.pre_arpa
    eitc.max.brackets[0].amount.update(
        start=start, stop=stop, value=pre_arpa.childless_max(start)
    )
    eitc.phase_out.start.brackets[0].amount.update(
        start=start, stop=stop, value=pre_arpa.childless_phase_out_start(start)
    )


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
    # The section 21(c) limit is reduced by the amount excludable under
    # section 129, so the 2020-rule CDCC also uses the 2020 section 129 cap:
    # $5,000 ($2,500), not the $10,500 ($5,250) that ARPA section 9632 set for
    # 2021. The worksheet recomputes the credit "based on 2020 Form 2441 Line
    # 11", and line 21 of the 2020 form enters $5,000.
    pin_date = instant("2020-01-01")
    start = instant("2021-01-01")
    stop = instant("2021-12-31")
    credits = tbs.parameters.gov.irs.credits
    dependent_care_assistance = (
        tbs.parameters.gov.irs.gross_income.dependent_care_assistance_programs
    )
    for subtree in (
        credits.eitc,
        credits.ctc,
        credits.cdcc,
        dependent_care_assistance,
    ):
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
    # The 2020 credit limit worksheets (e.g. the CTC & ODC Worksheet, Pub. 972,
    # p.7) subtract the CDCC from tax before every credit but the foreign tax
    # credit, so the recomputed CDCC must reduce each later credit's limit and
    # count among the non-refundable credits. The 2021 lists omit `cdcc` (it
    # was refundable under ARPA). Add `cdcc` after the foreign tax credit in
    # each current 2021 list whose 2020 version had it, rather than pinning
    # the whole 2020 lists, which would drop `new_clean_vehicle_credit` (2021+).
    credit_lists = [credits.non_refundable] + [
        param
        for param in credits.get_descendants()
        if isinstance(param, Parameter) and param.name.endswith(".preceding_credits")
    ]
    for credit_list in credit_lists:
        try:
            members_2021 = list(credit_list(start))
            if "cdcc" in credit_list(pin_date) and "cdcc" not in members_2021:
                position = (
                    members_2021.index("foreign_tax_credit") + 1
                    if "foreign_tax_credit" in members_2021
                    else 0
                )
                members_2021.insert(position, "cdcc")
            credit_list.update(start=start, stop=stop, value=members_2021)
        except Exception:
            pass


def get_pre_arpa_eitc_tbs(base_tbs):
    """Pre-ARPA EITC system (2021 inflation amounts) for NY's TY2021 decoupling."""
    return _get_pinned_tbs(base_tbs, "ny_pre_arpa_eitc", _pin_pre_arpa_eitc)


def get_2020_irc_tbs(base_tbs):
    """2020-IRC-pinned EITC/CTC/CDCC (and section 129 cap) system for Alabama's
    Act 2022-37 recompute."""
    return _get_pinned_tbs(base_tbs, "al_2020_irc", _pin_2020_irc)


def get_pre_tcja_ctc_tbs(base_tbs):
    """Pre-TCJA (2017-pinned) CTC system for the NY Empire State Child Credit."""
    return _get_pinned_tbs(base_tbs, "ny_pre_tcja_ctc", _pin_pre_tcja_ctc)
