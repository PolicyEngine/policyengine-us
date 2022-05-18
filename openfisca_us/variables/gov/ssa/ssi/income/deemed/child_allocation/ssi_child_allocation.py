from openfisca_us.model_api import *


class ssi_child_allocation(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible child allocation"
    unit = USD
    documentation = "A deduction in respect of this person which is deducted from an ineligible spouse' income."
    definition_period = YEAR

    def formula(person, period, parameters):
        ineligible = ~person("is_ssi_aged_blind_disabled", period)
        child = person("is_child", period)
        income = add(
            person, period, ["ssi_earned_income", "ssi_unearned_income"]
        )
        ssi = parameters(period).ssa.ssi.amount
        allocation = ineligible * child * (ssi.couple - ssi.individual)
        return max_(0, allocation - income)
