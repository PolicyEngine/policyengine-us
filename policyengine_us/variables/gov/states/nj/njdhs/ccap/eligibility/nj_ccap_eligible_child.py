from policyengine_us.model_api import *


class nj_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for New Jersey CCAP"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-15-5-2",
        "https://www.childcarenj.gov/ChildCareNJ/media/media_library/CCDF_State_Plan_for_New_Jersey_FFY25-27.pdf#page=14",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.njdhs.ccap.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_eligible = where(is_disabled, age < p.special_needs, age < p.child)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        standard_eligible = age_eligible & is_dependent & immigration_eligible
        # CP&P (Child Protective & Permanency) children are eligible
        # regardless of dependency or immigration status.
        protective = person("receives_or_needs_protective_services", period)
        foster = person("is_in_foster_care", period)
        categorical_eligible = age_eligible & (protective | foster)
        return standard_eligible | categorical_eligible
