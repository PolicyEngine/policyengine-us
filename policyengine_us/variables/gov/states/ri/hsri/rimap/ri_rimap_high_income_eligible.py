from policyengine_us.model_api import *


class ri_rimap_high_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Rhode Island Marketplace Affordability Program above 400% of the federal poverty line"
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/statutes/TITLE42/42-157.2/42-157.2-4.htm",
        "https://healthsourceri.com/wp-content/uploads/2027-RIMAP-Final-Parameters.pdf#page=3",
        "https://www.law.cornell.edu/uscode/text/26/36B#c_1",
    )
    documentation = (
        "A tax unit qualifies for the Rhode Island Marketplace Affordability "
        "Program above 400% of the federal poverty line when the program is "
        "in effect, household income is above that floor, and income is the "
        "only reason it is ineligible for the federal premium tax credit "
        "(R.I. Gen. Laws 42-157.2-4(c)(1)): at least one member of the "
        "credit's tax family is enrolled through HealthSource RI, which "
        "carries the credit's immigration, TIN and other-coverage "
        "conditions, the tax unit does not file separately, and it files a "
        "return. Lawfully present immigrants whom federal law bars from the "
        "credit from 2027 therefore do not qualify."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.hsri.rimap
        # Every federal credit condition except income: Marketplace
        # enrollment within the credit's tax family (26 U.S.C. 36B(c)(1)(D)),
        # including the immigration, TIN and other-coverage conditions of
        # is_aca_marketplace_enrollee, and the married-filing-separately
        # exclusion. is_aca_ptc_eligible itself fails here, because its
        # income test stops at 400% of the poverty line.
        enrolled = add(tax_unit, period, ["is_aca_coverage_family_member"]) > 0
        filing_status = tax_unit("filing_status", period)
        not_separate = filing_status != filing_status.possible_values.SEPARATE
        # The federal credit requires a return (26 U.S.C. 36B(a)). No credit
        # is due above 400% of the poverty line, so taking up coverage gives
        # no reason to file; only filing for another reason counts, as for
        # New Mexico's Middle Income Household component.
        is_filer = tax_unit("tax_unit_is_filer", period)
        ratio = tax_unit("ri_rimap_fpl_ratio", period)
        income_eligible = ratio > p.high_income.fpl_floor
        return p.in_effect & enrolled & not_separate & is_filer & income_eligible
