from policyengine_us.model_api import *


class ok_ui_base_period_total_wages(Variable):
    """Sum of total (uncapped) gross wages across all four quarters of the
    base period, per 40 O.S. § 1-218 and § 1-202. Used in the monetary-
    eligibility tests in § 2-207(A) and § 2-207(B). PolicyEngine cannot derive
    quarterly wages from annual data, so this is a direct input rather than a
    computed value; populate via test fixtures or reform.
    """

    value_type = float
    entity = Person
    label = "Oklahoma UI base period total wages"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.OK
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=24",
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=42",
    )
