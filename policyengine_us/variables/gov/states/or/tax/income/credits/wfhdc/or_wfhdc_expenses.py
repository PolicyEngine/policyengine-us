from policyengine_us.model_api import *


class or_wfhdc_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon working family household and dependent care expenses"
    unit = USD
    definition_period = YEAR
    reference = "https://oregon.public.law/statutes/ors_315.264"

    def formula(tax_unit, period, parameters):
        # First, cap based on the number of eligible care receivers
        childcare_expenses = tax_unit("tax_unit_childcare_expenses", period)
        p_cdcc = parameters(period).gov.irs.credits.cdcc
        p_or = parameters(period).gov.states["or"].tax.income.credits.wfhdc
        eligible_people = min_(
            p_cdcc.eligibility.max, tax_unit("count_cdcc_eligible", period)
        )

        total_max_amount = p_or.cap * eligible_people
        eligible_capped_expenses = min_(childcare_expenses, total_max_amount)

        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
