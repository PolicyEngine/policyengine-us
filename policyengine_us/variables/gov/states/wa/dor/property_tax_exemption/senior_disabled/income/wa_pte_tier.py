from policyengine_us.model_api import *


def property_tax_exemption_tier(income, county, thresholds):
    return select(
        [
            income <= thresholds.tier_1[county],
            income <= thresholds.tier_2[county],
            income <= thresholds.tier_3[county],
        ],
        [1, 2, 3],
        default=0,
    )


class wa_pte_tier(Variable):
    value_type = int
    entity = TaxUnit
    label = "Washington Senior/Disabled Property Tax Exemption tier"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.381",
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.383",
        "https://dor.wa.gov/sites/default/files/2022-02/PTExemption_Senior.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        income = tax_unit("wa_pte_combined_disposable_income", period)
        county = tax_unit.household("county_str", period)
        p = parameters(
            period
        ).gov.states.wa.dor.property_tax_exemption.senior_disabled.income.thresholds
        return property_tax_exemption_tier(income, county, p)
