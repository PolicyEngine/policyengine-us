from policyengine_us.model_api import *


class ut_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah taxable income"
    unit = USD
    documentation = "Form TC-40, line 9"
    definition_period = YEAR
    defined_for = StateCode.UT

    adds = ["ut_total_income"]
    subtracts = ["ut_subtractions", "ut_state_tax_refund"]
