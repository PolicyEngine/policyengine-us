from policyengine_us.model_api import *


class ut_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah taxable income"
    unit = USD
    documentation = "Form TC-40, line 9"
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://tax.utah.gov/forms/2021/tc-40.pdf#page=1"

    adds = ["ut_total_income"]
    subtracts = ["ut_subtractions", "ut_state_tax_refund"]
