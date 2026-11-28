"""State and county benefit programs count Railroad Retirement Act benefits as income.

Each row names a state, the variable that totals a program's income, and the
rule that covers railroad retirement benefits there. A rule covers the
benefits by naming railroad retirement, by listing pensions, annuities,
retirement benefits or federal benefits as income, or by defining income as
everything outside its exclusions.

Invariants:

- R1: for every program below and amounts from $1 to $200,000, railroad benefits
  raise the program's income by the amount received, at the variable's period.
  Where the income total also counts cash aid that the same benefit reduces, the
  test holds that aid at zero, so the row isolates the income list from the aid's
  own income test. R1 shows that the list entry reaches the program's income,
  and each row cites the rule whose text covers railroad benefits.
- R2: the same dollars count the same whether a person receives them as railroad
  benefits or as a pension, for programs whose lists count pensions.
- R3 scans every state and county list outside the tax code, and the top level
  and each function or class body of every state and county variable outside the
  tax code. Each one that reads a Social Security amount counts railroad benefits
  (the total or one of its parts), belongs to an R1 variable, or appears in
  NO_RAILROAD_INCOME with the reason it doesn't. A new reader fails this test
  until its author reads the rule and does one or the other. R3 reads names
  written out in full, so a name built with an f-string or concatenation, or a
  scalar parameter, passes unseen. So does a module that names Social Security in
  one top-level list and railroad benefits in another, since R3 reads a
  module's top level as one scope. A scope that names a railroad amount passes
  even if it reads the amount only as a yes-or-no test, so R1 rows cover the two
  LIHEAP programs that do that and count the benefits through their lists.
- R4: no two entries of a parameter list or variable adds list hold the same
  railroad dollars. The total, the tier 1 amount, the taxable total and each
  part map to the taxable and tax-free tier 1 benefits and the taxable and
  tax-free rest of the annuity.
- R5: a state or county program that reads a federal total, list or test takes
  its sources. R5 starts from each federal list that holds Social Security
  without railroad benefits, each federal variable that adds such a list or
  reads it in a formula, and each federal variable whose own code names a
  Social Security amount and no railroad amount, as R3 checks state code. It
  then takes up to two more steps. Each step adds the federal variables that
  name no railroad amount and either name a variable already found or add or
  read a federal list that holds one and no railroad amount, as irs_gross_income
  adds taxable_social_security through the gross income list. Each source that
  state or county code outside the tax code reads must appear in FEDERAL_GAPS,
  and the test fails on an entry once its source counts railroad benefits or no
  such code reads it. A new reader of a source already in FEDERAL_GAPS passes.
  A third step would reach further eligibility tests and amounts, such as
  is_snap_eligible, is_aca_ptc_eligible and medicaid_enrolled, and R5 doesn't
  take it. R5 reads a parameter path written out in code, built through names
  that a plain assignment to one name binds in the same module or function, or
  named in a string. R5 follows those assignments once, in source order, and a
  name bound to two paths reads as both. A path passed as a function argument,
  read with getattr or a subscript, bound in a tuple, annotated, chained or
  walrus assignment, bound to a call or conditional expression, built in a loop
  from a name the loop assigns further down, or used in a nested function under
  the enclosing function's name passes unseen. R5 reads a path that continues
  past a call, such as parameters.gov.x(period).y, only up to the call.
"""

import ast
import inspect
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
    ("CA", "ca_cvrp_countable_income", "CVRP Implementation Manual"),
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
    ("LA", "la_ccap_countable_income", "LAC 28:CLXV.509.A.3.b"),
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
    ("ND", "nd_ccap_gross_income", "NDAC 75-02-01.3-08"),
    ("NH", "nh_ccap_countable_income", "He-C 6910.06"),
    ("NJ", "nj_liheap_countable_income_person", "LIHEAP handbook 2.3.D"),
    ("NJ", "nj_ccap_countable_income", "FFY 2025-2027 CCDF plan"),
    ("NV", "nv_ccdp_countable_income", "Child care manual 306"),
    ("OK", "ok_ccs_gross_income", "OAC 340:40-7-11(c)(2)"),
    ("OR", "or_erdc_countable_income", "OAR 414-175-0035(52)"),
    ("PA", "pa_ccw_countable_income", "55 Pa. Code ch. 3042 app. A, part I(F)"),
    ("RI", "ri_ccap_countable_income", "218-RICR-20-00-4"),
    ("SC", "sc_ccap_countable_income", "CCS policy manual"),
    ("SD", "sd_cca_gross_income", "CCA subsidy manual, section 4"),
    ("TX", "tx_fpp_countable_unearned_income", "FPP manual 9000"),
    ("TX", "tx_ceap_countable_income_person", "10 TAC 6.4"),
    ("TX", "tx_dta_csfp_countable_income", "Texas CSFP Handbook, section 3"),
    ("TX", "tx_ccs_countable_income", "40 TAC 809.44(c)"),
    ("UT", "ut_ccap_gross_income", "Utah Admin. Code R986-200-235(2)(a)"),
    ("VA", "va_ccsp_countable_income", "8 VAC 20-790-40(H)"),
    ("VT", "vt_ccfap_countable_income", "CCFAP regulations"),
    ("WA", "wa_wccc_countable_income", "WAC 110-15-0060(8)"),
    ("WA", "wa_eceap_family_income", "DCYF 05-006, section 9"),
    ("WI", "wi_shares_countable_income", "Wisconsin Shares handbook"),
    ("WV", "wv_ccap_countable_income", "Child care policy 5.2.4"),
    ("WY", "wy_power_gross_unearned_income", "SNAP and POWER manual"),
    ("WY", "wy_ccap_gross_income", "Child care rules ch. 1, app. B"),
    # County programs.
    ("CA", "ca_ala_general_assistance_countable_income_person", "GA regulations"),
    ("CA", "ca_oc_general_relief_gross_unearned_income", "GR manual section 70.1"),
    ("CA", "ca_smc_general_assistance_countable_income", "GA fact sheet"),
    ("CA", "la_general_relief_gross_income", "GR policy 44-101"),
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
    ("MO", "mo_liheap_countable_income_person", "LIHEAP income list"),
    ("MT", "mt_liheap_countable_income", "LIHEAP income list"),
    ("NV", "nv_liheap_countable_income", "LIHEAP income list"),
    ("OH", "oh_liheap_countable_income", "HEAP income list"),
    ("PA", "pa_liheap_income", "LIHEAP income list"),
    ("SD", "sd_liheap_countable_income", "LIEAP income list"),
    ("TN", "tn_liheap_countable_income", "LIHEAP income list"),
    ("WA", "wa_liheap_countable_income", "LIHEAP income list"),
    ("WY", "wy_lieap_countable_income", "LIEAP income list"),
]

# These totals count cash aid (ca_tanf, hi_tanf, ks_tanf or tanf) that falls as
# income rises, so a benefit the aid program counts removes aid from a household
# on the program. Wages above the aid programs' limits keep the aid at zero with and
# without the benefit.
WAGES_ABOVE_AID_LIMITS = {"employment_income": 60_000}
BASE_INPUTS = {
    "ca_child_care_countable_income": WAGES_ABOVE_AID_LIMITS,
    "ca_cpuc_countable_income": WAGES_ABOVE_AID_LIMITS,
    "ca_cvrp_countable_income": WAGES_ABOVE_AID_LIMITS,
    "ca_la_ez_save_countable_income": WAGES_ABOVE_AID_LIMITS,
    "ca_riv_liheap_countable_income": WAGES_ABOVE_AID_LIMITS,
    "ca_riv_share_countable_income": WAGES_ABOVE_AID_LIMITS,
    "hi_ccap_countable_income": WAGES_ABOVE_AID_LIMITS,
    "ks_liheap_countable_unearned_income": WAGES_ABOVE_AID_LIMITS,
    "la_general_relief_gross_income": WAGES_ABOVE_AID_LIMITS,
    "pa_liheap_income": WAGES_ABOVE_AID_LIMITS,
    "tx_dta_csfp_countable_income": WAGES_ABOVE_AID_LIMITS,
    "wa_eceap_family_income": WAGES_ABOVE_AID_LIMITS,
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
# marks pension_income as exempt in its TANF and AABD lists; the other lists
# don't name it.
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
    "tax_exempt_social_security",
}

# Each railroad amount and the dollars it holds: the filers' taxable tier 1
# social security equivalent benefits, a dependent's taxable tier 1 benefits,
# the tax-free tier 1 benefits, and the taxable and tax-free rest of the annuity.
# PolicyEngine/policyengine-us#10696 splits railroad_benefits into the tier 1
# amount and the two parts of the rest, and defines the tax amounts. A
# dependent's own return taxes the dependent's tier 1 benefits, and the tax unit's
# tax-free tier 1 amount takes out only the filers' taxable part, so it holds a
# dependent's taxable tier 1 dollars too. PolicyEngine/policyengine-us#10722 adds
# the filers' tax-free tier 1 amount, which leaves dependents out.
TIER_1_TAXABLE = "taxable_railroad_social_security_equivalent_benefits"
TIER_1_DEPENDENT = "dependent_taxable_railroad_social_security_equivalent_benefits"
TIER_1_TAX_FREE = "tax_exempt_railroad_social_security_equivalent_benefits"
REST_TAXABLE = "taxable_railroad_pension_benefits"
REST_TAX_FREE = "tax_exempt_railroad_pension_benefits"
TIER_1 = {TIER_1_TAXABLE, TIER_1_DEPENDENT, TIER_1_TAX_FREE}
RAILROAD_DOLLARS = {
    "railroad_benefits": TIER_1 | {REST_TAXABLE, REST_TAX_FREE},
    "railroad_social_security_equivalent_benefits": TIER_1,
    "tax_unit_railroad_social_security_equivalent_benefits": TIER_1,
    "tax_unit_railroad_social_security_equivalent_benefits_for_taxability": {
        TIER_1_TAXABLE,
        TIER_1_TAX_FREE,
    },
    "taxable_railroad_benefits": {TIER_1_TAXABLE, REST_TAXABLE},
    "tax_unit_taxable_railroad_social_security_equivalent_benefits": {TIER_1_TAXABLE},
    "filer_tax_exempt_railroad_social_security_equivalent_benefits": {TIER_1_TAX_FREE},
    TIER_1_TAXABLE: {TIER_1_TAXABLE},
    TIER_1_DEPENDENT: {TIER_1_DEPENDENT},
    TIER_1_TAX_FREE: {TIER_1_TAX_FREE, TIER_1_DEPENDENT},
    REST_TAXABLE: {REST_TAXABLE},
    REST_TAX_FREE: {REST_TAX_FREE},
}
RAILROAD = set(RAILROAD_DOLLARS)

SIGNAL = (
    "Reads receipt of Social Security disability as a yes-or-no test, not an "
    "income amount. railroad_benefits doesn't separate disability annuities, so "
    "it can't stand in for receipt of Social Security disability."
)
SOCIAL_SECURITY_ONLY = "The rule or list covers Social Security benefits alone."
DISABILITY_ONLY = (
    "The list holds disability income, and railroad_benefits doesn't separate "
    "railroad disability annuities. CalWORKs counts railroad benefits with its "
    "other unearned income (ca_tanf_other_unearned_income, an R1 row)."
)
MINOR_SOCIAL_SECURITY_OR_DISABILITY = (
    "The guide counts a minor's Social Security or disability income. It names "
    "Social Security, not railroad benefits, and a minor's railroad annuity pays "
    "a child or survivor, not a disabled worker."
)
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
    _STATES + "ca/cdss/tanf/cash/income/sources/db_unearned.yaml": DISABILITY_ONLY,
    # An exemption list: counting railroad benefits here would exempt them.
    _STATES + "ca/chhs/wdp/eligibility/income/sources/disability.yaml": (
        "This list exempts disability income, and railroad_benefits doesn't "
        "separate disability annuities, so every railroad payment counts."
    ),
    _STATES + "in/fssa/ccdf/income/sources.yaml": UNRESOLVED,
    _STATES
    + "mn/dcyf/ccap/income/countable_income/rsdi_sources.yaml": SOCIAL_SECURITY_ONLY,
    _STATES + "ms/dom/wd/eligibility/income/sources/unearned.yaml": UNRESOLVED,
    _STATES + "nc/ncdhhs/scca/income/sources.yaml": UNRESOLVED,
    _STATES + "sc/oeo/liheap/income/minor_unearned_sources.yaml": (
        MINOR_SOCIAL_SECURITY_OR_DISABILITY
    ),
    # RCW 84.36.383(7)(g) counts Social Security and railroad retirement benefits
    # that AGI leaves out. The tax-free railroad amounts come with the federal
    # treatment in PolicyEngine/policyengine-us#10696, and
    # PolicyEngine/policyengine-us#10722 adds them to this list.
    _STATES + "wa/dor/property_tax_exemption/senior_disabled/income/sources.yaml": (
        "Main has no tax-free railroad amount for this list to add."
    ),
    "variables/gov/local/ca/cc/ga/eligibility/"
    "ca_cc_general_assistance_eligible_person.py": SIGNAL,
    _STATE_CODE + "az/des/liheap/points/az_liheap_energy_need_points.py": SIGNAL,
    _STATE_CODE + "ca/chhs/wdp/eligibility/ca_wdp_disability_eligible.py": SIGNAL,
    _STATE_CODE + "dc/dhs/ccsp/eligibility/qualified_activity_or_need/"
    "dc_ccsp_qualified_need_eligible.py": SIGNAL,
    _STATE_CODE + "hi/dhs/liheap/hi_liheap_points.py": SIGNAL,
    _STATE_CODE + "il/hfs/hbwd/eligibility/il_hbwd_disability_eligible.py": SIGNAL,
    _STATE_CODE + "in/ihcda/eap/in_eap.py": SIGNAL,
    _STATE_CODE + "la/lhc/liheap/la_liheap_matrix_amount.py": SIGNAL,
    _STATE_CODE + "ms/dom/wd/eligibility/ms_wd_disability_eligible.py": SIGNAL,
    _STATE_CODE + "nm/hca/liheap/nm_liheap.py": SIGNAL,
    _STATE_CODE + "pa/dhs/liheap/payment/pa_liheap_supplement.py": SIGNAL,
    _STATE_CODE + "va/dss/eap/va_eap_disabled.py": SIGNAL,
    _STATE_CODE + "wa/dor/property_tax_exemption/senior_disabled/"
    "wa_pte_retired_due_to_disability.py": SIGNAL,
    _STATE_CODE + "wi/dhs/ssp/wi_ssp_countable_for_hud.py": SIGNAL,
    # WHEAP Manual 3.2.2.4 counts a non-citizen who receives FoodShare or "any
    # form of monthly Social Security income" as an eligible household member.
    _STATE_CODE + "wi/doa/wheap/wi_wheap_household_size.py": SOCIAL_SECURITY_ONLY,
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


def code_strings(nodes, docstrings):
    """String constants under the nodes, leaving out docstrings and comments."""
    return {
        node.value
        for root in nodes
        for node in ast.walk(root)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    }


def code_scopes(text):
    """String constants of the module's top level, each function and each class body."""
    tree = ast.parse(text)
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef))
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }
    functions = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
    yield code_strings(
        [
            child
            for child in tree.body
            if not isinstance(child, (*functions, ast.ClassDef))
        ],
        docstrings,
    )
    for node in ast.walk(tree):
        if isinstance(node, functions):
            yield code_strings([node], docstrings)
        elif isinstance(node, ast.ClassDef):
            body = [child for child in node.body if not isinstance(child, functions)]
            yield code_strings(body, docstrings)


def lacks_railroad(names):
    """Whether names count Social Security and no railroad benefit."""
    return bool(SOCIAL_SECURITY & set(names)) and not RAILROAD & set(names)


def reads_without_railroad(path, text):
    """Whether a file reads Social Security and leaves railroad benefits out."""
    if path.suffix == ".yaml":
        return any(lacks_railroad(names) for names in parameter_lists(text))
    return any(lacks_railroad(names) for names in code_scopes(text))


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


def counts_railroad_twice(names):
    """Whether two entries of a list hold the same railroad dollars."""
    dollars = [part for name in names for part in RAILROAD_DOLLARS.get(name, ())]
    return len(dollars) != len(set(dollars))


def test_no_list_holds_railroad_benefits_twice():
    """R4. Two entries that hold the same dollars would count them twice."""
    repeated = []
    for path in (PACKAGE / "parameters" / "gov").rglob("*.yaml"):
        text = path.read_text(encoding="utf8")
        if "railroad" in text and any(
            counts_railroad_twice(names) for names in parameter_lists(text)
        ):
            repeated.append(path.relative_to(PACKAGE).as_posix())
    repeated += [
        name
        for name, variable in system.variables.items()
        if isinstance(variable.adds, (list, tuple))
        and counts_railroad_twice(list(variable.adds))
    ]
    assert not repeated, repeated


# Federal totals, lists and tests that state and county programs read. Each one
# counts Social Security, tests for Social Security disability, or turns on such
# a total or test, and leaves railroad benefits out, so the programs that read it
# leave them out too.
FEDERAL_GAPS = {
    # Issue PolicyEngine/policyengine-us#10551 covers the TANF and SNAP lists.
    # Under 7 CFR 273.9(b)(2)(ii), state SNAP agencies count
    # "Annuities; pensions; retirement, veteran's, or disability benefits".
    # Under BEM 503, Michigan's MDHHS counts for FIP, its TANF program, the
    # "gross benefit amount" that the Railroad Retirement Board pays.
    "tanf_gross_unearned_income": "TANF baseline list: 64 TANF variables in 37 states",
    "gov.usda.snap.income.sources.unearned": "SNAP unearned list: Nebraska LIHEAP",
    # Under IRC 86(d)(1)(B), a tier 1 benefit is a Social Security benefit, so
    # its taxable part belongs in gross income. On main, the gross income list
    # counts taxable_social_security and no railroad amount.
    # PolicyEngine/policyengine-us#10696 adds the taxable railroad amounts.
    "irs_gross_income": "Gross income: DC, IL, MA energy aid; IL IHWAP, I-PASS, SCRETD",
    "filer_tax_exempt_social_security": "Filer tax-exempt Social Security: IL SCRETD",
    "adjusted_gross_income": "AGI: CA CVRP normal rebate, WA exemption income",
    "adjusted_gross_income_person": "Person AGI: IL FPP, IL BAP",
    "charitable_contributions_ald": "Charitable deduction: CA CVRP normal rebate",
    "tax_unit_is_filer": "Filing requirement: NM premium help",
    # Under IRC 36B(d)(2)(B)(iii), taxpayers add to AGI the untaxed share of
    # "social security benefits (as defined in section 86(d))", tier 1 included.
    # On main, neither adjusted_gross_income nor the MAGI additions list counts
    # railroad benefits. PolicyEngine/policyengine-us#10696 adds the taxable
    # amounts to AGI and the tax-free tier 1 amount to the additions list.
    "medicaid_magi": "MAGI: Colorado CHP+, Healthy Michigan, Montana HELP",
    "tax_unit_medicaid_income_level": "MAGI ratio: 17 CHIP premiums, IN HIP, MI, MT",
    # CA CCHIP and RI postpartum coverage also reach medicaid_income_level
    # through medicaid_income_eligible, a helper in its module.
    "medicaid_income_level": "MAGI ratio: AR, CO, IL, MS, OR and WA programs",
    "aca_magi": "ACA MAGI: CA, MD, NM and VT premium help",
    "aca_magi_fraction": "ACA MAGI ratio: premium help in nine states",
    # These take ACA MAGI, or Medicare eligibility through ACA's list of
    # coverage that rules out the credit.
    "gov.aca.ineligible_coverage": "ACA coverage list: NM Puente Health",
    "aca_ptc": "ACA PTC: premium help in ten states",
    "aca_ptc_slcsp": "ACA benchmark premium: premium help in nine states",
    "aca_required_contribution_percentage": "ACA contribution share: VT",
    "files_return_for_aca_ptc": "ACA filing test: CA, MD and NM premium help",
    "is_aca_coverage_family_member": "ACA coverage family: NM premium help",
    "is_aca_marketplace_enrollee": "Marketplace enrollment: WA Cascade Care",
    "pays_aca_premium": "ACA premium payer: NJ NJHPS",
    # Under 7 U.S.C. 2012(j)(7), SNAP agencies treat a railroad disability
    # annuitant as disabled, and railroad_benefits doesn't separate disability
    # annuities from the others.
    "is_usda_disabled": "SNAP disability test: NC, NV, NY and OK energy aid",
    # Under 42 U.S.C. 426(b)(2)(B), a person under 65 gets Medicare Part A
    # after 24 months as "a disabled qualified railroad retirement beneficiary".
    # is_medicare_eligible tests age 65, or Social Security disability for 24
    # months, and the premiums, enrollment and Medicaid tests below read it.
    "is_medicare_eligible": "Medicare test: IL SMIB and fares, MBTA, MS HMW, DART",
    "base_part_b_premium": "Part B premium: IL SMIB",
    "medicare_enrolled": "Medicare enrollment: RI Medicaid third-party coverage",
    "medicare_part_a_premium": "Part A premium: energy aid income in eight states",
    "medicare_part_b_premium": "Part B premium: energy aid in 28 states, WA exemption",
    "is_adult_for_medicaid": "Medicaid adult test: MS HMW other coverage",
    "is_medicaid_eligible": "Medicaid test: CA CCHIP, CO CHP+",
    # The list holds medicare_enrolled.
    "gov.hhs.chip.disqualifying_health_coverage": "CHIP coverage list: RI",
    "has_chip_disqualifying_health_coverage": "CHIP coverage test: CA CCHIP",
}
# Mississippi's waiver reads the annual Medicaid income wrapper. The shared
# monthly formula reads the Part B premium two steps from Medicare eligibility.
# R5 stops before the annual wrapper. Mississippi sets the deduction to false.
FEDERAL_FORMULA_STEPS = 2


def is_state_or_local(relative):
    """Whether a path below the package sits in the states or local tree."""
    parts = Path(relative).parts
    return len(parts) > 2 and parts[2] in ("states", "local")


def federal_lists_without_railroad():
    """Dotted paths of federal parameter lists that count Social Security alone."""
    found = set()
    for path in (PACKAGE / "parameters" / "gov").rglob("*.yaml"):
        relative = path.relative_to(PACKAGE).as_posix()
        if is_state_or_local(relative):
            continue
        text = path.read_text(encoding="utf8")
        if "social_security" in text and reads_without_railroad(path, text):
            parts = path.relative_to(PACKAGE / "parameters").with_suffix("").parts
            found.add(".".join(parts))
    return found


def parameter_paths(node, aliases):
    """The dotted paths from gov onward that an expression can name."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    parts.reverse()
    if "gov" in parts:
        return {".".join(parts[parts.index("gov") :])}
    if isinstance(node, ast.Name):
        return {".".join([base, *parts]) for base in aliases.get(node.id, ())}
    return set()


def scope_nodes(scope):
    """The nodes of a module or function, without the bodies of functions inside."""
    pending = list(ast.iter_child_nodes(scope))
    while pending:
        node = pending.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            pending.extend(ast.iter_child_nodes(node))


def scope_paths(scope, outer):
    """The parameter paths a scope reads, through the names it assigns paths to."""
    aliases = {name: set(paths) for name, paths in outer.items()}
    nodes = list(scope_nodes(scope))
    assignments = sorted(
        (
            node
            for node in nodes
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ),
        key=lambda node: (node.lineno, node.col_offset),
    )
    # One pass in source order gives each name every path assigned to it up to
    # that line. A name assigned from its own attribute, such as
    # `p = p.income`, gains its new paths once, so the pass always ends.
    for node in assignments:
        aliases.setdefault(node.targets[0].id, set()).update(
            parameter_paths(node.value, aliases)
        )
    paths = set()
    for node in nodes:
        if isinstance(node, ast.Attribute):
            paths |= parameter_paths(node, aliases)
    return paths, aliases


def read_paths(tree):
    """The parameter paths that parsed code reads or names in a string."""
    paths, aliases = scope_paths(tree, {})
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            paths |= scope_paths(node, aliases)[0]
    return paths | code_strings([tree], set())


def reads_a_list(tree, lists):
    """The listed parameter paths that parsed code reads or names in a string."""
    return lists & read_paths(tree)


def federal_parameter_lists():
    """Each federal parameter file's dotted path and the names its lists hold."""
    found = {}
    for path in (PACKAGE / "parameters" / "gov").rglob("*.yaml"):
        relative = path.relative_to(PACKAGE).as_posix()
        if is_state_or_local(relative):
            continue
        held = {
            name
            for names in parameter_lists(path.read_text(encoding="utf8"))
            for name in names
        }
        if held:
            parts = path.relative_to(PACKAGE / "parameters").with_suffix("").parts
            found[".".join(parts)] = held
    return found


def federal_variables():
    """Each federal variable: its adds, the variables and paths it names, its scopes."""
    found = {}
    for name, variable in system.variables.items():
        try:
            source = Path(inspect.getfile(type(variable))).resolve()
            relative = source.relative_to(PACKAGE).as_posix()
        except (TypeError, ValueError):
            continue
        if is_state_or_local(relative):
            continue
        adds = variable.adds
        text = source.read_text(encoding="utf8")
        tree = ast.parse(text)
        names = code_strings([tree], set())
        if isinstance(adds, (list, tuple)):
            names |= set(adds)
        scopes = list(code_scopes(text))
        found[name] = (adds, names & set(system.variables), read_paths(tree), scopes)
    return found


def counts_social_security_alone(adds, names, paths, scopes, lists):
    """Whether a federal variable takes Social Security with no railroad amount."""
    if isinstance(adds, str):
        listed = adds in lists
    else:
        listed = isinstance(adds, (list, tuple)) and lacks_railroad(adds)
    if (listed or lists & paths) and not names & RAILROAD:
        return True
    return any(lacks_railroad(scope) for scope in scopes)


def carrying_lists(held, found):
    """Federal lists that hold a found variable and no railroad amount."""
    return {
        path for path, names in held.items() if names & found and not names & RAILROAD
    }


def federal_sources_without_railroad():
    """Federal lists and variables that count Social Security without railroad."""
    lists = federal_lists_without_railroad()
    held = federal_parameter_lists()
    variables = federal_variables()
    found = {
        name
        for name, (adds, names, paths, scopes) in variables.items()
        if name not in SOCIAL_SECURITY
        and counts_social_security_alone(adds, names, paths, scopes, lists)
    }
    # Each step takes the variables that name a found variable, or that add or
    # read a federal list holding one, such as the gross income sources list.
    for _ in range(FEDERAL_FORMULA_STEPS):
        carriers = carrying_lists(held, found)
        found |= {
            name
            for name, (_, names, paths, _) in variables.items()
            if name not in SOCIAL_SECURITY
            and (names & found or paths & carriers)
            and not names & RAILROAD
        }
    return lists | carrying_lists(held, found), found


def inherited_federal_sources():
    """Federal sources without railroad benefits that state or county code reads."""
    lists, variables = federal_sources_without_railroad()
    found = set()
    for tree, suffix in (("parameters/gov", ".yaml"), ("variables/gov", ".py")):
        for area in ("states", "local"):
            for path in (PACKAGE / tree / area).rglob(f"*{suffix}"):
                if "/tax/" in path.relative_to(PACKAGE).as_posix():
                    continue
                text = path.read_text(encoding="utf8")
                if suffix == ".yaml":
                    for names in parameter_lists(text):
                        found |= variables & set(names)
                    continue
                parsed = ast.parse(text)
                found |= variables & code_strings([parsed], set())
                found |= reads_a_list(parsed, lists)
    return found


def test_state_programs_that_read_a_federal_list_without_railroad_are_known():
    """R5. A program that reads a federal total, list or test takes its sources."""
    inherited = inherited_federal_sources()
    unknown = sorted(inherited - set(FEDERAL_GAPS))
    assert not unknown, (
        "State or county code reads these federal sources, which count Social "
        "Security and leave out railroad benefits. Read the program's rule, then "
        f"count railroad benefits or add the source to FEDERAL_GAPS: {unknown}"
    )
    stale = sorted(set(FEDERAL_GAPS) - inherited)
    assert not stale, (
        "No state or county code reads these as sources without railroad "
        f"benefits; remove them: {stale}"
    )
