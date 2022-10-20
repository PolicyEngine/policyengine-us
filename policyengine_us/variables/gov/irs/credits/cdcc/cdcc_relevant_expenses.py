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
        # First, cap based on the number of eligible care receivers
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        cdcc = parameters(period).gov.irs.credits.cdcc
        count_eligible = min_(
            cdcc.eligibility.max, tax_unit("count_cdcc_eligible", period)
        )
        eligible_capped_expenses = min_(expenses, cdcc.max * count_eligible)
        # Then, cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
