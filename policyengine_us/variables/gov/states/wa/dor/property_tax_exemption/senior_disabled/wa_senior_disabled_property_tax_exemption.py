from policyengine_us.model_api import *


def regular_exempt_assessed_value(assessed_value, tier, benefit):
    # RCW 84.36.381(5)(b) sets a floor and percentage for tiers 1 and 2,
    # and an additional valuation cap for tier 2.
    tier_1_exempt_value = min_(
        max_(
            benefit.tier_1.dollar_floor,
            assessed_value * benefit.tier_1.valuation_pct,
        ),
        assessed_value,
    )
    tier_2_exempt_value = min_(
        min_(
            max_(
                benefit.tier_2.dollar_floor,
                assessed_value * benefit.tier_2.valuation_pct,
            ),
            benefit.tier_2.valuation_cap,
        ),
        assessed_value,
    )
    return select([tier == 1, tier == 2], [tier_1_exempt_value, tier_2_exempt_value])


class wa_senior_disabled_property_tax_exemption(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Washington Senior Citizens and Disabled Persons Property Tax Exemption"
    definition_period = YEAR
    defined_for = "wa_pte_eligible"
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.381",
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.383",
        "https://dor.wa.gov/sites/default/files/2022-02/PTExemption_Senior.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.wa.dor.property_tax_exemption.senior_disabled.benefit
        annual_taxes = add(tax_unit, period, ["real_estate_taxes"])
        assessed_value = add(tax_unit, period, ["assessed_property_value"])
        tier = tax_unit("wa_pte_tier", period)
        # RCW 84.36.381(5)(a): every qualifying tier is exempt from excess
        # levies, the state property tax under RCW 84.52.065, and any
        # RCW 84.55.050 lid-lift portion that named this exemption. Modeled
        # as a statewide-average share of the total property tax bill.
        full_exempt = annual_taxes * p.tier_3_exempt_share
        # The residual share is the regular property tax. Convert it to an
        # effective millage using the assessed value of the residence so the
        # valuation-based tier 1 / tier 2 exemptions can be priced.
        regular_taxes = annual_taxes * (1 - p.tier_3_exempt_share)
        regular_rate = where(
            assessed_value > 0,
            regular_taxes / max_(assessed_value, 1),
            0,
        )
        exempt_value = regular_exempt_assessed_value(assessed_value, tier, p)
        tier_1_or_2 = (tier == 1) | (tier == 2)
        return select(
            [tier_1_or_2, tier == 3],
            [full_exempt + exempt_value * regular_rate, full_exempt],
            default=0,
        )
