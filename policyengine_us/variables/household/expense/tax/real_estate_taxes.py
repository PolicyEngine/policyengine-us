from policyengine_us.model_api import *


class real_estate_taxes(Variable):
    value_type = float
    entity = Person
    label = "Real estate taxes"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.adjusted_gross_income"
