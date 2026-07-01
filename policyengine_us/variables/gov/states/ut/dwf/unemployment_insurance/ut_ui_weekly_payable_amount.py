from policyengine_us.model_api import *


class ut_ui_weekly_payable_amount(Variable):
    value_type = float
    entity = Person
    label = "Utah UI weekly payable amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://le.utah.gov/xcode/Title35A/Chapter4/35A-4-S401.html",
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R994-401-301",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dwf.unemployment_insurance
        weekly_benefit_amount = person("ut_ui_weekly_benefit_amount", period)
        gross_weekly_earnings = person("ut_ui_gross_weekly_earnings", period)
        weekly_hours_worked = person("ut_ui_weekly_hours_worked", period)

        # § 35A-4-401(3)(a): the first 30% of WBA in weekly earnings is
        # disregarded; earnings above that reduce the WBA dollar-for-dollar.
        earnings_disregard = (
            p.benefit.partial.earnings_disregard_rate * weekly_benefit_amount
        )
        excess_earnings = max_(gross_weekly_earnings - earnings_disregard, 0)
        raw_payable = max_(np.floor(weekly_benefit_amount - excess_earnings), 0)

        # § 35A-4-401(3)(a): earnings at or above the WBA disqualify the
        # week. Claimant Guide page 11 (PDF file p. 13) / § 35A-4-207:
        # working at least the full-time hours threshold (40 hours) in a
        # week also disqualifies.
        disqualified = (gross_weekly_earnings >= weekly_benefit_amount) | (
            weekly_hours_worked >= p.benefit.partial.hours_threshold
        )
        return where(disqualified, 0, raw_payable)
