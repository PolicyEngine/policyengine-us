from policyengine_us.model_api import *


class pa_ccw_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Pennsylvania CCW"
    # YEAR: PA evaluates child eligibility at annual redetermination.
    # A child who turns 13 mid-period stays eligible until the next
    # redetermination (55 Pa. Code 3042.11(d)).
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = (
        "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=9",
        "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=16",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.ccw.eligibility.age_threshold
        age = person("age", period)
        is_disabled = person("is_disabled", period)
        age_eligible = where(is_disabled, age < p.disabled_child, age < p.child)
        is_dependent = person("is_tax_unit_dependent", period)
        immigration_eligible = person("is_ccdf_immigration_eligible_child", period)
        standard_eligible = age_eligible & is_dependent & immigration_eligible
        # Foster and protective services children are eligible regardless
        # of dependency or immigration (55 Pa. Code 3042.3).
        foster = person("is_in_foster_care", period)
        protective = person("receives_or_needs_protective_services", period)
        categorical_eligible = age_eligible & (foster | protective)
        return standard_eligible | categorical_eligible
