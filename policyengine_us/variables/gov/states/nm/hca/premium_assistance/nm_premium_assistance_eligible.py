from policyengine_us.model_api import *


class nm_premium_assistance_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for base New Mexico Premium Assistance"
    definition_period = YEAR
    defined_for = StateCode.NM
    reference = (
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=4",
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=6",
    )
    documentation = (
        "A tax unit is eligible for base New Mexico Premium Assistance when "
        "the program is in effect, at least one member is eligible for the "
        "federal ACA premium tax credit (which embeds on-Marketplace "
        "enrollment and the required-contribution income test), and household "
        "income is at or below the federal poverty line limit."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.premium_assistance
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC. This
        # gate embeds on-Marketplace enrollment (pays_aca_premium), the MFS
        # exclusion, and the 100-400% FPL required-contribution income test.
        aptc_eligible = tax_unit.any(tax_unit.members("is_aca_ptc_eligible", period))
        magi_frac = tax_unit("aca_magi_fraction", period)
        income_eligible = magi_frac <= p.fpl_limit
        return in_effect & aptc_eligible & income_eligible
