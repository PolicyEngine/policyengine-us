from policyengine_us.model_api import *


class medicaid_irs_gross_income(Variable):
    value_type = float
    entity = Person
    label = "Gross income used for Medicaid MAGI filing-threshold checks"
    unit = USD
    documentation = (
        "The person's own gross income. Social Security counts only to the "
        "extent section 86 taxes it: taxable_social_security gives the head "
        "and spouse their shares of their return's taxable benefits, and a "
        "tax unit dependent's benefits are taxed on the dependent's own "
        "return (dependent_taxable_social_security)."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/61",
        "https://www.law.cornell.edu/cfr/text/42/435.603#d_2",
        # IRS Pub. 501 (2025), Table 2: a dependent's unearned income
        # includes taxable Social Security benefits.
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=4",
        # IRS Pub. 915 (2025), "Who is taxed": a child's benefits are added
        # to the child's own income.
        "https://www.irs.gov/pub/irs-prior/p915--2025.pdf#page=5",
    )

    def formula(person, period, parameters):
        sources = parameters(period).gov.irs.gross_income.sources
        total = 0
        for source in sources:
            total += max_(0, add(person, period, [source]))
        if "taxable_social_security" in sources:
            # taxable_social_security is zero for a tax unit dependent.
            total += person("dependent_taxable_social_security", period)
        return total
