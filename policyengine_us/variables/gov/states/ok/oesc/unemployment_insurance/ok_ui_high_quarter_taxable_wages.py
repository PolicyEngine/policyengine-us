from policyengine_us.model_api import *


class ok_ui_high_quarter_taxable_wages(Variable):
    """Wages paid in the claimant's highest base-period quarter, capped at the
    Oklahoma taxable wage base per quarter. Used as the input to the weekly
    benefit amount formula per 40 O.S. § 2-104(A). PolicyEngine cannot derive
    quarterly wages from annual data, so this is a direct input rather than a
    computed value; populate via test fixtures or reform.
    """

    value_type = float
    entity = Person
    label = "Oklahoma UI high quarter taxable wages"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.OK
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=44",
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=49",
    )
