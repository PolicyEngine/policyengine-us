from policyengine_us.model_api import *


class al_ui_monetarily_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Monetarily eligible for Alabama Unemployment Insurance"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-77/",
        "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-72/",
    )
    defined_for = StateCode.AL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dol.unemployment_insurance
        high_quarter_wages = person("al_ui_high_quarter_wages", period)
        base_period_wages = person("al_ui_base_period_wages", period)
        quarters_with_wages = person("al_ui_quarters_with_wages", period)
        unrounded_wba = person("al_ui_unrounded_wba", period)

        meets_quarters_test = quarters_with_wages >= p.eligibility.quarters_with_wages
        meets_wages_test = (
            base_period_wages
            >= p.eligibility.bpw_to_hqw_multiplier * high_quarter_wages
        )
        meets_unrounded_wba_floor = unrounded_wba > p.wba.min_threshold
        return meets_quarters_test & meets_wages_test & meets_unrounded_wba_floor
