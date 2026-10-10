from policyengine_us.model_api import *


class mn_income_tax_if_claiming_claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota income tax under the claim of right deduction method"
    unit = USD
    documentation = (
        "Minnesota income tax computed with a deduction for the repayment of "
        "claim of right income (Minn. Stat. 290.07, subdivision 4)."
    )
    definition_period = YEAR
    reference = "https://www.revisor.mn.gov/statutes/cite/290.07"
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        branch = get_override_branch(
            tax_unit.simulation,
            "mn_claim_of_right_deduction",
            period,
            {"mn_claim_of_right_credit_applies": np.zeros(tax_unit.count, dtype=bool)},
        )
        return branch.calculate("mn_income_tax", period)
