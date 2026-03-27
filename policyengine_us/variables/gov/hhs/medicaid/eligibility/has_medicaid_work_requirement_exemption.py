from policyengine_us.model_api import *


class has_medicaid_work_requirement_exemption(Variable):
    value_type = bool
    entity = Person
    label = "Has an exemption for Medicaid work requirements"
    definition_period = MONTH
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters):
        is_totally_disabled_veteran = person("is_totally_disabled_veteran", period)
        is_medically_frail = person("is_medically_frail", period)

        return (
            is_totally_disabled_veteran or
            is_medically_frail
        )
