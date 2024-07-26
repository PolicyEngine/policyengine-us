from policyengine_us.model_api import *


class medical_expense(Variable):
    value_type = float
    entity = Person
    label = "Total medical expenses"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.adjusted_gross_income"

    adds = ["health_insurance_premiums", "medical_out_of_pocket_expenses"]
