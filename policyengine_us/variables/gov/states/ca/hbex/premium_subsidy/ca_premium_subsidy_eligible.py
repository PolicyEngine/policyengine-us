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
        # PDF pages 1-2
        "https://board.coveredca.com/meetings/2025/July%2028,%202025/CoveredCA_2026_Premium_Subsidy_Program_Design_Final.pdf#page=1",
        # Final 2027 Program Design, (d)(7): "at or below 200 percent".
        "https://hbex.coveredca.com/data-research/Final-2027-California-Premium-Subsidy-Program-Design.pdf#page=2",
        # FTB 3849 Table 1-2 (predecessor program): exact percentage decides
        # the band edge; the truncated percentage only drives the rate lookup.
        "https://www.ftb.ca.gov/forms/2020/2020-3849-instructions.pdf#page=6",
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
        # Program Design (d)(7) bounds household income "at or above 100
        # percent" and "at or below" 165 percent (PY2026) or 200 percent
        # (PY2027) of the FPL. Test the exact ratio, not the truncated
        # aca_magi_fraction: truncation maps 165.00%-165.99% to 1.65, which
        # would admit incomes above 165%. FTB 3849 Table 1-2 (2020) likewise
        # decides band edges on the exact percentage.
        magi = max_(tax_unit("aca_magi", period), 0)
        fpg = tax_unit("tax_unit_fpg", period.last_year)
        # Divide in float64: a float32 quotient can round a ratio just above
        # a limit down onto it.
        exact_magi_frac = magi.astype(np.float64) / fpg
        income_eligible = (exact_magi_frac >= p.fpl_floor) & (
            exact_magi_frac <= p.fpl_limit
        )
        # An applicable return filer (Program Design (d)(7); GC
        # Section 100810(a)(6)) must file a California return, so the tax unit
        # must be a filer. This gate replaces reliance on the federal 100% FPL
        # floor exception: the federal PTC gate admits a below-poverty
        # immigration exception that the applicable-return-filer definition
        # excludes. Dependents claimed by another filer do not form separate
        # claiming units in the model, so the dependent exclusion is structural.
        is_filer = tax_unit("files_return_for_aca_ptc", period)
        return in_effect & aptc_eligible & income_eligible & is_filer
