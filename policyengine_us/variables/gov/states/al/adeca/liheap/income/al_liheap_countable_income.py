from policyengine_us.model_api import *


class al_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alabama LIHEAP annual countable household income"
    defined_for = StateCode.AL
    # PDF pages 17-19, 22
    reference = "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-Manual-1.pdf#page=17"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.adeca.liheap.income
        person = spm_unit.members
        adult = person("age", period) >= p.earned_income_min_age
        # Annual income approximates the preceding calendar month's income.
        # Existing net business inputs need no further expense deduction.
        # Manual 5.5.1 counts "total monthly cash receipts before taxes from
        # all sources", so each source is floored at zero and a loss in one
        # source cannot offset another.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period), 0)
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
        # The annual tanf aggregate includes al_tanf and applies take-up;
        # al_tanf alone is the entitlement and would count benefits a
        # nonrecipient could get.
        return spm_unit.sum(earned * adult + unearned + net_gambling) + spm_unit(
            "tanf", period
        )
