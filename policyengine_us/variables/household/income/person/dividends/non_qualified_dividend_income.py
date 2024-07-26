from policyengine_us.model_api import *


class non_qualified_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "non-qualified dividend income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.taxable_interest_and_ordinary_dividends"
