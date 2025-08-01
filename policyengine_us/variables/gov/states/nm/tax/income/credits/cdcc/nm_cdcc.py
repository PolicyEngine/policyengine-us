from policyengine_us.model_api import *


class nm_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico dependent child day care credit"
    unit = USD
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503752/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsfAEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = "nm_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        nm_cdcc_max = tax_unit("nm_cdcc_max_amount", period)
        us_cdcc = tax_unit("cdcc_potential", period)
        # New Mexico matches the potential federal credit
        if "cdcc" in parameters(period).gov.irs.credits.non_refundable:
            us_taxbc = tax_unit("income_tax_before_credits", period)
            used_us_cdcc = min_(us_cdcc, us_taxbc)
        else:
            used_us_cdcc = us_cdcc
        nm_cdcc = max_(0, nm_cdcc_max - used_us_cdcc)
        # separate filers can claim only part of nm_cdcc
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        p = parameters(period).gov.states.nm.tax.income.credits.cdcc
        return where(separate, nm_cdcc / p.divisor, nm_cdcc)
