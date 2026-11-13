from policyengine_us.model_api import *


class income_tax_if_claiming_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal income tax under section 1341(a)(5)"
    unit = USD
    documentation = (
        "Federal income tax computed without a deduction for the repayment of "
        "claim of right income, less the decrease in prior-year tax from "
        "excluding the repaid income (section 1341(a)(5))."
    )
    definition_period = YEAR
    reference = "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapQ-partV-sec1341.htm"

    def formula(tax_unit, period, parameters):
        branch = get_override_branch(
            tax_unit.simulation,
            "claim_of_right_credit",
            period,
            {"claim_of_right_credit_applies": np.ones(tax_unit.count, dtype=bool)},
            # A value the parent calculated in another branch reflects the
            # method that branch chose, so start from inputs only.
            inherit_calculated=False,
        )
        return branch.calculate("income_tax", period)
