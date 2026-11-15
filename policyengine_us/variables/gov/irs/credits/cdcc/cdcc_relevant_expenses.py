from policyengine_us.model_api import *


class cdcc_relevant_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC-relevant care expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/21#c",
        "https://www.law.cornell.edu/uscode/text/26/21#d_1",
        "https://www.irs.gov/pub/irs-prior/f2441--2017.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/f2441--2021.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/f2441--2025.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        # Form 2441 line 30 excludes expenses paid with the benefits already
        # excluded under section 129; line 29 separately reduces the dollar cap.
        expenses = max_(
            tax_unit("cdcc_qualified_care_expenses", period)
            - tax_unit("dependent_care_assistance_exclusion", period),
            0,
        )
        cdcc_limit = tax_unit("cdcc_limit", period)
        eligible_capped_expenses = min_(expenses, cdcc_limit)
        # cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
