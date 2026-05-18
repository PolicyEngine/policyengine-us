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
        net_capital_gains = max_(0, add(tax_unit, period, ["capital_gains"]))
        # HB0037 (2024) caps the 40% element at $1,000,000 of qualifying gain
        # starting 2025 (per NMSA 7-2-34(A)(2)). Pre-2025 the cap parameter is
        # infinite so the formula behavior is unchanged. The statute also
        # restricts the 40% element to "sale of a business" gains; that
        # business-sale flag is not yet modeled, so the cap is applied to all
        # capital gains as an upper bound on the deduction.
        gain_for_uncapped_element = min_(net_capital_gains, p.uncapped_element_max_gain)
        uncapped_element = p.uncapped_element_percent * gain_for_uncapped_element
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # Halve the deduction if filing separately.
        denominator = where(separate, 2, 1)
        capped_element = p.capped_element.calc(net_capital_gains)
        numerator = max_(uncapped_element, capped_element)
        return numerator / denominator
