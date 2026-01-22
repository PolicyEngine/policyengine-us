from policyengine_us.model_api import *


class sd_tanf_countable_earned_income_person(Variable):
    value_type = float
    entity = Person
    label = "South Dakota TANF countable earned income for person"
    unit = USD
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:10:03:05"
    defined_for = StateCode.SD

    def formula(person, period, parameters):
        gross_earned = person("tanf_gross_earned_income", period)
        p = parameters(
            period
        ).gov.states.sd.dss.tanf.income.earned_income_disregard
        # Per ARSD 67:10:03:05: Each employed member receives
        # $90 flat deduction + 20% of remaining gross earned income
        after_flat = max_(gross_earned - p.flat_deduction, 0)
        return after_flat * (1 - p.percentage)
