from policyengine_us.model_api import *


class taxable_interest_income(Variable):
    value_type = float
    entity = Person
    label = "taxable interest income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.taxable_interest_and_ordinary_dividends"
