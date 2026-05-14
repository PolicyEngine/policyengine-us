from policyengine_us.model_api import *


class al_ui_partial_weekly_benefit(Variable):
    value_type = float
    entity = Person
    label = "Alabama UI partial weekly benefit amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-73/",
        "https://oui.doleta.gov/unemploy/pdf/uilawcompar/2023/monetary.pdf#page=20",
        "https://www.nelp.org/new-alabama-unemployment-insurance-law-makes-work-pay/",
    )
    defined_for = StateCode.AL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dol.unemployment_insurance.partial
        wba = person("al_ui_weekly_benefit_amount", period)
        weekly_earnings = person("al_ui_weekly_earnings", period)
        disregard = wba * p.disregard_rate
        countable_earnings = max_(weekly_earnings - disregard, 0)
        partial_amount = max_(wba - countable_earnings, 0)
        return where(weekly_earnings < wba, partial_amount, 0)
