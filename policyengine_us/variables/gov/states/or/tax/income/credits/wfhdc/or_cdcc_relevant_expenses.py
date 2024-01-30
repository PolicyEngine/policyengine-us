from policyengine_us.model_api import *


class or_cdcc_relevant_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon working family household and dependent care expenses"
    unit = USD
    definition_period = YEAR
    reference = "https://oregon.public.law/statutes/ors_315.264"

    def formula(tax_unit, period, parameters):
        p_cdcc = parameters(period).gov.irs.credits.cdcc
        p_or = parameters(period).gov.states["or"].tax.income.credits.wfhdc

        # First, cap based on the number of eligible care receivers
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        capped_eligible_people = tax_unit("capped_count_cdcc_eligible", period)

        total_max_amount = p_or.cap * capped_eligible_people
        capped_eligible_expenses = min_(expenses, total_max_amount)

        return min_(
            capped_eligible_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
