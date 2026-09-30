from policyengine_us.model_api import *


class nyc_school_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC income used for school tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"
    reference = (
        # NY Tax Law § 606(ggg)(2)
        "https://www.nysenate.gov/legislation/laws/TAX/606",
        # NY Real Property Tax Law § 425(4)(b)(ii)
        "https://www.nysenate.gov/legislation/laws/RPT/425",
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=20",
    )

    def formula(tax_unit, period, parameters):
        # The credit uses income as defined in RPTL § 425(4)(b)(ii): federal
        # adjusted gross income reduced by distributions from individual
        # retirement accounts and annuities, to the extent included in
        # federal adjusted gross income (IT-201 line 19 minus line 9).
        # Recomputed federal AGI is not modeled separately.
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.school
        person = tax_unit.members
        # Federal gross income excludes dependents' income and negative
        # amounts, so only those distributions are included in AGI.
        not_dependent = ~person("is_tax_unit_dependent", period)
        ira_distributions = add(person, period, p.ira_distribution_sources)
        included_ira_distributions = tax_unit.sum(
            not_dependent * max_(0, ira_distributions)
        )
        return agi - included_ira_distributions
