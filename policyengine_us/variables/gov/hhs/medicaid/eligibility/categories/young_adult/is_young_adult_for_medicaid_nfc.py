from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
)


class is_young_adult_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid young adult non-financial criteria"
    definition_period = YEAR
    reference = "https://healthweb-back.health.ny.gov/health_care/medicaid/publications/adm/13adm3.htm"
    documentation = (
        "New York's MAGI pathway for 19- and 20-year-olds requires living "
        "with a parent. Parent identifiers establish that relationship and "
        "must resolve within the person's household; tax dependency alone "
        "does not establish co-residence."
    )

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.young_adult
        age = person("age", period)
        return ma.age_range.calc(age)

    def formula_2014(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.young_adult
        age_eligible = ma.age_range.calc(person("age", period))
        first, second = co_resident_parent_indices(person, period)
        lives_with_parent = (first >= 0) | (second >= 0)
        state = person.household("state_code", period)
        return age_eligible & ((state != StateCode.NY) | lives_with_parent)
