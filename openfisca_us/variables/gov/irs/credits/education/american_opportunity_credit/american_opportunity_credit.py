from openfisca_us.model_api import *


class american_opportunity_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "American Opportunity Credit"
    unit = USD
    documentation = "Total value of the American Opportunity Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#b"

    def formula(tax_unit, period, parameters):
        education = parameters(period).irs.credits.education
        aoc = education.american_opportunity_credit
        person = tax_unit.members
        is_eligible = person(
            "is_eligible_for_american_opportunity_credit", period
        )
        tuition_expenses = (
            person("qualified_tuition_expenses", period) * is_eligible
        )
        maximum_amount_per_student = aoc.amount.calc(tuition_expenses)
        maximum_amount = tax_unit.sum(maximum_amount_per_student)
        phaseout = tax_unit("education_credit_phaseout", period)
        if aoc.abolition:
            return 0
        return max_(0, maximum_amount * (1 - phaseout))
