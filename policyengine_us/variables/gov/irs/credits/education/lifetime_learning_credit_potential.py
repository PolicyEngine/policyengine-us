from policyengine_us.model_api import *


class lifetime_learning_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Potential value of the Lifetime Learning Credit"
    unit = USD
    documentation = "Value of the non-refundable Lifetime Learning Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#c"

    def formula(tax_unit, period, parameters):
        education = parameters(period).gov.irs.credits.education
        llc = education.lifetime_learning_credit
        person = tax_unit.members
        is_aoc_eligible = person(
            "is_eligible_for_american_opportunity_credit", period
        )
        eligible_expenses = tax_unit.sum(
            person("qualified_tuition_expenses", period) * ~is_aoc_eligible
        )
        capped_expenses = min_(llc.expense_limit, eligible_expenses)
        maximum_amount = llc.rate * capped_expenses
        phase_out = tax_unit("education_credit_phase_out", period)
        if llc.abolition:
            return 0
        return max_(0, maximum_amount * (1 - phase_out))
