from policyengine_us.model_api import *


class al_ui_weekly_benefit_amount(Variable):
    value_type = float
    entity = Person
    label = "Alabama UI weekly benefit amount"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-72/"
    defined_for = StateCode.AL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dol.unemployment_insurance.wba
        unrounded_wba = person("al_ui_unrounded_wba", period)
        monetarily_eligible = person("al_ui_monetarily_eligible", period)
        # NOTE: § 25-4-72(b)(1) half-down rounding: ties at $0.50 round DOWN.
        # np.ceil(x - 0.5): 100.50 -> 100, 100.51 -> 101.
        rounded_wba = np.ceil(unrounded_wba - 0.5)
        return min_(rounded_wba, p.max) * monetarily_eligible
