from policyengine_us.model_api import *


class wi_income_tax_if_claiming_claim_of_right_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin income tax if subtracting the claim of right repayment"
    unit = USD
    documentation = (
        "Wisconsin income tax computed with the repayment of claim of right "
        "income subtracted from income (Wis. Stat. 71.05(6)(b)29)."
    )
    definition_period = YEAR
    reference = "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/29"
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        branch = get_override_branch(
            tax_unit.simulation,
            "wi_claim_of_right_subtraction",
            period,
            {"wi_claim_of_right_credit_applies": np.zeros(tax_unit.count, dtype=bool)},
        )
        return branch.calculate("wi_income_tax", period)
