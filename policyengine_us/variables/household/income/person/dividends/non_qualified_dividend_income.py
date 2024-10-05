from policyengine_us.model_api import *


class non_qualified_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "non-qualified dividend income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.non_qualified_dividend_income"
