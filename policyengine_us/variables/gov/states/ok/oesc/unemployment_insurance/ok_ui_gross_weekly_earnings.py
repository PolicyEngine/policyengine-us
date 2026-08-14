from policyengine_us.model_api import *


class ok_ui_gross_weekly_earnings(Variable):
    """Gross earnings during a week of partial unemployment, used to compute
    the partial weekly benefit reduction per 40 O.S. § 2-105. Stored at the
    annual definition period but holds an average WEEKLY figure; populate via
    test fixtures or reform. Defaults to zero, so it is inert in
    microsimulation until supplied.
    """

    value_type = float
    entity = Person
    label = "Oklahoma UI average weekly earnings"
    documentation = (
        "Stored at the annual definition period but holds an average WEEKLY "
        "figure, populated via test fixtures or reform."
    )
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.OK
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=51",
    )
