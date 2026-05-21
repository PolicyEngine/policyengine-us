from policyengine_us.model_api import *


class has_medicaid_work_requirement_exemption(Variable):
    value_type = bool
    entity = Person
    label = "Has an exemption for Medicaid work requirements"
    definition_period = MONTH
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters):
        has_age_exemption = person("has_age_exemption", period)
        is_totally_disabled_veteran = person("is_totally_disabled_veteran", period)
        is_medically_frail = person("is_medically_frail", period)
        is_pregnant = person("is_pregnant", period)
        has_young_dependent = person("has_young_dependent", period)
        is_disabled = person("is_disabled", period)
        has_disabled_dependent = person("has_disabled_dependent", period)

        
        return (
            has_age_exemption or
            is_pregnant or
            is_totally_disabled_veteran or
            is_medically_frail or
            is_disabled or
            has_disabled_dependent or
            has_young_dependent
        )
