from policyengine_us.model_api import *


class pr_american_opportunity_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico American Opportunity Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=13"
    defined_for = "pr_american_opportunity_credit_eligibility"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.american_opportunity_credit
        aoc = parameters(
            period
        ).gov.irs.credits.education.american_opportunity_credit
        person = tax_unit.members
        is_eligible = person(
            "is_eligible_for_american_opportunity_credit", period
        )
        tuition_expenses = (
            person("qualified_tuition_expenses", period) * is_eligible
        )
        capped_tuition = min_(
            tuition_expenses, p.tuition_cap
        )  # p.tuition_cap: 4000. column C
        maximum_amount_per_student = aoc.amount.calc(capped_tuition)
        maximum_amount = tax_unit.sum(maximum_amount_per_student)
        phase_out = tax_unit("education_credit_phase_out", period)
        return max_(0, maximum_amount * (1 - phase_out))