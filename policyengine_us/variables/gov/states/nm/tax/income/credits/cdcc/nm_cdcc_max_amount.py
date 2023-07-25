from policyengine_us.model_api import *


class nm_cdcc_max_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico maximum credit for child and dependent day care credit"
    unit = USD
    definition_period = YEAR
    defined_for = "nm_cdcc_eligible"
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503752/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsfAEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.credits.cdcc
        person = tax_unit.members
        eligible_dependent = person("nm_cdcc_eligible_child", period)
        # For each dependent we calculate the number of days in daycare
        # the daily amount can not exceed $8
        daily_expenses = min_(
            person("daily_childcare_expenses", period),
            p.max_amount.per_day,
        )
        childcare_days = person("childcare_days_per_year", period)
        total_expenses = eligible_dependent * (childcare_days * daily_expenses)
        # These costs are multiplied by 0.4 and capped at $480 per child
        reimbursed_costs = min_(
            total_expenses * p.rate, p.max_amount.per_child
        )
        # Total cap is $1,200
        total_costs = tax_unit.sum(reimbursed_costs)
        return min_(total_costs, p.max_amount.total)
