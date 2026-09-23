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
        p = parameters(period).gov.states.nm.tax.income.deductions.net_capital_gains
        long_term_gain = add(tax_unit, period, ["long_term_capital_gains"])
        short_term_gain = add(tax_unit, period, ["short_term_capital_gains"])
        # From 2023 the instructions define "net capital gains" by IRC Section
        # 1222(11): net long-term capital gain less any net short-term capital
        # loss, so short-term gains are excluded. Earlier years use the net
        # capital gains reported on the federal return.
        net_capital_gains = where(
            p.excludes_short_term_gains,
            max_(0, long_term_gain - max_(0, -short_term_gain)),
            max_(0, long_term_gain + short_term_gain),
        )
        uncapped_element = p.uncapped_element_percent * net_capital_gains
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # Halve the deduction if filing separately.
        denominator = where(separate, 2, 1)
        capped_element = p.capped_element.calc(net_capital_gains)
        numerator = max_(uncapped_element, capped_element)
        return numerator / denominator
