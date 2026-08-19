from policyengine_us.model_api import *


class ok_ui_high_quarter_total_wages(Variable):
    """Total (uncapped) gross wages paid in the claimant's highest base-period
    quarter, per 40 O.S. § 2-207(A)(2), which applies the 1.5x multiplier to
    the claimant's total high-quarter wages rather than the taxable-capped
    figure. PolicyEngine cannot derive quarterly wages from annual data, so
    this is a direct input rather than a computed value; populate via test
    fixtures or reform. Defaults to zero, so it is inert in microsimulation
    until supplied.
    """

    value_type = float
    entity = Person
    label = "Oklahoma UI high quarter total wages"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.OK
    reference = (
        # 40 O.S. §2-207(A)(2) — total high-quarter wages used in the 1.5x test
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=56",
    )
