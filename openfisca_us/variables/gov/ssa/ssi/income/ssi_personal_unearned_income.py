from openfisca_us.model_api import *


class ssi_personal_unearned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "SSI personal unearned income"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/42/1382a#a_2"

    def formula(person, period, parameters):
        sources = parameters(period).ssa.ssi.income.sources.unearned
        child_allocation_deduction = person(
            "ssi_ineligible_spouse_child_allocation_deduction_unearned", period
        )
        return max_(
            0, add(person, period, sources) - child_allocation_deduction
        )
