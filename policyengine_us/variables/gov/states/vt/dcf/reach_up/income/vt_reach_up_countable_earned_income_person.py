from policyengine_us.model_api import *


class vt_reach_up_countable_earned_income_person(Variable):
    value_type = float
    entity = Person
    label = "Vermont Reach Up countable earned income for each person"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://law.justia.com/codes/vermont/title-33/chapter-11/section-1103/",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = StateCode.VT

    def formula(person, period, parameters):
        # Per Section 2252.3: Disregard applied to each eligible household member
        p = parameters(
            period
        ).gov.states.vt.dcf.reach_up.income.earned_disregard
        gross_earned = person("tanf_gross_earned_income", period)
        after_flat = max_(gross_earned - p.flat, 0)
        return after_flat * (1 - p.rate)
