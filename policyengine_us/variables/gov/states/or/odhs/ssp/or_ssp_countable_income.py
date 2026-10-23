from policyengine_us.model_api import *


class or_ssp_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Oregon SSP countable income before deductions"
    definition_period = MONTH
    unit = USD
    reference = (
        # PDF pages 1-2, 5
        "https://ch461rules.odhs.oregon.gov/rules/461-001-0000.pdf#page=1",
        "https://ch461rules.odhs.oregon.gov/rules/461-145-0030.pdf#page=2",
        "https://ch461rules.odhs.oregon.gov/rules/461-145-0108.pdf#page=1",
        # PDF pages 2, 4
        "https://ch461rules.odhs.oregon.gov/rules/461-140-0040.pdf#page=2",
        # Effective 10-01-26; the 7-01-18 version in the history applies before.
        "https://ch461rules.odhs.oregon.gov/rules/461-145-0120.pdf#page=1",
        "https://ch461rules.odhs.oregon.gov/historical/461-145-0120_history.pdf#page=1",
        "https://ch461rules.odhs.oregon.gov/rules/461-145-0130.pdf#page=2",
        "https://ch461rules.odhs.oregon.gov/rules/461-150-0095.pdf#page=1",
    )
    documentation = "Includes SSI, earned income as SSI counts it and countable unearned cash income, before the general or earnings deductions. Earned income excludes salary-reduction health premiums, and a reported self-employment loss offsets only the person's other earned income. Investment interest and dividends and income inaccessible due to incapacity are excluded. Other state exclusions and countable loan interest are not modeled."

    def formula(person, period, parameters):
        p = parameters(period).gov
        excluded = p.states["or"].odhs.ssp.excluded_income_sources
        # OAR 461-145-0120(5)(b) counts cafeteria plan benefits only when taken
        # as cash, and 461-150-0095(2) excludes a documented self-employment
        # loss "only from other earned income". ssi_earned_income applies both,
        # as SSI does, and the floor keeps a loss off unearned income.
        # NOTE: 461-140-0040(4) counts income "before deductions, such as
        # garnishments, taxes, or other payroll deductions", but only "Unless
        # exclusions under another rule in chapter 461 apply"; salary-reduction
        # health premiums follow 0120(5)(b).
        # NOTE: A loss offsets only the person's own earned income, while
        # 0095(2) also applies it to other earned income of the financial
        # group, such as a spouse's wages.
        earned = max_(person("ssi_earned_income", period), 0)
        income = person("ssi", period) + earned
        for name in p.ssa.ssi.income.sources.unearned:
            if name not in excluded:
                income = income + max_(person(name, period), 0)
        # OAR 461-140-0040(5)(e)(D): income inaccessible due to incapacity is
        # unavailable, so it is not countable.
        inaccessible = max_(person("or_ssp_inaccessible_income", period), 0)
        return max_(income - inaccessible, 0)
