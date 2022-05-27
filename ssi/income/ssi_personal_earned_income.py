from openfisca_us.model_api import *


class ssi_personal_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "SSI personal earned income"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/42/1382a#a_1"

    def formula(person, period, parameters):
        sources = parameters(period).ssa.ssi.income.sources.earned
        child_allocation_deduction = person(
            "ssi_ineligible_spouse_child_allocation_deduction_earned", period
        )
        return max_(
            0, add(person, period, sources) - child_allocation_deduction
        )
