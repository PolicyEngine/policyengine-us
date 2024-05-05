from policyengine_us.model_api import *


class pre_tax_contributions(Variable):
    value_type = float
    entity = Person
    label = "Pre-tax contributions"
    unit = USD
    documentation = "Payroll deductions."
    definition_period = YEAR

    adds = "gov.irs.gross_income.pre_tax_contributions"
