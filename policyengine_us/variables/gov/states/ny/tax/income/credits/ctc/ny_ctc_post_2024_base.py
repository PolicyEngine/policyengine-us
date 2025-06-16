from policyengine_us.model_api import *


class ny_ctc_post_2024_base(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CTC post-2024 base amount"
    documentation = "Base NY CTC amount before phase-out under post-2024 rules"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)
    defined_for = "ny_ctc_post_2024_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        person = tax_unit.members
        age = person("age", period)

        # Post-2024 CTC rules (2025-2027)
        qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
        qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)

        # Age-based amounts: young vs older children
        young_children = qualifies & (
            age <= p.post_2024.young_child_age_threshold
        )
        older_children = (
            qualifies
            & (age >= p.post_2024.older_child_age_min)
            & (age <= p.post_2024.older_child_age_max)
        )

        young_child_credit = (
            tax_unit.sum(young_children) * p.post_2024.young_child_amount
        )
        older_child_credit = (
            tax_unit.sum(older_children) * p.post_2024.older_child_amount
        )
        return young_child_credit + older_child_credit
