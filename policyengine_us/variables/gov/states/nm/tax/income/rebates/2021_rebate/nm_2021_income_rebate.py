from policyengine_us.model_api import *


class nm_2021_income_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico 2021 income tax rebate"
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503708/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsPABwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        dependent_on_another_return = tax_unit("dsi", period)
        income = tax_unit("adjusted_gross_income", period)
        p = (
            parameters(period)
            .gov.states.nm.tax.income.rebates["2021_income"]
            .main
        )
        filing_status = tax_unit("filing_status", period)
        income_eligible = income < p.income_limit[filing_status]
        eligible = income_eligible & ~dependent_on_another_return
        amount_if_eligible = p.amount[filing_status]
        return eligible * amount_if_eligible
