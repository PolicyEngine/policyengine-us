from policyengine_us.model_api import *


class charitable_non_cash_donations(Variable):
    value_type = float
    entity = Person
    label = "Charitable donations (non-cash)"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.adjusted_gross_income"
