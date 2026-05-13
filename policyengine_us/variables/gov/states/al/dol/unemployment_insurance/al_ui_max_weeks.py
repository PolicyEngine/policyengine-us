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

    def formula(person, period, parameters):
        # NOTE: state_unemployment_rate is monthly; at YEAR period the
        # framework returns the January value of the benefit year.
        p = parameters(period).gov.states.al.dol.unemployment_insurance
        return p.mba.duration_weeks.calc(p.state_unemployment_rate)
