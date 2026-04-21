from policyengine_us.model_api import *


class pa_uc_weeks_unemployed(Variable):
    value_type = int
    entity = Person
    label = "Pennsylvania unemployment compensation weeks unemployed"
    unit = "week"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=133",
    )
    defined_for = StateCode.PA
