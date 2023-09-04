from policyengine_us.model_api import *


class nc_standard_or_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina standard or itemized deductions amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ncdor.gov/2021-d-401-individual-income-tax-instructions/open#page=14"
        "https://www.ncdor.gov/2022-d-401-individual-income-tax-instructions/open#page=14"
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        # From above instructions for Line 11:
        #   You may deduct from federal adjusted gross income either
        #   the N.C. standard deduction or N.C. itemized deductions.
        #   In most cases, your state income tax will be less if you
        #   take the larger of your N.C. itemized deductions or your
        #   N.C. standard deduction.
        stded = tax_unit("nc_standard_deduction", period)
        itded = tax_unit("nc_itemized_deductions", period)
        return max_(stded, itded)
