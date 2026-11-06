from policyengine_us.model_api import *


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
        # defined_for masks the output but does not stop the formula from
        # running over every household, and the thresholds are keyed by
        # Washington county only. Households outside Washington, or with an
        # UNKNOWN county, are looked up under Adams County (the county the
        # model assigns a Washington household that gives none) so the lookup
        # cannot raise ParameterNotFoundError.
        county = tax_unit.household("county_str", period)
        in_wa = tax_unit.household("state_code_str", period) == "WA"
        county = where(in_wa & (county != "UNKNOWN"), county, "ADAMS_COUNTY_WA")
        p = parameters(
            period
        ).gov.states.wa.dor.property_tax_exemption.senior_disabled.income.thresholds
        return select(
            [
                income <= p.tier_1[county],
                income <= p.tier_2[county],
                income <= p.tier_3[county],
            ],
            [1, 2, 3],
            default=0,
        )
