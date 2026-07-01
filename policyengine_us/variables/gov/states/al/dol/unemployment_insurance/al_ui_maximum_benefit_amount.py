from policyengine_us.model_api import *


class al_ui_maximum_benefit_amount(Variable):
    value_type = float
    entity = Person
    label = "Alabama UI maximum benefit amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-74/",
        "https://oui.doleta.gov/unemploy/pdf/uilawcompar/2023/monetary.pdf#page=26",
    )
    defined_for = StateCode.AL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dol.unemployment_insurance
        wba = person("al_ui_weekly_benefit_amount", period)
        max_weeks = person("al_ui_max_weeks", period)
        base_period_wages = person("al_ui_base_period_wages", period)
        weeks_cap = max_weeks * wba
        bpw_cap = p.mba.bpw_fraction * base_period_wages
        return np.round(min_(weeks_cap, bpw_cap))
