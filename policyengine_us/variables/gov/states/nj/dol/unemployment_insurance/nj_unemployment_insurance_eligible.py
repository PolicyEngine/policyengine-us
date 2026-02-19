from policyengine_us.model_api import *


class nj_unemployment_insurance_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for New Jersey unemployment insurance"
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/who/",
        "https://www.nj.gov/labor/lwdhome/press/2025/20251229_newbenefitrates2026.shtml",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        base_weeks = person(
            "nj_unemployment_insurance_base_period_weeks", period
        )
        base_wages = person(
            "nj_unemployment_insurance_base_period_wages", period
        )
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        meets_weeks_test = base_weeks >= p.min_base_weeks
        meets_earnings_test = base_wages >= p.min_total_base_earnings
        return meets_weeks_test | meets_earnings_test
