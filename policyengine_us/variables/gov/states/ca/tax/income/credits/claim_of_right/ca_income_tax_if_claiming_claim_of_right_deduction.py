from policyengine_us.model_api import *


class ca_income_tax_if_claiming_claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California income tax under the claim of right deduction method"
    unit = USD
    documentation = (
        "California income tax computed with a deduction for the repayment of "
        "claim of right income (Cal. Rev. & Tax. Code 17049)."
    )
    definition_period = YEAR
    reference = "https://www.leginfo.ca.gov/pub/05-06/bill/asm/ab_1751-1800/ab_1767_bill_20050922_chaptered.html"
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        branch = get_override_branch(
            tax_unit.simulation,
            "ca_claim_of_right_deduction",
            period,
            {"ca_claim_of_right_credit_applies": np.zeros(tax_unit.count, dtype=bool)},
        )
        return branch.calculate("ca_income_tax", period)
