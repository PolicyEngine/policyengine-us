from openfisca_us.model_api import *


class ssi_ineligible_spouse_child_allocation_deduction_earned(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible spouse child deduction (earned income)"
    unit = USD
    documentation = "Deduction from earned income if this is an eligible spouse, in respect of any ineligible children."
    definition_period = YEAR

    def formula(person, period, parameters):
        child_allocation = person.tax_unit.sum(
            person("ssi_child_allocation", period)
        )
        unearned_deduction = person(
            "ssi_ineligible_spouse_child_allocation_deduction_unearned", period
        )
        sources = parameters(period).ssa.ssi.income.sources.earned
        earned_income = add(person, period, sources)
        return max_(0, child_allocation - earned_income - unearned_deduction)
