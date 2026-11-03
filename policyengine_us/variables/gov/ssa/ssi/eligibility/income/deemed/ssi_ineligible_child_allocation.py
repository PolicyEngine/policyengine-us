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
        # 416.1111(b) permits net losses to offset only earned income;
        # 416.1163(b) reduces the allocation by the child's own income.
        income = max_(person("ssi_earned_income", period), 0) + person(
            "ssi_unearned_income", period
        )
        ssi = parameters(period).gov.ssa.ssi.amount
        allocation = (
            person("is_ssi_ineligible_child", period)
            * (ssi.couple - ssi.individual)
            * MONTHS_IN_YEAR
        )
        return max_(0, allocation - income)
