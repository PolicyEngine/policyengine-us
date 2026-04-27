from policyengine_us.model_api import *


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
        annual_taxes = tax_unit("real_estate_taxes", period)
        tier = tax_unit("wa_pte_tier", period)
        p = parameters(
            period
        ).gov.states.wa.dor.property_tax_exemption.senior_disabled.benefit
        rate = select(
            [tier == 1, tier == 2, tier == 3],
            [
                p.tier_1_reduction_rate,
                p.tier_2_reduction_rate,
                p.tier_3_reduction_rate,
            ],
            default=0,
        )
        return annual_taxes * rate
