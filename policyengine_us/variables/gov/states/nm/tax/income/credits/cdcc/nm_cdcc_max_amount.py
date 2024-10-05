from policyengine_us.model_api import *


class nm_cdcc_max_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico maximum credit for dependent child day care credit"
    unit = USD
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503752/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsfAEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = "nm_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        # allocate unit's childcare expenses across eligible children
        person = tax_unit.members
        expenses = person.tax_unit("tax_unit_childcare_expenses", period)
        eligible = person("nm_cdcc_eligible_child", period).astype(float)
        count_eligible = person.tax_unit.sum(eligible)
        expense = np.zeros_like(eligible)
        mask = count_eligible > 0
        expense[mask] = eligible[mask] * expenses[mask] / count_eligible[mask]
        # cap each eligible child's allowable expense
        p = parameters(period).gov.states.nm.tax.income.credits.cdcc
        child_expense = min_(p.max_amount.per_child, p.rate * expense)
        # cap unit's total allowable expense
        total_expense = tax_unit.sum(child_expense)
        return min_(p.max_amount.total, total_expense)
