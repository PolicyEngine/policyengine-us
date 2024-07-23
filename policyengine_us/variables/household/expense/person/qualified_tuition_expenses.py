from policyengine_us.model_api import *


class qualified_tuition_expenses(Variable):
    value_type = float
    entity = Person
    label = "Qualified tuition expenses"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.adjusted_gross_income"
