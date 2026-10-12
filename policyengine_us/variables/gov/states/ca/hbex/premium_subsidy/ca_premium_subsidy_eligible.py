from policyengine_us.model_api import *


class ca_premium_subsidy_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the California Premium Subsidy"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        # 2026 Program Design (Final): eligibility bands and the applicable
        # return filer definition at Program Design (d)(7).
        "https://board.coveredca.com/meetings/2025/July%2028,%202025/CoveredCA_2026_Premium_Subsidy_Program_Design_Final.pdf#page=1",
        "https://board.coveredca.com/meetings/2025/July%2028,%202025/CoveredCA_2026_Premium_Subsidy_Program_Design_Final.pdf#page=2",
        # GC Title 25 Section 100805 authorizes the subsidy and disclaims the
        # federal income requirements; Section 100810 defines eligibility.
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=GOV&sectionNum=100805.",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=GOV&sectionNum=100810.",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.hbex.premium_subsidy
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC. GC
        # Section 100805(b) disclaims the federal income requirements ("shall
        # not be subject to the income requirements"), so the inherited
        # is_aca_ptc_eligible gate is relied on only for its non-income
        # conditions: on-Marketplace enrollment (pays_aca_premium) and the
        # married-filing-separately exclusion. The income component of that
        # federal gate is an FPL-band test (ptc_income_eligibility), not a
        # required-contribution income test; it is non-binding here only while
        # the California band ([fpl_floor, fpl_limit]) is a subset of the
        # federal [1.00, 4.00) band. Should California ever band above 400%
        # FPL, this must be decomposed to (pays_aca_premium & ~MFS) plus the
        # California band. The unmodeled 26 CFR 1.36B-2(b)(2)(ii)-(v) MFS
        # exceptions (abandoned-spouse, domestic-abuse relief) are not applied.
        aptc_eligible = add(tax_unit, period, ["is_aca_ptc_eligible"]) > 0
        magi_frac = tax_unit("aca_magi_fraction", period)
        income_eligible = (magi_frac >= p.fpl_floor) & (magi_frac <= p.fpl_limit)
        # An applicable return filer (Program Design (d)(7); GC
        # Section 100810(a)(6)) must file a California return, so the tax unit
        # must be a filer. This gate replaces reliance on the federal 100% FPL
        # floor exception: the federal PTC gate admits a below-poverty
        # immigration exception that the applicable-return-filer definition
        # excludes. Dependents claimed by another filer do not form separate
        # claiming units in the model, so the dependent exclusion is structural.
        is_filer = tax_unit("tax_unit_is_filer", period)
        return in_effect & aptc_eligible & income_eligible & is_filer
