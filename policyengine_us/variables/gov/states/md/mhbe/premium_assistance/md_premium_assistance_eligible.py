from policyengine_us.model_api import *


class md_premium_assistance_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Maryland Premium Assistance"
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/pubs/committee/AELR/25-134E-Regulation.pdf#page=5",
        "https://www.marylandhbe.com/wp-content/uploads/2025/07/Final-2026-State-Subsidy-and-Reinsurance-Parameters-Board-7-21-25-1.pdf#page=14",
    )
    documentation = (
        "A tax unit is eligible for Maryland Premium Assistance when the "
        "program is in effect, at least one member is eligible for the "
        "federal ACA premium tax credit, and household income is at or below "
        "the federal poverty line limit."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.mhbe.premium_assistance
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC.
        aptc_eligible = add(tax_unit, period, ["is_aca_ptc_eligible"]) > 0
        magi_frac = tax_unit("aca_magi_fraction", period)
        income_eligible = magi_frac <= p.fpl_limit
        return in_effect & aptc_eligible & income_eligible
