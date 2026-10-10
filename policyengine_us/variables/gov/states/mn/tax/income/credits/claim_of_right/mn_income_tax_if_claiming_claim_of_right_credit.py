from policyengine_us.model_api import *


class mn_income_tax_if_claiming_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota income tax under the claim of right credit method"
    unit = USD
    documentation = (
        "Minnesota income tax computed without a deduction for the repayment "
        "of claim of right income, less the decrease in the earlier year's "
        "Minnesota tax from excluding the repaid income (Minn. Stat. 290.07, "
        "subdivision 4)."
    )
    definition_period = YEAR
    reference = "https://www.revisor.mn.gov/statutes/cite/290.07"
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        branch = get_override_branch(
            tax_unit.simulation,
            "mn_claim_of_right_credit",
            period,
            {"mn_claim_of_right_credit_applies": np.ones(tax_unit.count, dtype=bool)},
        )
        return branch.calculate("mn_income_tax", period)
