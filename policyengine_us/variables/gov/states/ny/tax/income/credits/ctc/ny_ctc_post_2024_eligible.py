from policyengine_us.model_api import *


class ny_ctc_post_2024_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "NY CTC post-2024 eligibility"
    documentation = (
        "Whether the tax unit is eligible for NY CTC under post-2024 rules"
    )
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc

        # Only eligible if post-2024 rules are in effect
        if not p.ctc_ny_in_effect:
            return False

        person = tax_unit.members
        age = person("age", period)

        # Check if we have qualifying children for post-2024 rules
        qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
        qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)

        # Check if any children fall within the post-2024 age ranges
        young_children = qualifies & (
            age <= p.post_2024.young_child_age_threshold
        )
        older_children = (
            qualifies
            & (age >= p.post_2024.older_child_age_min)
            & (age <= p.post_2024.older_child_age_max)
        )

        total_qualifying_children = tax_unit.sum(
            young_children
        ) + tax_unit.sum(older_children)
        return total_qualifying_children > 0
