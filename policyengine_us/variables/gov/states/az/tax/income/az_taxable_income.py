from policyengine_us.model_api import *


class az_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona taxable income"
    unit = USD
    reference = (
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140Ai.pdf#page=8",
        "https://www.azleg.gov/ars/43/01029.htm",
        # ITP 16-1, Example 1: taxable income without regard to the repayment
        "https://azdor.gov/sites/default/files/2023-03/PROCEDURES_INDIV_2016_ITP16-1.pdf#page=3",
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        az_agi = tax_unit("az_agi", period)
        deductions = tax_unit("az_deductions", period)
        # A.R.S. 43-1029(B) computes Arizona tax without the claim of right
        # repayment deduction. On the return, the federal deduction carried
        # into Arizona Schedule A offsets its addition to Arizona gross
        # income (A.R.S. 43-1021(9)). az_itemized_deductions leaves the
        # deduction out, so the addition is removed here: taxable income is
        # the same as without the repayment whichever deduction Arizona
        # allows (ITP 16-1, Example 1).
        claim_of_right_addition = tax_unit("az_claim_of_right_addition", period)
        return max_(0, az_agi - claim_of_right_addition - deductions)
