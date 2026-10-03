from policyengine_us.model_api import *


class al_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alabama LIHEAP annual countable household income"
    defined_for = StateCode.AL
    # Pages 17-19 define income; page 22 retains nonqualified members' income.
    reference = "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-Manual-1.pdf#page=17"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.adeca.liheap.income
        person = spm_unit.members
        adult = person("age", period) >= p.earned_income_min_age
        # Annual income approximates the preceding calendar month's income.
        # Existing signed net business inputs need no further expense deduction.
        # The manual does not expressly settle whether losses offset other income;
        # preserve the signed inputs and floor the combined household total.
        earned = add(person, period, p.sources.earned)
        unearned = add(spm_unit, period, p.sources.unearned, options=[ADD])
        net_gambling = max_(
            person("gambling_winnings", period) - person("gambling_losses", period),
            0,
        )
        # Earned income under age 18 is excluded; unearned income is included
        # at every age. Immigration status does not remove anyone's income.
        # Estate income captures existing net estate/trust income separately
        # from interest and dividends; it cannot classify distributions of
        # principal or nonperiodic receipts. Financial assistance covers cash
        # support from family or friends; royalties, stipends, and some
        # severance payments remain unavailable as distinct inputs.
        return max_(
            spm_unit.sum(earned * adult + net_gambling) + unearned,
            0,
        )
