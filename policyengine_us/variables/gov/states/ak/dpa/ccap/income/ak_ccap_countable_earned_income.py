from policyengine_us.model_api import *


class ak_ccap_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska CCAP countable earned income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.AK
    reference = (
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=203",
        "https://www.akleg.gov/basis/aac.asp#7.41.335",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.ccap.income.countable_income
        person = spm_unit.members
        is_adult = person("age", period.this_year) >= 18
        # YEAR-defined earned-income variables are auto-divided to monthly
        # values when read with a MONTH period.
        earned_per_person = sum(person(source, period) for source in p.earned_sources)
        return spm_unit.sum(earned_per_person * is_adult)
