from policyengine_us.model_api import *


class hi_income_tax_if_claiming_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii income tax with the claim of right tax credit"
    unit = USD
    documentation = (
        "Hawaii income tax computed without a deduction for the repayment of "
        "claim of right income, less the decrease in prior-year Hawaii tax "
        "(section 1341(a)(5) as operative in Hawaii)."
    )
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/forms/2025/n364_i.pdf"
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        branch = get_override_branch(
            tax_unit.simulation,
            "hi_claim_of_right_credit",
            period,
            {"hi_claim_of_right_credit_applies": np.ones(tax_unit.count, dtype=bool)},
        )
        return branch.calculate("hi_income_tax", period)
