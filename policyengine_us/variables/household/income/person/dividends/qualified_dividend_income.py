from policyengine_us.model_api import *


class qualified_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "qualified dividend income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.qualified_dividend_income"
