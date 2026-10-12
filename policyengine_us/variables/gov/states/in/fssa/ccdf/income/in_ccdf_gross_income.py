from policyengine_us.model_api import *


class in_ccdf_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Indiana CCDF gross countable income"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=26"
    )
    adds = "gov.states.in.fssa.ccdf.income.sources"
