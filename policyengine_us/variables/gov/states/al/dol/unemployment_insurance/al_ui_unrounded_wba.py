from policyengine_us.model_api import *


class al_ui_unrounded_wba(Variable):
    value_type = float
    entity = Person
    label = "Alabama UI unrounded weekly benefit amount"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-72/"
    defined_for = StateCode.AL

    def formula(person, period, parameters):
        high_quarter_wages = person("al_ui_high_quarter_wages", period)
        second_high_quarter_wages = person("al_ui_second_high_quarter_wages", period)
        # Statutory formula per Code of Ala. § 25-4-72(b): 1/52 of the sum of
        # the two highest base-period quarters (confirmed by USDOL Comparison
        # of State UI Laws). This is authoritative over the BRR handbook's
        # simplified gloss and should not be "corrected" to match it.
        return (high_quarter_wages + second_high_quarter_wages) / WEEKS_IN_YEAR
