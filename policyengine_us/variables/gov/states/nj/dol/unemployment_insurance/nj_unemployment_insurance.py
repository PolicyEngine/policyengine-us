from policyengine_us.model_api import *


class nj_unemployment_insurance(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance"
    unit = USD
    documentation = "Annual unemployment insurance benefit for New Jersey. Calculated as the weekly benefit multiplied by the number of weeks claimed, capped at 26 weeks or the number of base period weeks worked."
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/calculator/",
    )
    defined_for = "nj_unemployment_insurance_eligible"

    def formula(person, period, parameters):
        weekly_benefit = person(
            "nj_unemployment_insurance_weekly_benefit", period
        )
        weeks_claimed = person(
            "nj_unemployment_insurance_weeks_claimed", period
        )
        base_weeks = person(
            "nj_unemployment_insurance_base_period_weeks", period
        )

        # Get parameters
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        max_weeks = p.max_benefit_weeks

        # Maximum weeks is the lesser of: max benefit weeks (26),
        # base period weeks, or weeks actually claimed
        available_weeks = min_(base_weeks, max_weeks)
        actual_weeks = min_(weeks_claimed, available_weeks)

        return weekly_benefit * actual_weeks
