from policyengine_us.model_api import *


class is_medicaid_work_requirement_applicable_adult(Variable):
    value_type = bool
    entity = Person
    label = "Adult subject to Medicaid work requirements"
    definition_period = YEAR
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib12082025.pdf",
    )

    def formula(person, period, parameters):
        category = person("medicaid_category", period)
        return (category == category.possible_values.ADULT) | (
            category == category.possible_values.SECTION_1115_MEC_ADULT
        )
