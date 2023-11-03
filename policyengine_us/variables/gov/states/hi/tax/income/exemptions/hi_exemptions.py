from policyengine_us.model_api import *


class hi_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii exemptions"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.exemptions
        # disability exemption
        disabled_head = tax_unit("head_is_disabled", period)
        disabled_spouse = tax_unit("spouse_is_disabled", period)
        # aged exemption
        aged_head = (tax_unit("age_head", period) >= p.age_threshold).astype(
            int
        )
        aged_spouse = (
            tax_unit("age_spouse", period) >= p.age_threshold
        ).astype(int)

        # Head can claim the disabled exemption if they are disabled.
        head_non_disabled_exemption = p.base + p.base * aged_head
        head_disabled_exemption = p.disabled * disabled_head
        head_exemption = max_(
            head_non_disabled_exemption, head_disabled_exemption
        )
        # Same for spouse.
        spouse_non_disabled_exemption = p.base + p.base * aged_spouse
        spouse_disabled_exemption = p.disabled * disabled_spouse
        spouse_exemption = max_(
            spouse_non_disabled_exemption, spouse_disabled_exemption
        )
        # Add dependent exemptions only if neither head nor spouse claims disabled exemptions.
        dependent_exemptions = tax_unit("tax_unit_dependents", period) * p.base
        # Check if using disabled exemptions (and forgoing dependent exemptions) increases total exemption value.
        exemptions_if_claiming_disabled = head_exemption + spouse_exemption
        exemptions_if_not_claiming_disabled = (
            head_non_disabled_exemption
            + spouse_non_disabled_exemption
            + dependent_exemptions
        )
        return max_(
            exemptions_if_claiming_disabled,
            exemptions_if_not_claiming_disabled,
        )
