from policyengine_us.model_api import *


class ssi_ineligible_child_allocation(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible child allocation"
    unit = USD
    documentation = "The amount of income that SSI deems ought to be spent on this child, and therefore is not deemed to SSI claimants."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"

    def formula(person, period, parameters):
        income = add(
            person, period, ["ssi_earned_income", "ssi_unearned_income"]
        )
        ssi = parameters(period).gov.ssa.ssi.amount
        allocation = (
            person("is_ssi_ineligible_child", period)
            * (ssi.couple - ssi.individual)
            * MONTHS_IN_YEAR
        )
        return max_(0, allocation - income)
