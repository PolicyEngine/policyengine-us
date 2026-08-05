from policyengine_us.model_api import *


class co_premium_assistance_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Colorado Premium Assistance"
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = (
        "https://connectforhealthco.com/financial-help/colorado-premium-assistance/"
    )
    documentation = (
        "A tax unit is eligible for Colorado Premium Assistance when the "
        "program is in effect, at least one member is eligible for the federal "
        "ACA premium tax credit (which embeds on-Marketplace enrollment and "
        "the required-contribution income test), and household income is "
        "within the 100%-400% federal poverty line band. The $80/$29/5-member "
        "and 100-400% FPL design is administrative (Health Insurance "
        "Affordability Enterprise board / Connect for Health Colorado); the "
        "primary Connect for Health Colorado page 403's to bots, so the design "
        "is corroborated by Boulder County, healthinsurance.org, and ACA "
        "Signups."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.doi.premium_assistance
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC. This
        # gate embeds on-Marketplace enrollment (pays_aca_premium), the MFS
        # exclusion, immigration/TIN status, and the required-contribution
        # income test.
        aptc_eligible = tax_unit.any(tax_unit.members("is_aca_ptc_eligible", period))
        magi_frac = tax_unit("aca_magi_fraction", period)
        income_eligible = (magi_frac >= p.fpl_limit.lower) & (
            magi_frac <= p.fpl_limit.upper
        )
        return in_effect & aptc_eligible & income_eligible
