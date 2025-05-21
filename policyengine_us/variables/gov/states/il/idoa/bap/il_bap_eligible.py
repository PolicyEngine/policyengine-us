from policyengine_us.model_api import *


class il_bap_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Illinois Chicago Department of Aging Benefit Access Program (BAP)"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://ilaging.illinois.gov/benefitsaccess.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.idoa.bap
        age = person("age", period)

        senior = age >= p.senior_age_threshold
        income = person("adjusted_gross_income_person", period)
        household_income = person.spm_unit.sum(income)
        size = person.spm_unit("spm_unit_size", period)
        capped_size = min_(size, 3)
        income_limit = p.income_limit[capped_size]
        income_eligible = household_income <= income_limit
        eligible_senior = senior & income_eligible

        disabled = person("is_permanently_and_totally_disabled", period)
        disabled_age = age >= p.disabled
        eligible_disabled = disabled & disabled_age & income_eligible

        return eligible_senior | eligible_disabled
