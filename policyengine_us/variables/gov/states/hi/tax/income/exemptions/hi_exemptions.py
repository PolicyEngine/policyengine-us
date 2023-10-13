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
        exemp = tax_unit("exemptions", period)
        # disability exemption
        disabled_head = tax_unit("head_is_disabled", period).astype(int)
        disabled_spouse = tax_unit("spouse_is_disabled", period).astype(int)
        # aged exemption
        aged_head = (tax_unit("age_head", period) >= p.age_threshold).astype(
            int
        )
        aged_spouse = (
            tax_unit("age_spouse", period) >= p.age_threshold
        ).astype(int)

        # if the head or spouse has disabled exemption, aged exemption will be excluded from the total exemptions
        adjusted_exemp = where(
            disabled_head, exemp - disabled_head, exemp + aged_head
        )
        # exemp_base stores the normal exemptions other than disability exemptions
        # and the exemp_base will be multiply by 1_144
        exemp_base = where(
            disabled_spouse,
            max_(0, adjusted_exemp - disabled_spouse),
            adjusted_exemp + aged_spouse,
        )
        # disabled_exemptions will be multiplied by 7_000 instead
        disabled_exemptions = (disabled_head + disabled_spouse) * p.disabled
        exemption_base_amount = exemp_base * p.base

        return exemption_base_amount + disabled_exemptions
