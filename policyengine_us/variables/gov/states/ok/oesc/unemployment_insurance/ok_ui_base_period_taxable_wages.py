from policyengine_us.model_api import *


class ok_ui_base_period_taxable_wages(Variable):
    """Sum of taxable wages across all four quarters of the base period, each
    capped at the Oklahoma taxable wage base. Per 40 O.S. § 1-201(48) the
    taxable-wage cap applies per CALENDAR YEAR, not per quarter, per 40 O.S.
    § 1-223 and § 1-201(4). Used in the monetary-eligibility tests in
    § 2-207(A) and § 2-207(B). PolicyEngine cannot derive quarterly wages from
    annual data, so this is a direct input rather than a computed value;
    populate via test fixtures or reform. Defaults to zero, so it is inert in
    microsimulation until supplied.
    """

    value_type = float
    entity = Person
    label = "Oklahoma UI base period taxable wages"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.OK
    reference = (
        # 40 O.S. §1-201(48) — Taxable wages / base period definitions
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=23",
        # 40 O.S. §1-223 — Taxable wage base
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=44",
    )
