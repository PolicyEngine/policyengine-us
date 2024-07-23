from policyengine_us.model_api import *


class educator_expense(Variable):
    value_type = float
    entity = Person
    label = "Educator expenses"
    unit = USD
    documentation = (
        "Expenses necessary for carrying out educator-related duties."
    )
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.adjusted_gross_income"
