from policyengine_us.model_api import *


class mn_claim_of_right_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota claim of right credit"
    unit = USD
    documentation = (
        "When Minnesota tax is computed under the credit method of Minn. "
        "Stat. 290.07, subdivision 4, the decrease in the earlier year's "
        "Minnesota tax from excluding the repaid income. Any excess over the "
        "year's tax is treated as a payment and refunded (290.07, subdivision "
        "4). Reported on Schedule M1REF, line 11."
    )
    definition_period = YEAR
    reference = (
        # Minn. Stat. 290.07, subdivision 4
        "https://www.revisor.mn.gov/statutes/cite/290.07",
        # 2025 Schedule M1REF, line 11
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1ref-25.pdf#page=3",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("mn_claim_of_right_eligible", period)
        credit_applies = tax_unit("mn_claim_of_right_credit_applies", period)
        person = tax_unit.members
        decrease = person("mn_claim_of_right_prior_year_tax_decrease", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        prior_year_tax_decrease = tax_unit.sum(decrease * head_or_spouse)
        return where(eligible & credit_applies, prior_year_tax_decrease, 0)
