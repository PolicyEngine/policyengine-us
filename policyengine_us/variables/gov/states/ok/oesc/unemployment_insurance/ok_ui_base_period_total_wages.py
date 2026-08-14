from policyengine_us.model_api import *


class ok_ui_base_period_total_wages(Variable):
    """Sum of total (uncapped) gross wages across all four quarters of the
    base period, per 40 O.S. § 1-218 (wages definition), § 1-201(4) (base
    period definition), and § 2-207 (where "total wages" is used). Used in
    the monetary-eligibility tests in § 2-207(A) and § 2-207(B). PolicyEngine
    cannot derive quarterly wages from annual data, so this is a direct input
    rather than a computed value; populate via test fixtures or reform.
    Defaults to zero, so it is inert in microsimulation until supplied.
    """

    value_type = float
    entity = Person
    label = "Oklahoma UI base period total wages"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.OK
    reference = (
        # 40 O.S. §1-201(4) — Base period definition
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=20",
        # 40 O.S. §1-218 — Wages definition
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=42",
        # 40 O.S. §2-207 — Total wages used in monetary-eligibility tests
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=56",
    )
