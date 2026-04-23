from policyengine_us.model_api import *


class nj_unemployment_insurance(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance"
    unit = USD
    documentation = (
        "Annualized New Jersey unemployment insurance benefit amount. "
        "Within-year dynamics are approximated through weeks_claimed and "
        "weekly claiming inputs rather than modeled week by week."
    )
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/calculator/",
        "https://www.nj.gov/labor/myunemployment/help/faqs/reducebenefits.shtml",
    )
    defined_for = "nj_unemployment_insurance_eligible"

    def formula(person, period, parameters):
        weekly_benefit = person("nj_unemployment_insurance_weekly_benefit", period)
        weekly_gross_wages = person(
            "nj_unemployment_insurance_weekly_gross_wages", period
        )
        weeks_claimed = person("nj_unemployment_insurance_weeks_claimed", period)
        qualifying_base_weeks = person(
            "nj_unemployment_insurance_base_period_weeks", period
        )
        working_less_than_full_time = person(
            "nj_unemployment_insurance_working_less_than_full_time", period
        )
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        available_weeks = min_(qualifying_base_weeks, p.max_benefit_weeks)
        actual_weeks = min_(weeks_claimed, available_weeks)
        reduced_weekly_benefit = min_(
            weekly_benefit,
            np.floor(
                max_(
                    0,
                    weekly_benefit * p.partial_benefit_rate_multiplier
                    - np.floor(weekly_gross_wages),
                )
            ),
        )
        payable_weekly_benefit = where(
            weekly_gross_wages > 0,
            where(working_less_than_full_time, reduced_weekly_benefit, 0),
            weekly_benefit,
        )
        return payable_weekly_benefit * actual_weeks
