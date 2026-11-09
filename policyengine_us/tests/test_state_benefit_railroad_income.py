"""State and county benefit programs count Railroad Retirement Act benefits as income.

Each row names an income list or variable, the rule that reaches railroad
retirement benefits, and the variable that reads the list. A rule reaches the
benefits by naming them, by counting pensions, annuities or retirement
benefits, or by counting all income it doesn't exclude.

Invariants:

- R1: for every program below and any benefit amount, railroad benefits raise
  the program's income by the amount received, at the variable's period. Where
  the income total also counts cash aid that the same benefit reduces, the test
  holds that aid at zero, so the row isolates the income list from the aid's own
  income test. R1 shows that the list entry reaches the program's income. Whether
  a rule reaches railroad benefits is a matter of the rule's text, which each
  row cites.
- R2: the same dollars count the same whether a person receives them as railroad
  benefits or as a pension, for programs whose lists count pensions.
- R3: every state or county list and variable outside the tax code that reads a
  Social Security amount either counts railroad benefits or appears in
  NO_RAILROAD_INCOME with the reason it doesn't. A new reader fails this test
  until its author reads the rule and does one or the other.
- R4: no list holds railroad_benefits twice.
"""

import ast
from functools import lru_cache
from pathlib import Path

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEAR = 2026
MONTH = "2026-06"
PACKAGE = Path(__file__).resolve().parents[1]

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
    ("HI", "hi_ccap_countable_income", "HAR 17-798.3-10(b)(2)(A)"),
    ("ID", "id_iccp_countable_income", "IDAPA 16.06.12"),
    ("IL", "il_aabd_gross_unearned_income", "89 Ill. Adm. Code 113.100"),
    ("IL", "il_tanf_gross_unearned_income", "89 Ill. Adm. Code 112.100"),
    ("IL", "il_hbwd_countable_unearned_income", "89 Ill. Adm. Code 120.330"),
    ("IL", "il_isbe_countable_income", "ISBE household income form"),
    ("KS", "ks_ccap_countable_income", "KEESM 6200"),
    ("KS", "ks_liheap_countable_unearned_income", "KEESM 13361"),
    ("KY", "ky_ccap_countable_income", "922 KAR 2:160"),
    ("MA", "ma_tcap_gross_unearned_income", "106 CMR 704.210(B)"),
    ("MA", "ma_ccfa_countable_income_person", "EEC interim policies, Oct. 2023"),
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
    ("MT", "mt_ccap_countable_income", "Child care manual CC 2-6"),
    ("NC", "nc_lieap_gross_income_person", "EP-300 300.09 and FNS 300.01 B"),
    ("NC", "nc_tanf_countable_gross_unearned_income", "WF-114"),
    ("ND", "nd_tanf_gross_unearned_income", "Manual 400-19-55-20-15"),
    ("NH", "nh_ccap_countable_income", "He-C 6910.06"),
    ("NJ", "nj_liheap_countable_income_person", "LIHEAP handbook 2.3.D"),
    ("NJ", "nj_ccap_countable_income", "FFY 2025-2027 CCDF plan"),
    ("NV", "nv_ccdp_countable_income", "Child care manual 306"),
    ("OK", "ok_ccs_gross_income", "OAC 340:40-7-11(c)(2)"),
    ("PA", "pa_ccw_countable_income", "55 Pa. Code ch. 3042 app. A, part I(F)"),
    ("RI", "ri_ccap_countable_income", "218-RICR-20-00-4"),
    ("SC", "sc_ccap_countable_income", "CCS policy manual"),
    ("TX", "tx_fpp_countable_unearned_income", "FPP manual 9000"),
    ("TX", "tx_ceap_countable_income_person", "10 TAC 6.4"),
    ("UT", "ut_ccap_gross_income", "Utah Admin. Code R986-200-235(2)(a)"),
    ("VA", "va_ccsp_countable_income", "8 VAC 20-790-40(H)"),
    ("VT", "vt_ccfap_countable_income", "CCFAP regulations"),
    ("WA", "wa_wccc_countable_income", "WAC 110-15-0060(8)"),
    ("WI", "wi_shares_countable_income", "Wisconsin Shares handbook"),
    ("WV", "wv_ccap_countable_income", "Child care policy 5.2.4"),
    ("WY", "wy_power_gross_unearned_income", "SNAP and POWER manual"),
    ("WY", "wy_ccap_gross_income", "Child care rules ch. 1, app. B"),
    # County programs.
    ("CA", "ca_ala_general_assistance_countable_income_person", "GA regulations"),
    ("CA", "ca_oc_general_relief_gross_unearned_income", "GR manual section 70.1"),
    ("CA", "ca_smc_general_assistance_countable_income", "GA fact sheet"),
    ("CA", "la_general_relief_gross_income", "ABP 392"),
    ("CA", "ca_la_ez_save_countable_income", "EZ-SAVE income definition"),
    ("CA", "ca_riv_liheap_countable_income", "2025 LIHEAP application"),
    ("CA", "ca_riv_share_countable_income", "SHARE program page"),
]


# LIHEAP and energy programs whose formulas read Social Security directly and
# take railroad benefits from the program's unearned income list, which already
# named them. R1 confirms the benefits reach the total.
ALREADY_COUNTED = [
    ("CO", "co_leap_countable_income_person", "LEAP income list"),
    ("CT", "ct_ceap_countable_income", "CEAP income list"),
    ("GA", "ga_liheap_income", "LIHEAP income list"),
    ("IA", "ia_liheap_countable_unearned_income", "LIHEAP Appendix C"),
    ("ID", "id_liheap_countable_income", "LIHEAP income list"),
    ("IN", "in_eap_income", "EAP income list"),
    ("KY", "ky_liheap_income", "LIHEAP income list"),
    ("LA", "la_liheap_countable_income", "LIHEAP income list"),
    ("MT", "mt_liheap_countable_income", "LIHEAP income list"),
    ("NV", "nv_liheap_countable_income", "LIHEAP income list"),
    ("OH", "oh_liheap_countable_income", "HEAP income list"),
    ("SD", "sd_liheap_countable_income", "LIEAP income list"),
    ("TN", "tn_liheap_countable_income", "LIHEAP income list"),
    ("WA", "wa_liheap_countable_income", "LIHEAP income list"),
    ("WY", "wy_lieap_countable_income", "LIEAP income list"),
]

# These totals count cash aid (ca_tanf, ks_tanf or tanf) that falls as income
# rises, so a benefit the aid program counts removes aid from a household on the
# program. Wages above the aid programs' limits keep the aid at zero with and
# without the benefit.
WAGES_ABOVE_AID_LIMITS = {"employment_income": 60_000}
BASE_INPUTS = {
    "ca_child_care_countable_income": WAGES_ABOVE_AID_LIMITS,
    "ca_cpuc_countable_income": WAGES_ABOVE_AID_LIMITS,
    "ca_la_ez_save_countable_income": WAGES_ABOVE_AID_LIMITS,
    "ca_riv_liheap_countable_income": WAGES_ABOVE_AID_LIMITS,
    "ca_riv_share_countable_income": WAGES_ABOVE_AID_LIMITS,
    "ks_liheap_countable_unearned_income": WAGES_ABOVE_AID_LIMITS,
    "la_general_relief_gross_income": WAGES_ABOVE_AID_LIMITS,
}

COUNTIES = {
    "ca_oc_general_relief_gross_unearned_income": "ORANGE_COUNTY_CA",
    "ca_smc_general_assistance_countable_income": "SAN_MATEO_COUNTY_CA",
    "la_general_relief_gross_income": "LOS_ANGELES_COUNTY_CA",
    "ca_la_ez_save_countable_income": "LOS_ANGELES_COUNTY_CA",
    "ca_riv_liheap_countable_income": "RIVERSIDE_COUNTY_CA",
    "ca_riv_share_countable_income": "RIVERSIDE_COUNTY_CA",
}


def household(state, inputs, county=None):
    """A single 40-year-old parent with one child, as every program's rules apply."""
    people = {
        "parent": {"age": {YEAR: 40}, **{k: {YEAR: v} for k, v in inputs.items()}},
        "child": {"age": {YEAR: 5}},
    }
    members = list(people)
    home = {"members": members, "state_code": {YEAR: state}}
    if county:
        home["county_str"] = {YEAR: county}
    return {
        "people": people,
        "tax_units": {"tax_unit": {"members": members}},
        "families": {"family": {"members": members}},
        "marital_units": {
            "parent_unit": {"members": ["parent"]},
            "child_unit": {"members": ["child"]},
        },
        "spm_units": {"spm_unit": {"members": members}},
        "households": {"household": home},
    }


def income(state, variable, inputs):
    """The program's income for the parent, at the variable's own period."""
    period = YEAR if system.variables[variable].definition_period == "year" else MONTH
    situation = household(
        state, {**BASE_INPUTS.get(variable, {}), **inputs}, COUNTIES.get(variable)
    )
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


AMOUNTS = st.floats(min_value=1, max_value=200_000).map(lambda x: round(x, 2))
R1_ROWS = PROGRAMS + ALREADY_COUNTED


@pytest.mark.parametrize("state, variable, rule", R1_ROWS, ids=[r[1] for r in R1_ROWS])
@given(AMOUNTS)
@settings(max_examples=5, deadline=None)
def test_railroad_benefits_count_as_received(state, variable, rule, amount):
    """R1. The whole benefit counts, from the first dollar."""
    change = income(state, variable, {"railroad_benefits": amount}) - base_income(
        state, variable
    )
    assert change == pytest.approx(received(variable, amount), abs=0.05), rule


# Programs whose modeled lists have no pension line, so R2 doesn't apply. Illinois
# marks pension_income as exempt in its TANF list; the other lists don't name it.
NO_PENSION_LINE = {
    "ca_ala_general_assistance_countable_income_person",
    "ca_tanf_other_unearned_income",
    "il_aabd_gross_unearned_income",
    "il_hbwd_countable_unearned_income",
    "il_tanf_gross_unearned_income",
    "la_general_relief_gross_income",
}
PENSION_PROGRAMS = [row for row in PROGRAMS if row[1] not in NO_PENSION_LINE]


@pytest.mark.parametrize(
    "state, variable, rule", PENSION_PROGRAMS, ids=[r[1] for r in PENSION_PROGRAMS]
)
@given(AMOUNTS)
@settings(max_examples=5, deadline=None)
def test_railroad_benefits_count_as_a_pension_would(state, variable, rule, amount):
    """R2. Railroad benefits and a pension of the same size count the same."""
    railroad = income(state, variable, {"railroad_benefits": amount})
    pension = income(state, variable, {"pension_income": amount})
    assert railroad == pytest.approx(pension, abs=0.05), rule


SOCIAL_SECURITY = {
    "social_security",
    "social_security_dependents",
    "social_security_disability",
    "social_security_retirement",
    "social_security_survivors",
}

SIGNAL = "Reads receipt of a benefit as a yes-or-no test, not an income amount."
SOCIAL_SECURITY_ONLY = "The rule or list covers Social Security benefits alone."
UNRESOLVED = "The cited sources don't settle whether railroad benefits count."
_STATES = "parameters/gov/states/"
_COUNTY = "parameters/gov/local/ca/"
_STATE_CODE = "variables/gov/states/"

# Readers outside the tax code that leave railroad benefits out, and why. A
# variable whose formula reads Social Security directly and takes railroad benefits
# from a list passes through ALREADY_COUNTED instead.
NO_RAILROAD_INCOME = {
    _COUNTY + "cc/general_assistance/countable_income/sources.yaml": UNRESOLVED,
    _COUNTY + "riv/general_relief/income/sources/unearned.yaml": UNRESOLVED,
    _STATES + "ca/cdss/tanf/cash/income/sources/db_unearned.yaml": SOCIAL_SECURITY_ONLY,
    # An exemption list: counting railroad benefits here would exempt them.
    _STATES + "ca/chhs/wdp/eligibility/income/sources/disability.yaml": (
        "This list exempts disability income, and railroad_benefits doesn't "
        "separate disability annuities, so every railroad payment counts."
    ),
    _STATES + "in/fssa/ccdf/income/sources.yaml": UNRESOLVED,
    _STATES + "la/ldoe/ccap/income/unearned_sources.yaml": UNRESOLVED,
    _STATES
    + "mn/dcyf/ccap/income/countable_income/rsdi_sources.yaml": SOCIAL_SECURITY_ONLY,
    _STATES + "ms/dom/wd/eligibility/income/sources/unearned.yaml": UNRESOLVED,
    _STATES + "nc/ncdhhs/scca/income/sources.yaml": UNRESOLVED,
    _STATES + "nd/dhs/ccap/income/sources.yaml": UNRESOLVED,
    _STATES + "or/delc/erdc/income/countable_income/sources.yaml": UNRESOLVED,
    _STATES + "sc/oeo/liheap/income/minor_unearned_sources.yaml": SOCIAL_SECURITY_ONLY,
    _STATES + "sd/dss/cca/income/sources.yaml": UNRESOLVED,
    _STATES + "wa/dcyf/eceap/income_sources.yaml": UNRESOLVED,
    "variables/gov/local/ca/cc/ga/eligibility/"
    "ca_cc_general_assistance_eligible_person.py": SIGNAL,
    _STATE_CODE + "az/des/liheap/points/az_liheap_energy_need_points.py": SIGNAL,
    _STATE_CODE + "ca/chhs/wdp/eligibility/ca_wdp_disability_eligible.py": SIGNAL,
    _STATE_CODE + "dc/dhs/ccsp/eligibility/qualified_activity_or_need/"
    "dc_ccsp_qualified_need_eligible.py": SIGNAL,
    _STATE_CODE + "hi/dhs/liheap/hi_liheap_points.py": SIGNAL,
    _STATE_CODE + "il/hfs/hbwd/eligibility/il_hbwd_disability_eligible.py": SIGNAL,
    _STATE_CODE + "in/ihcda/eap/in_eap.py": SIGNAL,
    _STATE_CODE + "la/lhc/liheap/la_liheap.py": SIGNAL,
    _STATE_CODE + "md/dhs/fia/paa/md_paa_eligible.py": SIGNAL,
    _STATE_CODE + "ms/dom/wd/eligibility/ms_wd_disability_eligible.py": SIGNAL,
    _STATE_CODE + "nm/hca/liheap/nm_liheap.py": SIGNAL,
    _STATE_CODE + "pa/dhs/liheap/payment/pa_liheap_supplement.py": SIGNAL,
    _STATE_CODE + "va/dss/eap/va_eap_disabled.py": SIGNAL,
    _STATE_CODE + "wi/dhs/ssp/wi_ssp_countable_for_hud.py": SIGNAL,
    _STATE_CODE + "wi/doa/wheap/wi_wheap_household_size.py": SIGNAL,
}


def string_lists(node):
    """Every list of strings in a parsed parameter file."""
    if isinstance(node, dict):
        for value in node.values():
            yield from string_lists(value)
    elif isinstance(node, list):
        if all(isinstance(item, str) for item in node):
            yield node
        else:
            for value in node:
                yield from string_lists(value)


def parameter_lists(text):
    """Lists in a parameter file. BaseLoader keeps year-zero dates as strings."""
    return list(string_lists(yaml.load(text, Loader=yaml.BaseLoader)))


def code_strings(text):
    """String constants in a module's code, leaving out docstrings and comments."""
    tree = ast.parse(text)
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef))
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    }


def reads_without_railroad(path, text):
    """Whether a file reads Social Security and leaves railroad benefits out."""
    if path.suffix == ".yaml":
        return any(
            SOCIAL_SECURITY & set(names) and "railroad_benefits" not in names
            for names in parameter_lists(text)
        )
    names = code_strings(text)
    return bool(SOCIAL_SECURITY & names) and "railroad_benefits" not in names


def readers_without_railroad():
    """Non-tax state and county files that read Social Security without railroad benefits."""
    found = set()
    for tree, suffix in (("parameters/gov", ".yaml"), ("variables/gov", ".py")):
        for area in ("states", "local"):
            for path in (PACKAGE / tree / area).rglob(f"*{suffix}"):
                relative = path.relative_to(PACKAGE).as_posix()
                if "/tax/" in relative:
                    continue
                text = path.read_text(encoding="utf8")
                if "social_security" in text and reads_without_railroad(path, text):
                    found.add(relative)
    return found


def test_each_social_security_reader_counts_railroad_benefits_or_says_why():
    """R3. Tax provisions read the three railroad parts, so this test leaves them out."""
    checked_by_r1 = {variable for _, variable, _ in R1_ROWS}
    found = {
        path
        for path in readers_without_railroad()
        if Path(path).stem not in checked_by_r1
    }
    unexplained = sorted(found - set(NO_RAILROAD_INCOME))
    assert not unexplained, (
        "These read Social Security and leave out railroad_benefits. Read the rule, "
        "then add railroad_benefits or add the file to NO_RAILROAD_INCOME with the "
        f"reason: {unexplained}"
    )
    stale = sorted(set(NO_RAILROAD_INCOME) - found)
    assert not stale, f"These no longer leave railroad_benefits out: {stale}"


def test_no_list_holds_railroad_benefits_twice():
    """R4. A second entry would count the same dollars twice."""
    repeated = []
    for path in (PACKAGE / "parameters" / "gov").rglob("*.yaml"):
        text = path.read_text(encoding="utf8")
        if "railroad_benefits" not in text:
            continue
        if any(names.count("railroad_benefits") > 1 for names in parameter_lists(text)):
            repeated.append(path.relative_to(PACKAGE).as_posix())
    assert not repeated, repeated
