from policyengine_us.model_api import *


class ri_rimap_low_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Rhode Island Marketplace Affordability Program below 200% of the federal poverty line"
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/statutes/TITLE42/42-157.2/42-157.2-4.htm",
        "https://webserver.rilegislature.gov/statutes/TITLE42/42-157.2/42-157.2-5.htm",
        # PDF pages 1, 3: the statutory eligibility criteria (p.1) and the
        # Plan Year 2027 Rhode Island Applicable Percentage Table (p.3).
        "https://healthsourceri.com/wp-content/uploads/2027-RIMAP-Final-Parameters.pdf#page=1",
        "https://www.law.cornell.edu/uscode/text/26/36B#a",
    )
    documentation = (
        "A tax unit qualifies for the main Rhode Island Marketplace "
        "Affordability Program subsidy when the program is in effect, at "
        "least one member is eligible for the federal premium tax credit "
        "and enrolled through HealthSource RI (R.I. Gen. Laws "
        "42-157.2-4(c)), the tax unit files the return that credit requires, "
        "and household income is below 200% of the federal poverty line, "
        "the last band with a Rhode Island applicable percentage in the "
        "Plan Year 2027 table. The federal credit's own income floor of "
        "100% of the poverty line applies through its eligibility test."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.hsri.rimap
        # R.I. Gen. Laws 42-157.2-4(c): determined eligible for the federal
        # premium tax credit and enrolled in coverage through the exchange.
        # is_aca_ptc_eligible covers Marketplace enrollment (pays_aca_premium),
        # immigration and TIN status, other coverage, the
        # married-filing-separately exclusion and the federal income test.
        aptc_eligible = add(tax_unit, period, ["is_aca_ptc_eligible"]) > 0
        # is_aca_ptc_eligible leaves out the federal credit's filing
        # requirement (26 U.S.C. 36B(a)); aca_ptc applies it through
        # files_return_for_aca_ptc, so apply it here too.
        is_filer = tax_unit("files_return_for_aca_ptc", period)
        ratio = tax_unit("ri_rimap_fpl_ratio", period)
        income_eligible = ratio < p.fpl_limit
        return p.in_effect & aptc_eligible & is_filer & income_eligible
