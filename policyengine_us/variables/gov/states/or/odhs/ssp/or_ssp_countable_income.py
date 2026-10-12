from policyengine_us.model_api import *


class or_ssp_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Oregon SSP countable income before deductions"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-001-0000.pdf",
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-145-0030.pdf",
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-145-0108.pdf",
    )
    documentation = "Includes SSI and countable cash income before the general or earnings deductions. Investment interest and dividends are excluded. Override for other state exclusions, inaccessible income, countable loan interest or sources absent from federal SSI inputs."

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi.income.sources
        sources = list(p.earned) + list(p.unearned)
        income = sum(
            max_(person(name, period), 0)
            for name in sources
            if name not in ("interest_income", "dividend_income")
        )
        return income + person("ssi", period)
