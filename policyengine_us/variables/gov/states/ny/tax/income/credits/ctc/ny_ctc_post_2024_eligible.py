from policyengine_us.model_api import *


class ny_ctc_post_2024_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New York CTC post-2024 eligibility"
    documentation = "Whether the tax unit is eligible for New York CTC under post-2024 rules"
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc

        # Only eligible if post-2024 rules are in effect
        if not p.post_2024.in_effect:
            return False

        person = tax_unit.members
        age = person("age", period)

        # Check if we have qualifying children for post-2024 rules
        qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
        qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)

        # Check if any children get a non-zero credit amount
        credit_by_age = p.post_2024.amount.calc(age)
        qualifying_children = qualifies & (credit_by_age > 0)

        total_qualifying_children = tax_unit.sum(qualifying_children)
        return total_qualifying_children > 0
