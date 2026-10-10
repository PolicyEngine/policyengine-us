from policyengine_us.model_api import *


class nm_2021_income_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico 2021 income tax rebate"
    definition_period = YEAR
    reference = (
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503708/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsPABwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA",
        # PDF pages 2-3
        "https://realfile.tax.newmexico.gov/2021pit-rc-ins.pdf#page=2",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        # The rebate goes to "a resident ... who is not a dependent of another
        # individual", and the law does not settle a joint return where only
        # one spouse is. For the same phrase on its rebate and credit schedule,
        # TRD says "If you are a dependent with a spouse who was not a
        # dependent of another taxpayer, your spouse may still qualify to
        # claim rebates or credits" (PIT-RC instructions); we apply that
        # reading, so only a return on which every filer is a dependent
        # elsewhere is barred.
        every_filer_dependent = tax_unit("every_filer_is_dependent_elsewhere", period)
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.nm.tax.income.rebates["2021_income"]
        income_eligible = agi < p.main.income_limit[filing_status]
        eligible = income_eligible & ~every_filer_dependent
        amount_if_eligible = p.main.amount[filing_status]
        return eligible * amount_if_eligible
