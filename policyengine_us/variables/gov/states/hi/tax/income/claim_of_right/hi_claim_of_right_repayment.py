from policyengine_us.model_api import *


class hi_claim_of_right_repayment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii claim of right repayment"
    unit = USD
    documentation = (
        "Total repaid this year by the head and spouse of income Hawaii "
        "taxed in an earlier year under a claim of right (Form N-364, line "
        "1). Dependents' repayments belong on their own returns."
    )
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/forms/2025/n364_i.pdf"
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        repayment = person("claim_of_right_repayment", period)
        excluded = person("hi_claim_of_right_repayment_excluded_from_income", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(max_(repayment - excluded, 0) * head_or_spouse)
