from policyengine_us.model_api import *


class nm_net_capital_gains_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico net capital gain deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503882/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcwgEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nm.tax.income.deductions.net_capital_gains
        net_capital_gains = max_(0, add(tax_unit, period, ["capital_gains"]))
        # Filers can deduct 100% of CG up to a cap, or 40% uncapped, whichever is greater.
        uncapped_element = p.uncapped_element_percent * net_capital_gains
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # Halve the deduction if filing separately.
        denominator = where(separate, 2, 1)
        capped_element = p.capped_element.calc(net_capital_gains)
        numerator = max_(uncapped_element, capped_element)
        return numerator / denominator
