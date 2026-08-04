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

    # Not modeled: the 5 additional weeks of benefits available during approved
    # training (Code of Ala. § 25-4-74(f)); non-monetary eligibility conditions
    # (able and available for work, active work search, and separation
    # qualification); employer experience rating; and combined-wage claims
    # (wages earned in other states). Only monetary eligibility and the regular
    # benefit amount are captured here.
    #
    # Microsim limitation: the five wage/quarter inputs feeding this program
    # (base-period and quarterly wages, weekly earnings, and weeks unemployed)
    # default to 0 and are not imputed in the national dataset, so the program
    # is inert in dataset runs and produces nonzero benefits only when those
    # inputs are supplied through the household calculator.

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dol.unemployment_insurance
        partial_weekly_benefit = person("al_ui_partial_weekly_benefit", period)
        max_weeks = person("al_ui_max_weeks", period)
        mba = person("al_ui_maximum_benefit_amount", period)
        weeks_unemployed = person("weeks_unemployed", period)
        weeks_paid = clip(weeks_unemployed - p.waiting_weeks, 0, max_weeks)
        # Intentional: the partial weekly benefit is applied to every payable
        # week, assuming the same weekly earnings across the whole spell
        # (equivalent to the full WBA whenever weekly earnings are zero).
        return min_(weeks_paid * partial_weekly_benefit, mba)
