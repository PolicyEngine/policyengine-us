from policyengine_us.model_api import *


class md_premium_assistance_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Maryland Premium Assistance"
    definition_period = YEAR
    defined_for = StateCode.MD
    # COMAR 14.35.21.03 (eligibility) is on page 5 of the codified chapter,
    # permanent effective 2025-10-13. The emergency PDF (25-134E) expired
    # 2026-01-06. HGO briefing p.58 documents the all-ages eligibility design.
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/14.35.21#page=5",
        "https://mgaleg.maryland.gov/meeting_material/2025/hgo%20-%20134051066649659653%20-%20Combined%20MHBE.MIA%20slides_10.16.2025%20briefing%20to%20HGO&Finance.pdf#page=58",
    )
    # A tax unit is eligible for Maryland Premium Assistance when the program
    # is in effect, at least one member is eligible for the federal ACA
    # premium tax credit, and household income is at or below the federal
    # poverty line limit.

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.mhbe.premium_assistance
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC.
        aptc_eligible = add(tax_unit, period, ["is_aca_ptc_eligible"]) > 0
        magi_frac = tax_unit("aca_magi_fraction", period)
        income_eligible = magi_frac <= p.fpl_limit
        return in_effect & aptc_eligible & income_eligible
