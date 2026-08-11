from policyengine_us.model_api import *


class co_premium_assistance_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Colorado Premium Assistance"
    definition_period = YEAR
    defined_for = StateCode.CO
    # A tax unit is eligible for Colorado Premium Assistance when the program is
    # in effect, at least one member is eligible for the federal ACA premium tax
    # credit (which embeds on-Marketplace enrollment and the required-
    # contribution income test), and household income is at or below the 400%
    # federal poverty line ceiling. Regulation 4-2-78 Section 4.C sets a 400%-
    # inclusive ceiling with no explicit lower bound.
    reference = (
        # Amended Regulation 4-2-78 (3 CCR 702-4), Section 5.B and the 400%-
        # inclusive income ceiling in Section 4.C. Adopted via the DOI notice
        # below (which returns HTTP 403 to non-browser user agents).
        "https://drive.google.com/file/d/1GkpvQTauvS4hr97_CSfkSEQCnoYjqrJI/view",
        "https://doi.colorado.gov/announcements/notice-of-adoption-amended-regulation-4-2-78-concerning-health-insurance",
        # Enrolled HB25B-1006, Section 10-16-1207(5) (rule authority) and
        # Section 10-16-1205(1)(b)(II) (payment authority).
        "https://content.leg.colorado.gov/sites/default/files/documents/2025B/bills/2025b_1006_enr.pdf",
        "https://connectforhealthco.com/new-customers/tips-for-choosing-a-plan/colorado-premium-assistance/",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.doi.premium_assistance
        if not p.in_effect:
            return False
        # At least one member must be eligible for the federal ACA PTC. This
        # gate embeds on-Marketplace enrollment (pays_aca_premium), the MFS
        # exclusion, immigration/TIN status, and the required-contribution
        # income test.
        aptc_eligible = tax_unit.any(tax_unit.members("is_aca_ptc_eligible", period))
        # Regulation 4-2-78 Section 4.C caps eligibility at 400% FPL inclusive
        # and states no lower bound.
        magi_frac = tax_unit("aca_magi_fraction", period)
        income_eligible = magi_frac <= p.fpl_limit.upper
        return aptc_eligible & income_eligible
