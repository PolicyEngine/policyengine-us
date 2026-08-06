from policyengine_us.model_api import *


class ca_premium_subsidy_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the California Premium Subsidy"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://board.coveredca.com/meetings/2025/July%2028,%202025/CoveredCA_2026_Premium_Subsidy_Program_Design_Final.pdf#page=1",
        "https://board.coveredca.com/meetings/2025/July%2028,%202025/CoveredCA_2026_Premium_Subsidy_Program_Design_Final.pdf#page=2",
        "https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=GOV&division=&title=25.&part=&chapter=&article=",
    )
    documentation = (
        "A tax unit is eligible for the California Premium Subsidy when the "
        "program is in effect, at least one member is eligible for the federal "
        "ACA premium tax credit (which embeds on-Marketplace enrollment, the "
        "married-filing-separately exclusion, and the federal required-"
        "contribution income test), and household income is at or above the "
        "poverty-line floor and at or below the poverty-line limit. The "
        "explicit 100% floor is applied here rather than relying on federal "
        "PTC eligibility, because the federal gate admits the below-poverty "
        "immigration exception that the California statutory definition of an "
        "applicable return filer excludes. Individuals claimed as dependents "
        "of another filer do not form separate claiming units in the model, "
        "so the dependent exclusion is handled structurally."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.hbex.premium_subsidy
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC. This
        # gate embeds on-Marketplace enrollment (pays_aca_premium), the MFS
        # exclusion, and the federal required-contribution income test.
        aptc_eligible = add(tax_unit, period, ["is_aca_ptc_eligible"]) > 0
        magi_frac = tax_unit("aca_magi_fraction", period)
        income_eligible = (magi_frac >= p.fpl_floor) & (magi_frac <= p.fpl_limit)
        return in_effect & aptc_eligible & income_eligible
