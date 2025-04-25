from policyengine_us.model_api import *


class il_cta_free_ride_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Eligible for the Illinois Chicago Transit Authority free ride program"
    )
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://www.transitchicago.com/reduced-fare-programs/#free"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.rta
        age = person("age", period)
        young_child = age <= p.age_threshold.young_child

        senior = age >= p.age_threshold.senior
        income = person("irs_gross_income", period)
        household_income = person.spm_unit.sum(income)
        size = person.spm_unit("spm_unit_size", period)
        capped_size = min_(size, 3)
        income_eligible = household_income <= p.income_limit[capped_size]
        eligible_senior = senior & income_eligible

        disabled = person("is_permanently_and_totally_disabled", period)
        disabled_age = age >= p.age_threshold.disabled
        eligible_disabled = disabled & disabled_age & income_eligible

        eligible_military_status = person(
            "il_cta_military_service_pass_eligible", period
        )
        return (
            young_child
            | eligible_senior
            | eligible_disabled
            | eligible_military_status
        )
