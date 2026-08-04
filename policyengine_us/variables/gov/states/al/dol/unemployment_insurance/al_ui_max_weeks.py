from policyengine_us.model_api import *


class al_ui_max_weeks(Variable):
    value_type = int
    entity = Person
    label = "Alabama UI maximum number of weeks of regular benefits"
    unit = "week"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/alabama/title-25/chapter-4/article-4/section-25-4-74/",
        "https://alabamaretail.org/news/unemployment-comp-weeks-weekly-benefits/",
    )
    defined_for = StateCode.AL

    # Statute (Code of Ala. § 25-4-74(d)) sets the number of weeks off the
    # seasonally adjusted 3-month average statewide unemployment rate for the
    # calendar quarter ending immediately before the benefit year begins (the
    # prior third calendar quarter). The model approximates this with the
    # benefit year's January value of state_unemployment_rate, which is a
    # monthly series returned at its January reading under a YEAR period. The
    # two measures diverge materially only in the COVID window, when the rate
    # moved sharply within a quarter; in ordinary years the January reading and
    # the prior-quarter 3-month average land in the same duration bracket.

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dol.unemployment_insurance
        return p.mba.duration_weeks.calc(p.state_unemployment_rate)
