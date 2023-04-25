from policyengine_us.model_api import *


class ut_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah taxable income"
    unit = USD
    documentation = "Form TC-40, line 9"
    definition_period = YEAR
    adds = ["ut_total_income"]
    defined_for = StateCode.UT
    subtracts = ["ut_subtractions_from_income", "ut_state_tax_refund"]
