from policyengine_us.model_api import *


class al_ui(Variable):
    value_type = float
    entity = Person
    label = "Alabama Unemployment Insurance"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-72/",
        "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-74/",
        "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-77/",
    )
    defined_for = "al_ui_monetarily_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dol.unemployment_insurance
        wba = person("al_ui_weekly_benefit_amount", period)
        partial_weekly_benefit = person("al_ui_partial_weekly_benefit", period)
        weekly_earnings = person("al_ui_weekly_earnings", period)
        max_weeks = person("al_ui_max_weeks", period)
        mba = person("al_ui_maximum_benefit_amount", period)
        weeks_unemployed = person("weeks_unemployed", period)
        weeks_paid = clip(weeks_unemployed - p.waiting_weeks, 0, max_weeks)
        weekly_amount = where(weekly_earnings < wba, partial_weekly_benefit, wba)
        return min_(weeks_paid * weekly_amount, mba)
