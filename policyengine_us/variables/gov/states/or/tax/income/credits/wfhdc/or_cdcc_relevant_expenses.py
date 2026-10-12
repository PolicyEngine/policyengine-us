from policyengine_us.model_api import *


class or_cdcc_relevant_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon working family household and dependent care expenses"
    unit = USD
    definition_period = YEAR
    reference = "https://oregon.public.law/statutes/ors_315.264"
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        p_cdcc = parameters(period).gov.irs.credits.cdcc
        p_or = parameters(period).gov.states["or"].tax.income.credits.wfhdc

        # ORS 315.264(1)(a) covers expenses of a type allowable under IRC
        # §21: childcare plus care for a disabled adult qualifying
        # individual (care_expenses).
        childcare = tax_unit("tax_unit_childcare_expenses", period)
        adult_care = add(tax_unit, period, ["care_expenses"])
        expenses = childcare + adult_care
        # First, cap based on the number of eligible care receivers
        capped_eligible_people = tax_unit("capped_count_cdcc_eligible", period)

        total_max_amount = p_or.cap * capped_eligible_people
        capped_eligible_expenses = min_(expenses, total_max_amount)

        return min_(
            capped_eligible_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
