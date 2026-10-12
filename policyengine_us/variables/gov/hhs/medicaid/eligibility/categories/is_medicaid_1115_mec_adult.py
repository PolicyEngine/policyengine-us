from policyengine_us.model_api import *


class is_medicaid_1115_mec_adult(Variable):
    value_type = bool
    entity = Person
    label = "Eligible under a Medicaid section 1115 MEC adult demonstration"
    definition_period = YEAR
    reference = (
        "https://www.congress.gov/bill/119th-congress/house-bill/1/text",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib12082025.pdf",
    )
