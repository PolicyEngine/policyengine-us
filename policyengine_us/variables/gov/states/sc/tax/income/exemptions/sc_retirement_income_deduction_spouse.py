from policyengine_us.model_api import *


class sc_retirement_income_deduction_spouse(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina retirement income deduction for spouse"
    defined_for = StateCode.SC
    unit = USD
    definition_period = YEAR
