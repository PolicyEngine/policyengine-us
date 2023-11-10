from policyengine_us.model_api import *


class hi_disabled_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii disabled exemptions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        # Compute the exemptions if head or spouse have a disability.
        # In this case, the disabled head/spouse gets a higher amount, but they cannot claim dependent
        # exemptions.
        # Start by computing for the head.
        p = parameters(period).gov.states.hi.tax.income.exemptions
        aged_head = (tax_unit("age_head", period) >= p.aged_threshold).astype(
            int
        )
        aged_spouse = (
            tax_unit("age_spouse", period) >= p.aged_threshold
        ).astype(int)
        disabled_head = tax_unit("head_is_disabled", period)
        disabled_exemption_disabled_head = disabled_head * p.disabled
        disabled_exemption_non_disabled_head = p.base * (1 + aged_head)
        disabled_exemption_head = max_(
            disabled_exemption_disabled_head,
            disabled_exemption_non_disabled_head,
        )
        # Same for spouse.
        disabled_spouse = tax_unit("spouse_is_disabled", period)
        disabled_exemption_disabled_spouse = disabled_spouse * p.disabled
        disabled_exemption_non_disabled_spouse = p.base * (1 + aged_spouse)
        disabled_exemption_spouse = max_(
            disabled_exemption_disabled_spouse,
            disabled_exemption_non_disabled_spouse,
        )

        return disabled_exemption_head + disabled_exemption_spouse
