from policyengine_us.model_api import *


class nm_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico dependent child day care credit"
    defined_for = "nm_cdcc_eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503752/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsfAEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.credits.cdcc
        # Maximum New Mexico CDCC amount
        nm_cdcc_max = tax_unit("nm_cdcc_max_amount", period)
        # Federal child and dependent care credit
        fed_cdcc = tax_unit("cdcc", period)
        # The maximum nm amount is subtracted from the federal cdcc amount
        nm_cdcc = max_(fed_cdcc - nm_cdcc_max, 0)
        # Separate filers can claim one half of the credit
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return where(separate, nm_cdcc / p.divisor, nm_cdcc)
