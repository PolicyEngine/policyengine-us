from policyengine_us.model_api import *


class taxable_pension_income(Variable):
    value_type = float
    entity = Person
    label = "taxable pension income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.taxable_pension_income"

    adds = ["taxable_public_pension_income", "taxable_private_pension_income"]
