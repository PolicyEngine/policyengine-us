from policyengine_us.model_api import *


class wi_income_tax_if_claiming_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin income tax if taking the claim of right credit"
    unit = USD
    documentation = (
        "Wisconsin income tax computed without subtracting the repayment of "
        "claim of right income, less the decrease in the earlier year's "
        "Wisconsin tax from excluding the repaid income (Wis. Stat. 71.07(1))."
    )
    definition_period = YEAR
    reference = "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/1"
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        branch = get_override_branch(
            tax_unit.simulation,
            "wi_claim_of_right_credit",
            period,
            {"wi_claim_of_right_credit_applies": np.ones(tax_unit.count, dtype=bool)},
        )
        return branch.calculate("wi_income_tax", period)
