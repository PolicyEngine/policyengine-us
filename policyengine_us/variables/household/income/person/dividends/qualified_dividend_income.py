from policyengine_us.model_api import *


class qualified_dividend_income(Variable):
    value_type = float
    entity = Person
    label = "qualified dividend income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.qualified_dividend_income"
