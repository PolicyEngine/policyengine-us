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
        cdcc = parameters(period).gov.irs.credits.cdcc
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        capped_count_cdcc_eligible = tax_unit(
            "capped_count_cdcc_eligible", period
        )
        eligible_capped_expenses = min_(
            expenses, cdcc.max * capped_count_cdcc_eligible
        )
        # cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
