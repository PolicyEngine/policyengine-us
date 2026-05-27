from policyengine_us.model_api import *


class wv_ccap_daily_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "West Virginia CCAP daily benefit per child"
    definition_period = MONTH
    defined_for = "wv_ccap_eligible_child"
    reference = "https://bfa.wv.gov/media/6766/download?inline#page=80"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.ccap
        daily_rate = person("wv_ccap_daily_rate", period)
        has_developmental_delay = person("has_developmental_delay", period.this_year)
        special_needs_supplement = where(
            has_developmental_delay, p.supplements.special_needs, 0
        )
        non_trad = person("wv_ccap_non_traditional_hours", period)
        non_trad_supplement = where(non_trad, p.supplements.non_traditional_hours, 0)
        total_rate = daily_rate + special_needs_supplement + non_trad_supplement
        pre_subsidy = person("pre_subsidy_childcare_expenses", period)
        monthly_care_days = person(
            "childcare_attending_days_per_month", period.this_year
        )
        mask = monthly_care_days > 0
        daily_charge = np.divide(
            pre_subsidy,
            monthly_care_days,
            out=np.zeros_like(pre_subsidy, dtype=float),
            where=mask,
        )
        return max_(min_(total_rate, daily_charge), 0)
