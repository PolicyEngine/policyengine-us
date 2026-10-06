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
        # federal adjusted gross income (IT-201 line 19 minus line 9; the
        # 2022 instructions used recomputed federal AGI, line 19a, which is
        # not modeled separately).
        # Roth conversions are not identified as IRA-sourced, and individual
        # retirement annuity distributions recorded as pension income are not
        # identified separately, so both stay in income.
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.school
        person = tax_unit.members
        # Federal gross income excludes dependents' income, so only the
        # head's and spouse's distributions are included in AGI. It counts
        # each member's taxable retirement distributions (IRA, SEP, 401(k),
        # 403(b) and Keogh) as one source floored at zero, so the subtraction
        # is capped at that included amount. Taxable distributions are
        # non-negative, so the floor and cap only guard inputs.
        not_dependent = ~person("is_tax_unit_dependent", period)
        ira_distributions = add(person, period, p.ira_distribution_sources)
        retirement_distributions = person("taxable_retirement_distributions", period)
        included_ira_distributions = tax_unit.sum(
            not_dependent
            * min_(max_(0, ira_distributions), max_(0, retirement_distributions))
        )
        return agi - included_ira_distributions
