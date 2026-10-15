from policyengine_us.model_api import *


class or_ssp_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Oregon SSP countable income before deductions"
    definition_period = MONTH
    unit = USD
    reference = (
        # PDF pages 1, 5
        "https://ch461rules.odhs.oregon.gov/rules/461-001-0000.pdf#page=1",
        "https://ch461rules.odhs.oregon.gov/rules/461-145-0030.pdf#page=2",
        "https://ch461rules.odhs.oregon.gov/rules/461-145-0108.pdf#page=1",
        "https://ch461rules.odhs.oregon.gov/rules/461-140-0040.pdf#page=4",
    )
    documentation = "Includes SSI and countable cash income before the general or earnings deductions. Investment interest and dividends and income inaccessible due to incapacity are excluded. Other state exclusions and countable loan interest are not modeled."

    def formula(person, period, parameters):
        p = parameters(period).gov
        sources = p.ssa.ssi.income.sources
        excluded = p.states["or"].odhs.ssp.excluded_income_sources
        income = person("ssi", period)
        for name in list(sources.earned) + list(sources.unearned):
            if name not in excluded:
                income = income + max_(person(name, period), 0)
        # OAR 461-140-0040(5)(e)(D): income inaccessible due to incapacity is
        # unavailable, so it is not countable.
        inaccessible = max_(person("or_ssp_inaccessible_income", period), 0)
        return max_(income - inaccessible, 0)
