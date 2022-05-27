from openfisca_us.model_api import *


class ssi_ineligible_spouse_child_allocation_deduction_unearned(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible spouse child deduction (unearned income)"
    unit = USD
    documentation = "Deduction from unearned income if this is an eligible spouse, in respect of any ineligible children."
    definition_period = YEAR

    def formula(person, period, parameters):
        child_allocation = person.tax_unit.sum(
            person("ssi_child_allocation", period)
        )
        sources = parameters(period).ssa.ssi.income.sources.unearned
        unearned_income = add(person, period, sources)
        return max_(0, child_allocation - unearned_income)
