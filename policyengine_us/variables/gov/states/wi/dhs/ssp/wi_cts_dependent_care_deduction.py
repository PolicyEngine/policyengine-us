from policyengine_us.model_api import *


class wi_cts_dependent_care_deduction(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin CTS allowed dependent care deduction"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=31",
        "https://www.govinfo.gov/content/pkg/CFR-1997-title45-vol2/pdf/CFR-1997-title45-vol2-sec233-20.pdf#page=14",
        "https://www.govinfo.gov/content/pkg/STATUTE-102/pdf/STATUTE-102-Pg2343.pdf#page=55",
    )
    documentation = "Childcare cost per care recipient, subject to the Handbook 3.2.1.2.3 limits. Incapacitated-adult care and the work-related condition are not modeled. The net income test deducts the group's total only from its earned income left after the $90, $30 and one-third disregards. AFDC took the care disregard from each earner's own earned income; the model pools the group's remaining earnings because it does not know who pays for care."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp.cts
        limit = where(
            person("age", period.this_year) < p.care_young_age,
            p.care_young_limit,
            p.care_other_limit,
        )
        return min_(max_(person("pre_subsidy_childcare_expenses", period), 0), limit)
