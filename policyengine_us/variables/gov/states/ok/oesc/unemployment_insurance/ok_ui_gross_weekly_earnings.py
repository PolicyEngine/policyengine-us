from policyengine_us.model_api import *


class ok_ui_gross_weekly_earnings(Variable):
    """Gross earnings during a week of partial unemployment, used to compute
    the partial weekly benefit reduction per 40 O.S. § 2-105. Stored at the
    annual definition period to match other UI inputs; populate via test
    fixtures or reform.
    """

    value_type = float
    entity = Person
    label = "Oklahoma UI gross weekly earnings"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.OK
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=50"
    )
