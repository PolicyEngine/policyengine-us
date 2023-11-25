from policyengine_us.model_api import *


class sc_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina taxable income"
    defined_for = StateCode.SC
    unit = USD
    definition_period = YEAR

    adds = ["sc_federal_taxable_income_without_salt_deduction", "sc_additions"]
    subtracts = ["sc_subtractions"]
