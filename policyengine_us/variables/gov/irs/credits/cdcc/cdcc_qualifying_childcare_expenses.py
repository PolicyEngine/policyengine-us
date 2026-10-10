from policyengine_us.model_api import *


class cdcc_qualifying_childcare_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Childcare expenses that count for the child and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/21#b_2_A",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )

    def formula(tax_unit, period, parameters):
        childcare = tax_unit("tax_unit_childcare_expenses", period)
        # IRC 21(b)(2)(A)(ii) counts only expenses "for the care of a
        # qualifying individual". A return on which a filer can be claimed as
        # a dependent (outside the claimant filing exception) has no
        # qualifying child under 13 unless the child is incapable of
        # self-care, so its childcare expenses do not count. The model records
        # childcare as a tax-unit total, so it cannot leave out one child's
        # share when another child qualifies.
        p = parameters(period).gov.irs.credits.cdcc.eligibility
        person = tax_unit.members
        qualifying_child = person("is_cdcc_eligible", period) & (
            person("age", period) < p.child_age
        )
        dependent_filer = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        return where(dependent_filer & ~tax_unit.any(qualifying_child), 0, childcare)
