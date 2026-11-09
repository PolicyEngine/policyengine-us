"""State benefit programs count Railroad Retirement Act benefits as income.

Each row names an income list or variable, the rule that reaches railroad
retirement benefits, and the variable that reads the list. A rule reaches the
benefits by naming them, by counting pensions, annuities or retirement
benefits, or by counting all income it doesn't exclude.

Invariants, for every program below and any benefit amount:

- R1: railroad benefits raise the program's income by the amount received, at
  the variable's period, as the program's own sources do. Where the income
  total also counts cash aid that the same benefit reduces, the test holds that
  aid at zero, so the row isolates the income list from the aid's own income test.
- R2: the same dollars count the same whether a person receives them as
  railroad benefits or as a pension, for programs that list pensions.
"""

from functools import lru_cache

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEAR = 2026
MONTH = "2026-06"

# (state, variable, rule)
PROGRAMS = [
    ("AK", "ak_ccap_countable_unearned_income", "CCAP manual 4080-3(1)"),
    ("AL", "al_ccsp_countable_income", "FFY 2025-2027 CCDF plan"),
    ("AR", "ar_sra_countable_income", "FFY 2025-2027 CCDF plan"),
    ("CA", "ca_child_care_countable_income", "5 CCR 18078"),
    ("CA", "ca_tanf_other_unearned_income", "CalWORKs EAS 44-113.3"),
    ("CA", "ca_cpuc_countable_income", "CARE and FERA application"),
    ("CO", "co_ccap_countable_income", "8 CCR 1403-1"),
    ("CO", "co_tanf_countable_gross_unearned_income", "9 CCR 2503-6 3.605"),
    ("CT", "ct_c4k_countable_income", "RCSA 17b-749 definitions"),
    ("DC", "dc_ccsp_countable_income", "CCSP policy manual 2.5.2"),
    ("DC", "dc_tanf_gross_unearned_income", "D.C. Code 4-205.05"),
    ("DE", "de_poc_countable_income", "16 Del. Admin. Code 11003"),
    ("FL", "fl_sr_countable_income", "Fla. Admin. Code 6M-4.200"),
    ("GA", "ga_caps_countable_income", "CAPS policy manual"),
    ("ID", "id_iccp_countable_income", "IDAPA 16.06.12"),
    ("IL", "il_aabd_gross_unearned_income", "89 Ill. Adm. Code 113.100"),
    ("IL", "il_tanf_gross_unearned_income", "89 Ill. Adm. Code 112.100"),
    ("IL", "il_hbwd_countable_unearned_income", "89 Ill. Adm. Code 120.330"),
    ("IL", "il_isbe_countable_income", "ISBE household income form"),
    ("KS", "ks_ccap_countable_income", "KEESM 6200"),
    ("KS", "ks_liheap_countable_unearned_income", "KEESM 13361"),
    ("KY", "ky_ccap_countable_income", "922 KAR 2:160"),
    ("MA", "ma_tcap_gross_unearned_income", "106 CMR 704.210(B)"),
    ("MD", "md_ccs_countable_income", "COMAR 13A.14.06.02"),
    ("ME", "me_ccap_countable_income", "CCAP rule"),
    ("ME", "me_tanf_gross_unearned_income", "10-144 C.M.R. ch. 331"),
    ("MI", "mi_ccap_countable_income", "BEM 503"),
    ("MN", "mn_ccap_gross_unearned_income", "Minn. Stat. 256P.06"),
    ("MN", "mn_mfip_gross_unearned_income", "Minn. Stat. 256P.06"),
    ("MO", "mo_ccs_countable_income", "5 CSR 25-200.050"),
    ("MO", "mo_snc_countable_income", "SNC manual 0610.005"),
    ("MS", "ms_ccpp_countable_income", "CCPP policy manual"),
    ("MT", "mt_tanf_gross_unearned_income_person", "TANF manual 501-1"),
    ("NC", "nc_lieap_gross_income_person", "EP-300 300.09 and FNS 300.01 B"),
    ("NC", "nc_tanf_countable_gross_unearned_income", "WF-114"),
    ("ND", "nd_tanf_gross_unearned_income", "Manual 400-19-55-20-15"),
    ("NH", "nh_ccap_countable_income", "He-C 6910.06"),
    ("NJ", "nj_liheap_countable_income_person", "LIHEAP handbook 2.3.D"),
    ("NJ", "nj_ccap_countable_income", "FFY 2025-2027 CCDF plan"),
    ("NV", "nv_ccdp_countable_income", "Child care manual 306"),
    ("OK", "ok_ccs_gross_income", "OAC 340:40-7-11(c)(2)"),
    ("RI", "ri_ccap_countable_income", "218-RICR-20-00-4"),
    ("SC", "sc_ccap_countable_income", "CCS policy manual"),
    ("TX", "tx_fpp_countable_unearned_income", "FPP manual 9000"),
    ("TX", "tx_ceap_countable_income_person", "10 TAC 6.4"),
    ("VA", "va_ccsp_countable_income", "8 VAC 20-790-40(H)"),
    ("VT", "vt_ccfap_countable_income", "CCFAP regulations"),
    ("WA", "wa_wccc_countable_income", "WAC 110-15-0060(8)"),
    ("WI", "wi_shares_countable_income", "Wisconsin Shares handbook"),
    ("WV", "wv_ccap_countable_income", "Child care policy 5.2.4"),
    ("WY", "wy_power_gross_unearned_income", "SNAP and POWER manual"),
]


# These totals count CalWORKs cash aid (ca_tanf and tanf), and CalWORKs counts
# railroad benefits as other unearned income, so each dollar of benefits removes
# a dollar of aid from a household on the program. Wages above the CalWORKs limit
# keep the aid at zero with and without the benefit.
BASE_INPUTS = {
    "ca_child_care_countable_income": {"employment_income": 60_000},
    "ca_cpuc_countable_income": {"employment_income": 60_000},
}


def household(state, inputs):
    """A single 40-year-old parent with one child, as every program's rules apply."""
    people = {
        "parent": {"age": {YEAR: 40}, **{k: {YEAR: v} for k, v in inputs.items()}},
        "child": {"age": {YEAR: 5}},
    }
    members = list(people)
    return {
        "people": people,
        "tax_units": {"tax_unit": {"members": members}},
        "families": {"family": {"members": members}},
        "marital_units": {
            "parent_unit": {"members": ["parent"]},
            "child_unit": {"members": ["child"]},
        },
        "spm_units": {"spm_unit": {"members": members}},
        "households": {"household": {"members": members, "state_code": {YEAR: state}}},
    }


def income(state, variable, inputs):
    """The program's income for the parent, at the variable's own period."""
    period = YEAR if system.variables[variable].definition_period == "year" else MONTH
    situation = household(state, {**BASE_INPUTS.get(variable, {}), **inputs})
    values = Simulation(situation=situation).calculate(variable, period)
    return float(values[0])


@lru_cache(maxsize=None)
def base_income(state, variable):
    return income(state, variable, {})


def received(variable, amount):
    """An annual amount at the variable's period."""
    return (
        amount
        if system.variables[variable].definition_period == "year"
        else amount / 12
    )


@pytest.mark.parametrize(
    "state, variable, rule", PROGRAMS, ids=[r[1] for r in PROGRAMS]
)
@given(st.floats(min_value=1_200, max_value=200_000).map(lambda x: round(x, 2)))
@settings(max_examples=2, deadline=None)
def test_railroad_benefits_count_as_received(state, variable, rule, amount):
    """R1. The whole benefit counts, from the first dollar."""
    change = income(state, variable, {"railroad_benefits": amount}) - base_income(
        state, variable
    )
    assert change == pytest.approx(received(variable, amount), abs=0.05), rule


PENSION_PROGRAMS = [
    row
    for row in PROGRAMS
    if row[1]
    in {
        "al_ccsp_countable_income",
        "co_ccap_countable_income",
        "md_ccs_countable_income",
        "mo_ccs_countable_income",
        "wi_shares_countable_income",
    }
]


@pytest.mark.parametrize(
    "state, variable, rule", PENSION_PROGRAMS, ids=[r[1] for r in PENSION_PROGRAMS]
)
@given(st.floats(min_value=1_200, max_value=200_000).map(lambda x: round(x, 2)))
@settings(max_examples=2, deadline=None)
def test_railroad_benefits_count_as_a_pension_would(state, variable, rule, amount):
    """R2. These rules count pensions and annuities without distinction."""
    railroad = income(state, variable, {"railroad_benefits": amount})
    pension = income(state, variable, {"pension_income": amount})
    assert railroad == pytest.approx(pension, abs=0.05), rule
