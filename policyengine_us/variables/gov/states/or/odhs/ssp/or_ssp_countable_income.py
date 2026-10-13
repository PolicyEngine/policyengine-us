from policyengine_us.model_api import *


class or_ssp_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Oregon SSP countable income before deductions"
    definition_period = MONTH
    unit = USD
    reference = (
        # PDF pages 1, 5
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-001-0000.pdf#page=1",
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-145-0030.pdf#page=2",
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-145-0108.pdf#page=1",
    )
    documentation = "Includes SSI and countable cash income before the general or earnings deductions. Investment interest and dividends are excluded. Override for other state exclusions, inaccessible income, countable loan interest or sources absent from federal SSI inputs."

    def formula(person, period, parameters):
        p = parameters(period).gov
        sources = p.ssa.ssi.income.sources
        excluded = p.states["or"].odhs.ssp.excluded_income_sources
        income = person("ssi", period)
        for name in list(sources.earned) + list(sources.unearned):
            if name not in excluded:
                income = income + max_(person(name, period), 0)
        return income
