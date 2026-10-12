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
    )

    def formula(tax_unit, period, parameters):
        # Section 21 employment-related expenses cover care for any qualifying
        # individual: childcare for children under 13
        # (tax_unit_childcare_expenses) plus care for a disabled qualifying
        # individual of any age — a disabled adult dependent or spouse
        # (care_expenses, a person-level yearly input).
        childcare = tax_unit("tax_unit_childcare_expenses", period)
        adult_care = add(tax_unit, period, ["care_expenses"])
        expenses = childcare + adult_care
        cdcc_limit = tax_unit("cdcc_limit", period)
        eligible_capped_expenses = min_(expenses, cdcc_limit)
        # cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
